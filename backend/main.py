from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import urlparse

from backend.github_analyzer import analyze_github_repository


# Create FastAPI application
app = FastAPI(
    title="CodeAtlas API",
    description="AI-powered codebase intelligence platform",
    version="1.0.0"
)


# Allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Request model
class RepositoryRequest(BaseModel):
    repo_url: str


# Home route
@app.get("/")
def home():
    return {
        "message": "Welcome to CodeAtlas!",
        "status": "Backend is running successfully"
    }


# Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# GitHub repository analysis
@app.post("/analyze")
def analyze_repository(request: RepositoryRequest):

    repo_url = request.repo_url.strip()

    # Validate GitHub URL
    parsed_url = urlparse(repo_url)

    if (
        parsed_url.scheme not in ["http", "https"]
        or parsed_url.netloc.lower() not in ["github.com", "www.github.com"]
    ):
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid GitHub repository URL"
        )

    # Call GitHub analyzer
    result = analyze_github_repository(repo_url)

    # Handle analyzer errors
    if "error" in result:
        status_code = result.get("status_code", 502)

        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    return {
        "message": "Repository analyzed successfully",
        "analysis": result
    }