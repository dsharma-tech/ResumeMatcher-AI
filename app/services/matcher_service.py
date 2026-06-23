import os
import re
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
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

def parse_experience_durations(text: str) -> (int, int, bool):
    """
    Parses resume text for experience date ranges and calculates total duration and internship duration.
    Returns (total_months, intern_months, has_intern).
    """
    months_map = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    pattern = re.compile(
        r'\b(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+(\d{4})\s*(?:-|–|—|to)\s*(present|current|jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)(?:\s+(\d{4}))?\b',
        re.IGNORECASE
    )
    
    total_months = 0
    intern_months = 0
    has_intern = False
    
    if re.search(r'\bintern(ship)?\b', text.lower()) or 'intern' in text.lower():
        has_intern = True
        
    for match in pattern.finditer(text):
        start_m_str = match.group(1).lower()
        start_y_str = match.group(2)
        end_m_str = match.group(3).lower()
        end_y_str = match.group(4)
        
        start_month = months_map.get(start_m_str, 1)
        start_year = int(start_y_str)
        
        if end_m_str in ['present', 'current']:
            end_month = 6
            end_year = 2026
        else:
            end_month = months_map.get(end_m_str, 1)
            end_year = int(end_y_str) if end_y_str else start_year
            
        months = (end_year - start_year) * 12 + (end_month - start_month) + 1
        if months < 0:
            months = 0
            
        match_start = match.start()
        match_end = match.end()
        window_start = max(0, match_start - 100)
        window_end = min(len(text), match_end + 100)
        context = text[window_start:window_end].lower()
        
        is_intern_job = 'intern' in context or 'internship' in context or 'trainee' in context
        
        if is_intern_job:
            intern_months += months
        else:
            total_months += months
            
    if total_months == 0 and intern_months == 0:
        year_matches = re.findall(r'(\d+)\+?\s*years?\b', text.lower())
        if year_matches:
            years_found = max(int(y) for y in year_matches)
            total_months = years_found * 12
            
    return total_months, intern_months, has_intern


