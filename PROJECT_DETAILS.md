# Project Documentation: ResumeMatcher AI

## 1. Project Overview
**ResumeMatcher AI** is an advanced, AI-powered Applicant Tracking System (ATS) assistant designed to bridge the gap between job seekers and hiring requirements. It allows users to upload their resumes (PDF/DOCX) and paste a Job Description (JD) to receive an instant, detailed analysis of how well they fit the role.

## 2. Problem Solved
Traditional ATS systems often reject qualified candidates because their resumes lack specific keywords or don't follow the exact formatting expected. This leads to:
- **Candidate Frustration**: Not knowing why they are being rejected.
- **Efficiency Gap**: Candidates spending hours manually tailoring resumes for every job.
- **Information Overload**: Recruitment teams missing great talent due to poor keyword matching.

ResumeMatcher AI solves this by providing **transparent, actionable feedback**, showing exactly what is missing and how to improve.

## 3. Key Features
- **Multi-Format Support**: Seamless parsing of `.pdf` and `.docx` files.
- **Hybrid AI Scoring**: Combines local NLP (Sentence Transformers) with advanced LLM analysis (Google Gemini).
- **Weighted Match Score**: A deterministic score based on Skills (50%), Experience (25%), Role Alignment (15%), and Education (10%).
- **Section-wise Improvements**: Categorized suggestions for "Skills Gap", "Experience Match", and "Keyword Optimization".
- **Real-time Feedback**: Detailed Executive Summary explaining the strengths and weaknesses of the candidate's profile.
- **Premium UI/UX**: A responsive, modern dashboard built with dark mode support and smooth animations.

## 4. Technology Stack
### Frontend
- **React 19 (Vite)**: Modern, blazing-fast web framework.
- **Tailwind CSS**: For sleek, responsive styling and glassmorphism effects.
- **Framer Motion**: For smooth transitions and interactive UI elements.
- **Lucide Icons**: Professional vector iconography.
- **Axios**: For robust API communication.

### Backend
- **FastAPI (Python)**: High-performance asynchronous API framework.
- **Uvicorn**: Lightweight ASGI server.
- **Pypdf & Python-Docx**: Libraries for deep text extraction from document binaries.
- **Sentence-Transformers**: Local NLP model (`all-MiniLM-L6-v2`) for semantic similarity calculations.
- **Scikit-Learn**: Used for Cosine Similarity between Resume and JD embeddings.

## 5. Hybrid AI Architecture
The system employs a smart hybrid approach to balance performance, cost, and depth of analysis:

- **Local Model (Sentence Transformers):** By default, the app uses the `all-MiniLM-L6-v2` model locally. This provides high-speed semantic matching and is 100% free and private. It is responsible for calculating the baseline match score and finding overlapping technical skills.
- **Enhanced API (Google Gemini):** When a `GEMINI_API_KEY` is provided, the app unlocks "Deep Audit" mode. It uses the Gemini 1.5 Flash API to perform human-like reasoning, provide section-wise career advice, and catch subtle context gaps that a local model might miss.
- **Fail-Safe Mechanism:** The system is designed to automatically fall back to the local model if the API key is missing or invalid, ensuring the app remains functional at all times.

## 6. How It Works (Internal Mechanism)

### Step 1: Document Parsing
When a user uploads a file, the `parser_service` identifies the file extension:
- **PDFs**: Scanned using `pypdf` to extract text from every page.
- **DOCX**: Scanned using `python-docx` to extract text from paragraphs.
This text is then cleaned and sent to the AI engine.

### Step 2: Semantic Analysis & Embedding
The backend uses a local embedding model to convert the entire Resume and JD into high-dimensional vectors. It then calculates the **Cosine Similarity** between these vectors. This ensures the tool understands *context* (e.g., matching "Software Engineer" with "Programmer") rather than just exact keywords.

### Step 3: Skill Matching Logic
The system uses a large, categorized database (`skills_db.py`) covering:
- **Programming Languages** (Python, Java, etc.)
- **Frameworks** (React, Spring Boot, etc.)
- **Office Tools** (Excel, PowerPoint, etc.)
- **Soft Skills** (Communication, Teamwork, etc.)
It performs a set-intersection match to find exactly what terms appear in both the Resume and the JD.

### Step 4: Intelligent Experience Detection
The model uses refined Regex pattern matching to detect years of experience and internships:
- It handles **JD Ranges** (e.g., "0-1 year") correctly, treating them as entry-level.
- It identifies keywords like "Intern" or "Trainee" and gives credit for internship experience, even if the candidate is a fresh graduate.

### Step 5: Gemini AI Reasoning (Optional/Enhanced)
If a Gemini API Key is provided, the system sends the Resume and JD to **Gemini 1.5 Flash**. The AI performs a "Deep Audit," generating section-by-section suggestions and identifying critical phrased-based missing elements that local regex might miss.

### Step 6: Final Scoring & Dashboard
All sub-scores are weighted into a final percentage. The result is streamed to the React dashboard, where it's displayed in a clean, categorized result panel.

## 7. Deployment Guide
The project is containerized using Docker for seamless deployment.

### Local Deployment
```bash
docker-compose up --build
```

### Production Deployment
1. **Frontend**: The React app is built and served via Nginx. Update `VITE_API_URL` in `docker-compose.yml` to your production domain.
2. **Backend**: The FastAPI server is production-ready. 
3. **Environment**: Ensure your `GEMINI_API_KEY` is set in the `.env` file for enhanced analysis.

## 8. Project Workflow Summary
1. **User Action**: Uploads Resume + Job Description.
2. **Backend**: Extracts text -> Generates Embeddings -> Runs Comparison.
3. **AI Engine**: Calculates weights + Generates granular suggestions.
4. **UI**: Displays Score, Verdict, Summary, and categorized Improvement Suggestions.
do