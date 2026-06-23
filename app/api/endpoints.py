from fastapi import APIRouter, UploadFile, Form, HTTPException, File
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any
from app.services.parser_service import extract_text
from app.services.matcher_service import analyze_resume_with_job_description
from app.services.pdf_service import generate_pdf_report

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


@router.post("/analyze-multiple")
async def analyze_multiple(
    resumes: List[UploadFile] = File(...),
    job_description: str = Form(...)
):
    if not resumes:
        raise HTTPException(status_code=400, detail="No files uploaded")
    if len(resumes) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 resumes allowed.")

    try:
        results = []
        for file in resumes:
            if not file.filename:
                continue
            content = await file.read()
            resume_text = extract_text(file.filename, content)
            analysis = await analyze_resume_with_job_description(resume_text, job_description)
            results.append({
                "filename": file.filename,
                "score": analysis["score"],
                "analysis": analysis
            })
        
        # Rank resumes descending by score
        results.sort(key=lambda x: x["score"], reverse=True)
        return {"results": results}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/export-pdf")
async def export_pdf(data: Dict[str, Any]):
    try:
        pdf_buf = generate_pdf_report(data)
        return StreamingResponse(
            pdf_buf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=semantic_resume_match_report.pdf",
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")
