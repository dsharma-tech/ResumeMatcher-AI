---
title: Semantic Resume Matcher
emoji: 📄
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# ResumeMatcher-AI

AI-Powered Resume & Job Description Matching

---

## About the Project
**ResumeMatcher-AI** (Semantic Resume Matcher) is a local, production-quality web application that analyzes how well a candidate's resume fits a specific job description. 

It provides an explainable, multi-component match breakdown using natural language processing (NLP) and rule-based compatibility scoring. All processing is run locally on the server (no third-party LLMs or API keys are required).

### Key Features
1. **Keyword Coverage**: Maps technical skills in the resume against job description requirements using a local skill taxonomy.
2. **Semantic Similarity**: Computes cosine similarity between the resume text and the job description using the `paraphrase-MiniLM-L3-v2` SentenceTransformer model.
3. **Section Completeness Audit**: Checks for the presence of 6 key resume sections (Education, Skills, Experience, Projects, Certifications, achievements) and calculates a completeness score.
4. **Experience Compatibility**: Parses complex experience durations (e.g., date ranges, current/present roles) and isolates internship contexts to determine if the candidate meets job tenure requirements.
5. **PDF Report Exports**: Compiles the breakdown metrics, skill lists, and recommendations list into a printable PDF report.

---

## Prerequisites

* Python 3.12+

## Installation

Install the required dependencies from the root directory:
```bash
pip install -r requirements.txt
```

## Running Application

Start the FastAPI application on port `8002`:
```bash
uvicorn app.main:app --reload --port 8002
```

## Sample Usage

1. Open browser at [http://127.0.0.1:8002](http://127.0.0.1:8002)
2. Upload a Resume in `.pdf` or `.docx` format
3. Paste the target Job Description in the text area
4. Click **Analyze Fit**
5. View the Match and Strength Scores, Keyword lists, and tenure compatibility
6. Click **Download PDF Report** to export the analysis as a PDF file
