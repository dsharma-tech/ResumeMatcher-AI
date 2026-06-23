# Semantic Resume Matcher

**Semantic Resume Matcher** is a production-quality, python-based web application that compares resumes against job descriptions. It computes detailed, explainable match scores using local semantic similarity, technical keyword coverage, section completeness audits, and experience/education compatibility checks.

All processing, scoring, NLP calculations, and Jinja2 rendering are done locally on the server without any external generative AI or API keys.

---

## 1. Quick Start Guide

### Prerequisites
* Python 3.12+

### Installation
From the project root directory, install the required dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application
Start the FastAPI server using Uvicorn:
```bash
uvicorn app.main:app --reload --port 8002
```

### Sample Usage
1. Open your browser and navigate to: [http://127.0.0.1:8002](http://127.0.0.1:8002)
2. Upload a candidate's resume (supported formats: `.pdf` and `.docx`).
3. Paste the target Job Description in the textarea.
4. Click **Analyze Fit** to process.
5. Review the comprehensive match analysis dashboard on the results page.
6. Click **Download PDF Report** to export a clean compiled PDF report.

---

## 2. Key Features & Internal Mechanisms

### Feature 1: Keyword Coverage Analysis
* Technical skills and concepts are matched against a standardized database (`app/services/skills_db.py`).
* Determines **Matched Keywords**, **Missing Keywords**, and **Additional Candidate Skills** (skills in the resume not requested in the JD).
* Keyword coverage is computed as:
  $$\text{Keyword Coverage Percentage} = \left( \frac{\text{len(matched\_keywords)}}{\text{len(jd\_keywords)}} \right) \times 100$$
  *(Falls back to semantic similarity score if the JD specifies no keywords).*

### Feature 2: Resume Section Analysis
* Audits the resume text for headings associated with 6 critical section types:
  1. **Education** (e.g., studies, academic background, degree)
  2. **Skills** (e.g., technical skills, technologies, expertise)
  3. **Experience** (e.g., work experience, employment history)
  4. **Projects** (e.g., personal projects, academic projects)
  5. **Certifications** (e.g., licenses, certificates)
  6. **Achievements** (e.g., awards, honors, accomplishments)
* Calculates completeness score:
  $$\text{Section Score} = \left( \frac{\text{sections\_found}}{6} \right) \times 100$$

### Feature 3: Experience Duration Calculator
* Uses regular expressions to extract experience ranges, supporting formats like:
  * `May 2025 - Feb 2026`
  * `Jan 2024 – Present` (calculates relative to the current date)
  * `June 2023 to December 2023`
* Differentiates professional experience from internship/trainee tenure using keyword checks in a 100-character context window.
* Matches total tenure against job requirements, reporting compatibility status ("Compatible" or "Not Compatible").

### Feature 4: Resume Strength Meter
* Assesses candidate profile quality based on overall structure and content:
  * Keyword Coverage: 40%
  * Semantic Similarity: 30%
  * Experience Match: 20%
  * Resume Completeness (Section Score): 10%

### Feature 5: Suggestions Engine
* Rule-based engine that returns targeted suggestions (without external LLMs):
  * Missing SQL: *"Add SQL related projects"*
  * Missing Excel/Power BI: *"Mention dashboard creation experience"*
  * Missing Certifications: *"Include Certifications section"*
  * Missing Achievements: *"Include Achievements section"*
  * Low Semantic Similarity: *"Align resume vocabulary with the job description terminology"*

### Feature 6: PDF Report Exporter
* Compiles report metrics, compatibility checks, and lists of matched/missing keywords into a downloadable PDF report built dynamically on the backend using `reportlab`.

### Feature 7: Multiple Resumes Comparison
* Supports comparing and ranking up to 5 resumes against a single Job Description simultaneously (via POST `/api/analyze-multiple`).

---

## 3. Technology Stack & Directory Structure

### Web Server & API Framework
* **FastAPI**: Serves REST APIs and handles template rendering.
* **Jinja2**: Standard python templates for server-side page serving:
  * `app/templates/home.html` (form submissions & uploads)
  * `app/templates/results.html` (interactive dashboards)
* **StaticFiles**: Serves CSS layout stylesheets dynamically from `app/static`.

### NLP & Document Processing
* **SentenceTransformers**: Downloads and runs the `all-MiniLM-L6-v2` model locally to calculate semantic sentence embeddings.
* **Scikit-Learn**: Computes Cosine Similarity between text vectors.
* **PyPDF & Python-Docx**: Document readers to extract clean plain text.
* **ReportLab**: Creates downloadable PDF reports locally.

### Directory Layout
```
SemanticResumeMatcher/
├── README.md
├── app/
│   ├── api/
│   │   └── endpoints.py
│   ├── main.py
│   ├── services/
│   │   ├── matcher_service.py
│   │   ├── parser_service.py
│   │   ├── pdf_service.py
│   │   └── skills_db.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── home.html
│       └── results.html
├── requirements.txt
├── samples/
│   ├── resume.docx
│   └── sample_jd.txt
└── .gitignore
```

---

## 4. Scoring Formulas

### Resume Match Score (Overall Fit)
* Technical Skills Match (Keyword Coverage): 40%
* Semantic Similarity: 30%
* Experience Match: 20%
* Education Match: 10%
$$\text{Match Score} = (\text{skills\_score} \times 0.40) + (\text{semantic\_score} \times 0.30) + (\text{experience\_score} \times 0.20) + (\text{education\_score} \times 0.10)$$

### Resume Strength Score (Profile Quality)
* Keyword Coverage: 40%
* Semantic Similarity: 30%
* Experience Match: 20%
* Resume Completeness (Section Score): 10%
$$\text{Resume Strength} = (\text{keyword\_coverage} \times 0.40) + (\text{semantic\_score} \times 0.30) + (\text{experience\_score} \times 0.20) + (\text{section\_score} \times 0.10)$$
