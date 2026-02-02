from fastapi import APIRouter, UploadFile, Form, HTTPException
from services.parser_service import extract_text
from services.ai_service import analyze_resume_with_job_description

router = APIRouter()

@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile,
    job_description: str = Form(...)
):
    if not resume.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    try:
        # Read file content
        file_content = await resume.read()
        
        # 1. Parse Resume Text
        resume_text = extract_text(resume.filename, file_content)
        
        # 2. AI Analysis
        analysis_result = await analyze_resume_with_job_description(resume_text, job_description)
        
        return analysis_result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
