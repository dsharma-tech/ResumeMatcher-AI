import os
import re
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import google.generativeai as genai
from .skills_db import ALL_SKILLS

# Global model instance (lazy loaded)
model = None

def load_model():
    global model
    if model is None:
        try:
            model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading model: {e}")
            raise RuntimeError(f"Failed to load AI model: {e}")

def get_embedding(text: str) -> np.ndarray:
    global model
    if model is None:
        load_model()
    return model.encode(text)

def calculate_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    v1 = vec1.reshape(1, -1)
    v2 = vec2.reshape(1, -1)
    return float(cosine_similarity(v1, v2)[0][0])

def extract_skills(text: str) -> List[str]:
    text_lower = text.lower()
    found_skills = []
    for skill in ALL_SKILLS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)
    return sorted(list(set(found_skills)))

def extract_years_experience(text: str, is_jd: bool = False) -> (int, int):
    """
    Returns (min_years, max_years) or a single value if only one detected.
    For JD: returns (min, max) required.
    For Resume: returns (detected_years, has_internships).
    """
    text_lower = text.lower()
    
    # Check for "fresher", "entry level", "graduate"
    is_fresher = any(x in text_lower for x in ["fresher", "entry level", "grad school", "junior role"])
    has_internships = "internship" in text_lower or "intern" in text_lower
    
    matches = re.findall(r'(\d+)(?:\s*-\s*(\d+))?\+?\s*years?', text_lower)
    
    years_found = []
    for m in matches:
        if m[0]: years_found.append(int(m[0]))
        if m[1]: years_found.append(int(m[1]))
    
    if is_jd:
        if is_fresher and not years_found:
            return 0, 1
        return (min(years_found), max(years_found)) if years_found else (0, 0)
    else:
        # Resume detection: use max found, but if matches internship, treat specially
        detected = max(years_found) if years_found else 0
        if detected == 0 and (has_internships or is_fresher):
            detected = 0.5 # Fractional for internship/fresher
        return detected, has_internships

def extract_education_level(text: str) -> int:
    text_lower = text.lower()
    if 'phd' in text_lower or 'doctorate' in text_lower: return 100
    if any(x in text_lower for x in ['master', 'm.s.', 'ms ', 'mba']): return 90
    if any(x in text_lower for x in ['bachelor', 'b.s.', 'bs ', 'b.tech', 'be ', 'bca']): return 80
    if any(x in text_lower for x in ['associate', 'diploma']): return 60
    return 40

