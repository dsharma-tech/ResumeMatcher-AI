# Resume-Job Description Matcher AI

A production-quality web application that uses Google Gemini AI to analyze resumes against job descriptions, providing a fit score, verdict, and actionable suggestions.

## Features
- **PDF & DOCX Support**: Upload resumes in standard formats.
- **AI-Powered Analysis**: Uses Google Gemini Pro/Flash for deep semantic understanding.
- **Weighted Scoring**:
    - Skills Match: 50%
    - Experience: 25%
    - Role Alignment: 15%
    - Education: 10%
- **Modern UI**: Built with React, Tailwind CSS, and Framer Motion.
- **Dark Mode**: Fully supported premium dark theme.

## Tech Stack
- **Backend**: Python, FastAPI, Google Generative AI
- **Frontend**: React (Vite), Tailwind CSS, Lucide Icons, Axios

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- Google Cloud API Key (Gemini)

### 1. Backend Setup
Navigate to the `backend` directory:
```bash
cd backend
```

Create a virtual environment and activate it:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

**Configure API Key**:
Create a `.env` file in the `backend` folder and add your Gemini API Key:
```env
GEMINI_API_KEY=your_api_key_here
```

Run the server:
```bash
uvicorn main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`.

### 2. Frontend Setup
Navigate to the `frontend` directory:
```bash
cd frontend
```

Install dependencies:
```bash
npm install
```

Run the development server:
```bash
npm run dev
```
The app will be available at `http://localhost:5173`.

## How It Works
1. Upload a Resume (PDF/DOCX).
2. Paste the Job Description.
3. Click "Analyze Fit".
4. The backend extracts text, sends it to Gemini for structured analysis, computes a deterministic weighted score, and returns the result to the UI.

## Disclaimer
This tool provides AI-based analysis and should not be used as the sole hiring decision criteria.
