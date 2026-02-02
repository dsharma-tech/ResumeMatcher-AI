# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()

# app = FastAPI(
#     title="Resume-JD Matcher API",
#     description="API for parsing resumes and matching them with job descriptions using AI.",
#     version="1.0.0"
# )

# # CORS Middleware to allow requests from frontend
# origins = [
#     "http://localhost:5173",  # Vite default
#     "http://localhost:3000",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# from api.endpoints import router as api_router
# app.include_router(api_router, prefix="/api")

# @app.get("/")
# async def root():
#     return {"message": "Resume-JD Matcher API is running"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables (works locally; Render uses its own env vars)
load_dotenv()

app = FastAPI(
    title="Resume-JD Matcher API",
    description="API for parsing resumes and matching them with job descriptions using AI.",
    version="1.0.0"
)

# ✅ CORS configuration (LOCAL + VERCEL)
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://resume-matcher-ai-jade.vercel.app",  # 👈 REQUIRED
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
from api.endpoints import router as api_router
app.include_router(api_router, prefix="/api")

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Resume-JD Matcher API is running"}

# Health check (IMPORTANT for Render)
@app.get("/health")
async def health():
    return {"status": "ok"}
