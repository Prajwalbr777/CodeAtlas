from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import urlparse

from backend.github_analyzer import analyze_github_repository

from backend.github_source_fetcher import fetch_source_files

from backend.code_quality_scanner import analyze_source_files


# Create FastAPI application
app = FastAPI(
    title="CodeAtlas API",
    description="Codebase intelligence and code quality analysis platform",
    version="1.1.0"
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
        or parsed_url.netloc.lower() not in [
            "github.com",
            "www.github.com"
        ]
    ):
        raise HTTPException(
            status_code=400,
            detail="Please provide a valid GitHub repository URL"
        )

    # Step 1: Analyze repository structure and languages
    result = analyze_github_repository(repo_url)

    if "error" in result:
        status_code = result.get("status_code", 502)

        raise HTTPException(
            status_code=status_code,
            detail=result["error"]
        )

    # Step 2: Fetch actual source code from GitHub
    source_result = fetch_source_files(
        result["owner"],
        result["repository"],
        result["files"]
    )

    if "error" in source_result:
        raise HTTPException(
            status_code=502,
            detail=source_result["error"]
        )

    source_files = source_result["files"]

    # Step 3: Scan source code for potential issues
    quality_result = analyze_source_files(source_files)

    # Step 4: Prepare combined analysis response
    return {
        "message": "Repository and code quality analysis completed successfully",

        "analysis": result,

        "code_quality": {
            "status": "completed",
            "scanned_source_files": source_result[
                "scanned_source_files"
            ],
            "skipped_files": source_result["skipped_files"],
            "summary": quality_result["summary"],
            "issues": quality_result["issues"]
        }
    }