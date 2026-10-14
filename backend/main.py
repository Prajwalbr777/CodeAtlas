from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from urllib.parse import urlparse

from backend.github_analyzer import analyze_github_repository
from backend.github_source_fetcher import fetch_source_files
from backend.code_quality_scanner import analyze_source_files
from backend.ecosystem_scanner import detect_ecosystems
from backend.dependency_analyzer import analyze_dependencies
from backend.dependency_version_checker import check_dependency_versions


# Create FastAPI application
app = FastAPI(
    title="CodeAtlas API",
    description=(
        "Codebase intelligence, ecosystem detection, "
        "code quality, dependency analysis and "
        "dependency version checking platform"
    ),
    version="1.4.0"
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
        "status": "Backend is running successfully",
        "version": "1.4.0"
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
        or len([
            part for part in parsed_url.path.strip("/").split("/")
            if part
        ]) != 2
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

    # Step 2: Detect technology ecosystems
    ecosystem_result = detect_ecosystems(result["files"])

    # Step 3: Fetch source files and dependency manifests
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
    manifest_files = source_result["manifest_files"]

    # Step 4: Scan source code for potential issues
    quality_result = analyze_source_files(source_files)

    # Step 5: Analyze declared dependencies
    dependency_result = analyze_dependencies(manifest_files)

    # Step 6: Check dependency versions
    version_result = check_dependency_versions(
        dependency_result["dependencies"]
    )

    # Step 7: Prepare combined analysis response
    return {
        "message": (
            "Repository, ecosystem, code quality, dependency "
            "and dependency version analysis completed successfully"
        ),

        "analysis": result,

        "ecosystem_analysis": {
            "status": "completed",
            "total_ecosystems": ecosystem_result["total_ecosystems"],
            "ecosystems": ecosystem_result["ecosystems"]
        },

        "code_quality": {
            "status": "completed",
            "scanned_source_files": source_result[
                "scanned_source_files"
            ],
            "skipped_files": source_result["skipped_files"],
            "summary": quality_result["summary"],
            "issues": quality_result["issues"]
        },

        "dependency_analysis": {
            "status": "completed",
            "scanned_manifests": len(manifest_files),
            "skipped_manifests": source_result["skipped_manifests"],
            "total_manifests": dependency_result["total_manifests"],
            "total_dependencies": dependency_result["total_dependencies"],
            "manifests": dependency_result["manifests"],
            "dependencies": dependency_result["dependencies"]
        },

        "dependency_version_analysis": {
            "status": "completed",
            "total_checked": version_result["total_checked"],
            "up_to_date": version_result["up_to_date"],
            "outdated": version_result["outdated"],
            "cannot_compare": version_result["cannot_compare"],
            "newer_than_latest": version_result["newer_than_latest"],
            "results": version_result["results"]
        }
    }