async def analyze_with_gemini(resume_text: str, job_description: str) -> Dict[str, Any]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Act as a professional ATS (Applicant Tracking System) and Career Coach. 
        Perform a deep analysis of this Resume against the Job Description.
        
        RESUME:
        {resume_text}
        
        JOB DESCRIPTION:
        {job_description}
        
        Provide a DETAILED JSON response with exactly these keys:
        - "score": (int 0-100)
        - "verdict": "Excellent Match" | "Good Match" | "Partial Match" | "Needs Improvement"
        - "summary": (Explain WHY the score was given, mentioning specific strengths and weaknesses.)
        - "matched_skills": [list of skills found in both]
        - "missing_skills": [list of CRITICAL keywords/skills present in JD but missing in Resume]
        - "suggestions": {{
            "Experience Match": [detailed points about tenure, industry fit, level],
            "Skills Gap": [explicit list of what to add to the skills section],
            "Specific Keywords to Add": [exact phrases from JD to include],
            "Section-wise Improvements": [Missing sections like 'Certifications', 'Portfolio', or specific bullet points to rewrite]
          }}
        
        Rule: If JD mentions 0-1 years and candidate has any internship or projects, grant full score for experience. 
        Focus on specific actionable items. For example, if 'Excel' is missing, say 'Add Microsoft Excel (Pivot Tables)'.
        """
        
        response = model.generate_content(prompt)
        content = response.text
        if "```json" in content:
            content = content.split("```json")[-1].split("```")[0]
        
        import json
        return json.loads(content)
    except Exception as e:
        print(f"Gemini error: {e}")
        return None

async def analyze_resume_with_job_description(resume_text: str, job_description: str) -> Dict[str, Any]:
    # 0. Try Gemini first
    gemini_result = await analyze_with_gemini(resume_text, job_description)
    if gemini_result:
        # Format suggestions as section-specific strings for the frontend
        flat_suggestions = []
        for section, items in gemini_result.get("suggestions", {}).items():
            if items:
                # Add a section header
                flat_suggestions.append(f"### {section}")
                for item in items:
                    flat_suggestions.append(item)
        gemini_result["suggestions"] = flat_suggestions
        return gemini_result

    # FALLBACK: Optimized Local Logic
    if model is None: load_model()

    resume_emb = get_embedding(resume_text[:2500])
    jd_emb = get_embedding(job_description[:2500])
    semantic_score = calculate_cosine_similarity(resume_emb, jd_emb) * 100 

    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(job_description))
    matched_skills = list(resume_skills.intersection(jd_skills))
    missing_skills = list(jd_skills - resume_skills)

    # 3. Skills Score (50%)
    skills_score = (len(matched_skills) / len(jd_skills)) * 100 if jd_skills else semantic_score

    # 4. Experience Score (25%)
    res_exp, has_intern = extract_years_experience(resume_text)
    jd_min, jd_max = extract_years_experience(job_description, is_jd=True)
    
    experience_score = 100
    if jd_min > 0:
        if res_exp >= jd_min:
            experience_score = 100
        else:
            experience_score = (res_exp / jd_min) * 100
            if has_intern and jd_min <= 1:
                experience_score = max(experience_score, 90)
    else:
        experience_score = 100

    # 5. Education Score (10%)
    res_edu = extract_education_level(resume_text)
    jd_edu = extract_education_level(job_description)
    education_score = 100 if res_edu >= jd_edu else (res_edu / jd_edu) * 100

    # 7. Final Score
    final_score = int((skills_score * 0.50) + (experience_score * 0.25) + (semantic_score * 0.15) + (education_score * 0.10))
    final_score = min(100, max(0, final_score))

    # 8. Verdict
    if final_score >= 85: verdict = "Excellent Match"
    elif final_score >= 70: verdict = "Good Match"
    elif final_score >= 50: verdict = "Partial Match"
    else: verdict = "Needs Improvement"

    # 9. Structured Suggestions
    suggestions = []
    
    # Section: Detailed Skills Gap
    if missing_skills:
        suggestions.append("### Skills Gap Analysis")
        suggestions.append(f"CRITICAL MISSING: {', '.join(missing_skills[:5])}")
        suggestions.append("ACTION: Add a 'Key Skills' section or integrate these specific terms into your experience bullet points.")
    
    # Section: Experience & Impact
    suggestions.append("### Experience & Role Fit")
    if experience_score < 100:
        if has_intern:
            suggestions.append("Your internship provides a strong foundation. Emphasize quantifiable achievements (e.g., 'Improves efficiency by X%') to bridge the experience gap.")
        else:
            suggestions.append(f"The JD asks for {jd_min} years. If you have freelance or project work, list it under 'Professional Experience' to show tenure.")
    else:
        suggestions.append("Your years of experience align well with the job requirements. Keep it as is.")

    # Section: Content & Keywords
    if semantic_score < 50:
        suggestions.append("### Resume Optimization")
        suggestions.append("LACK OF CONTEXT: Your resume mentions skills but doesn't map them to the job's core responsibilities.")
        suggestions.append("TIP: Mirror the language used in the JD. If they use 'Collaboration', don't just say 'Teamwork'.")
    
    if not suggestions:
        suggestions.append("### Final Polish")
        suggestions.append("Your resume content is highly aligned. Ensure your formatting is consistent and you use active verbs.")

    return {
        "score": final_score,
        "verdict": verdict,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "summary": f"Your profile matches {final_score}% of the requirements. " + 
                  (f"You have {len(matched_skills)} core matches, but are missing {len(missing_skills)} key elements mentioned in the JD." if missing_skills else "You have a solid match for most requirements."),
        "suggestions": suggestions
    }
