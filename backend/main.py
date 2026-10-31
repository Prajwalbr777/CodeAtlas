
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from urllib.parse import urlparse

from backend.github_analyzer import analyze_github_repository
from backend.github_source_fetcher import fetch_source_files
from backend.code_quality_scanner import analyze_source_files
from backend.ecosystem_scanner import detect_ecosystems
from backend.dependency_analyzer import analyze_dependencies
from backend.dependency_version_checker import check_dependency_versions
from backend.vulnerability_scanner import scan_vulnerabilities
from backend.ai_code_explainer import explain_code_issue
from backend.report_generator import generate_pdf_report


# Create FastAPI application
app = FastAPI(
    title="CodeAtlas API",
    description=(
        "Codebase intelligence, ecosystem detection, "
        "code quality, dependency analysis, version checking, "
        "vulnerability detection, AI code explanation "
        "and PDF report generation"
    ),
    version="1.7.0"
)


# Allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Repository request model
class RepositoryRequest(BaseModel):
    repo_url: str


# AI explanation request model
class IssueExplanationRequest(BaseModel):
    title: str
    severity: str
    description: str = ""
    file: str = ""
    code: str = ""


# Home route
@app.get("/")
def home():
    return {
        "message": "Welcome to CodeAtlas!",
        "status": "Backend is running successfully",
        "version": "1.7.0"
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

    # Step 7: Detect known dependency vulnerabilities
    vulnerability_result = scan_vulnerabilities(
        dependency_result["dependencies"]
    )

    # Step 8: Prepare combined analysis response
    return {
        "message": (
            "Repository, ecosystem, code quality, dependency, "
            "version and vulnerability analysis completed successfully"
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
        },

        "vulnerability_analysis": {
            "status": "completed",
            "total_dependencies": vulnerability_result[
                "total_dependencies"
            ],
            "checked_dependencies": vulnerability_result[
                "checked_dependencies"
            ],
            "vulnerable_dependencies": vulnerability_result[
                "vulnerable_dependencies"
            ],
            "no_known_vulnerabilities": vulnerability_result[
                "no_known_vulnerabilities"
            ],
            "cannot_check": vulnerability_result["cannot_check"],
            "check_failed": vulnerability_result["check_failed"],
            "results": vulnerability_result["results"]
        }
    }


# AI-powered code issue explanation
@app.post("/explain-issue")
def explain_issue(request: IssueExplanationRequest):

    issue = request.dict()

    result = explain_code_issue(issue)

    if result.get("status") == "error":
        raise HTTPException(
            status_code=503,
            detail=result.get("message", "AI explanation failed")
        )

    return result


# Generate and download PDF report
@app.post("/download-report")
def download_report(report_data: dict):

    try:
        # Generate PDF using the report generator
        pdf_content = generate_pdf_report(report_data)

        # Return downloadable PDF file
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": (
                    'attachment; filename="CodeAtlas_Report.pdf"'
                )
            }
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"PDF report generation failed: {str(error)}"
        )