def analyze_resume_sections(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    
    sections = {
        "Education": [r"\beducation\b", r"\bacademc\b", r"\bacademic\b", r"\bstudies\b", r"\bdegree\b"],
        "Skills": [r"\bskills\b", r"\btechnical skills\b", r"\bkey skills\b", r"\btechnologies\b", r"\bexpertise\b"],
        "Experience": [r"\bexperience\b", r"\bwork experience\b", r"\bemployment\b", r"\bprofessional experience\b", r"\bwork history\b"],
        "Projects": [r"\bprojects\b", r"\bacademc projects\b", r"\bkey projects\b", r"\bpersonal projects\b"],
        "Certifications": [r"\bcertifications\b", r"\bcertifications & licenses\b", r"\blicenses\b", r"\bcertificates\b"],
        "Achievements": [r"\bachievements\b", r"\bawards\b", r"\baccomplishments\b", r"\bhonors\b"]
    }
    
    sections_found = []
    missing_sections = []
    
    for section_name, patterns in sections.items():
        found = False
        for pattern in patterns:
            if re.search(pattern, text_lower):
                found = True
                break
        if found:
            sections_found.append(section_name)
        else:
            missing_sections.append(section_name)
            
    section_score = int((len(sections_found) / len(sections)) * 100)
    
    return {
        "sections_found": sections_found,
        "missing_sections": missing_sections,
        "section_score": section_score
    }


async def analyze_resume_with_job_description(resume_text: str, job_description: str) -> Dict[str, Any]:
    if model is None: load_model()

    # 1. Semantic Similarity
    resume_emb = get_embedding(resume_text[:2500])
    jd_emb = get_embedding(job_description[:2500])
    semantic_score = calculate_cosine_similarity(resume_emb, jd_emb) * 100 
    semantic_score = min(100.0, max(0.0, semantic_score))

    # 2. Skills / Keywords extraction
    resume_skills = set(extract_skills(resume_text))
    jd_skills = set(extract_skills(job_description))
    matched_skills = sorted(list(resume_skills.intersection(jd_skills)))
    missing_skills = sorted(list(jd_skills - resume_skills))

    # Keyword Coverage
    keyword_coverage_percentage = int((len(matched_skills) / len(jd_skills)) * 100) if jd_skills else int(semantic_score)

    # 3. Section Analysis
    section_analysis = analyze_resume_sections(resume_text)
    sections_found = section_analysis["sections_found"]
    missing_sections = section_analysis["missing_sections"]
    section_score = section_analysis["section_score"]

    # 4. Experience Calculation
    total_months, intern_months, has_intern = parse_experience_durations(resume_text)
    jd_min, jd_max = extract_years_experience(job_description, is_jd=True)
    
    experience_score = 100.0
    if jd_min > 0:
        candidate_years = (total_months + intern_months) / 12.0
        if candidate_years >= jd_min:
            experience_score = 100.0
        else:
            experience_score = (candidate_years / jd_min) * 100.0
            if (has_intern or intern_months > 0) and jd_min <= 1:
                experience_score = max(experience_score, 90.0)
    else:
        experience_score = 100.0

    # Display internship or total duration
    display_internship = "0 months"
    if intern_months > 0:
        display_internship = f"{intern_months} months"
    elif total_months > 0:
        display_internship = f"{total_months} months"

    jd_requirement_str = "0-1 years"
    if jd_min > 0:
        if jd_max > jd_min:
            jd_requirement_str = f"{jd_min}-{jd_max} years"
        else:
            jd_requirement_str = f"{jd_min}+ years"

    experience_compatibility = "Compatible" if experience_score >= 80 else "Not Compatible"

    # 5. Education Compatibility
    res_edu = extract_education_level(resume_text)
    jd_edu = extract_education_level(job_description)
    education_score = 100.0 if res_edu >= jd_edu else (res_edu / jd_edu) * 100.0
    education_compatibility = "Compatible" if education_score >= 80 else "Not Compatible"

    # 6. Overall Resume Strength Score
    # Components: Keyword Coverage: 40, Semantic Similarity: 30, Experience Match: 20, Resume Completeness: 10
    resume_strength = (keyword_coverage_percentage * 0.40) + (semantic_score * 0.30) + (experience_score * 0.20) + (section_score * 0.10)
    resume_strength = int(min(100, max(0, resume_strength)))

    # 7. Resume Match Score
    # Components: Technical Skills Match (Keyword Coverage): 40%, Semantic Similarity: 30%, Experience Match: 20%, Education Match: 10%
    final_score = (keyword_coverage_percentage * 0.40) + (semantic_score * 0.30) + (experience_score * 0.20) + (education_score * 0.10)
    final_score = int(min(100, max(0, final_score)))

    # Verdict
    if final_score >= 85: verdict = "Excellent Match"
    elif final_score >= 70: verdict = "Good Match"
    elif final_score >= 50: verdict = "Partial Match"
    else: verdict = "Needs Improvement"

    # 8. Deterministic Recommendations Engine
    recommendations = []
    
    # Keyword coverage suggestions
    if any(k.lower() == "sql" for k in missing_skills):
        recommendations.append("Add SQL related projects")
    dashboard_tools = ["power bi", "tableau", "excel"]
    if any(k.lower() in dashboard_tools for k in missing_skills):
        recommendations.append("Mention dashboard creation experience")
        
    if "Certifications" in missing_sections:
        recommendations.append("Include Certifications section")
        
    if intern_months > 0 or has_intern:
        recommendations.append("Emphasize internship achievements")

    # Add other missing keywords suggestions
    other_missing = [k for k in missing_skills if k.lower() not in ["sql", "power bi", "tableau", "excel"]]
    for k in other_missing[:2]:
        skill_cap = k.title() if len(k) > 3 or k.lower() in ["aws", "gcp", "git"] else k
        recommendations.append(f"Add {skill_cap}-related projects or experience")
        
    if "Achievements" in missing_sections:
        recommendations.append("Include Achievements section")
        
    if (total_months + intern_months) < jd_min * 12 and intern_months == 0:
        recommendations.append("Highlight academic projects and coursework to offset short professional experience")
        
    if semantic_score < 70:
        recommendations.append("Align resume vocabulary with the job description terminology")

    if not recommendations:
        recommendations.append("Ensure your resume contains achievements with quantifiable metrics")

    return {
        "score": final_score,
        "semantic_score": int(semantic_score),
        "skills_score": keyword_coverage_percentage,  # Technical Skills Match
        "keyword_coverage_percentage": keyword_coverage_percentage,
        "resume_strength": resume_strength,
        "resume_strength_score": resume_strength,  # spec requirement
        
        "experience_duration": f"{total_months + intern_months} months" if (total_months + intern_months) > 0 else "0 months",
        "experience_match": experience_compatibility,
        "experience_score": int(experience_score),
        
        "education_match": education_compatibility,
        "education_score": int(education_score),
        
        "internship_duration": display_internship,
        "jd_requirement": jd_requirement_str,
        "experience_compatibility": experience_compatibility,
        "education_compatibility": education_compatibility,
        
        "sections_found": sections_found,
        "missing_sections": missing_sections,
        "section_score": section_score,
        
        "verdict": verdict,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "additional_resume_skills": sorted(list(resume_skills - jd_skills)), # Skill Extraction addition
        
        "summary": f"Your profile matches {final_score}% of the requirements. " + 
                  (f"You have {len(matched_skills)} core matches, but are missing {len(missing_skills)} key elements mentioned in the JD." if missing_skills else "You have a solid match for most requirements."),
        "recommendations": recommendations,
        "suggestions": recommendations  # keep for backward compatibility
    }
