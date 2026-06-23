from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import os

from app.api.endpoints import router as api_router
from app.services.parser_service import extract_text
from app.services.matcher_service import analyze_resume_with_job_description

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Semantic Resume Matcher API",
    description="API for parsing resumes and matching them with job descriptions using semantic similarity and rule-based scoring.",
    version="1.0.0"
)

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://resume-matcher-ai-jade.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files and Jinja2 Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Register API Router
app.include_router(api_router, prefix="/api")

# HEALTH CHECK
@app.get("/health")
async def health():
    return {"status": "ok"}

# JINJA2 PAGE RENDERING ENDPOINTS

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request, "home.html", {"request": request})


@app.post("/results", response_class=HTMLResponse)
async def results_page(
    request: Request,
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    try:
        if not resume.filename:
            return templates.TemplateResponse(request, "home.html", {"request": request, "error": "No file uploaded"})
        
        file_content = await resume.read()
        resume_text = extract_text(resume.filename, file_content)
        analysis_result = await analyze_resume_with_job_description(resume_text, job_description)
        
        return templates.TemplateResponse(request, "results.html", {"request": request, "result": analysis_result})
    except Exception as e:
        return templates.TemplateResponse(request, "home.html", {"request": request, "error": f"Error: {str(e)}"})
