import requests
from collections import Counter
from urllib.parse import urlparse


# ============================================================
# CODEATLAS - GITHUB REPOSITORY ANALYZER
# ============================================================


# Supported programming languages and file extensions
LANGUAGE_EXTENSIONS = {
    ".py": "Python",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".cpp": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++ Header",
    ".hpp": "C++",
    ".cs": "C#",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".php": "PHP",
    ".rb": "Ruby",
    ".go": "Go",
    ".rs": "Rust",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".dart": "Dart",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Shell",
    ".ps1": "PowerShell",
    ".r": "R",
    ".m": "Objective-C",
    ".scala": "Scala",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".json": "JSON",
    ".xml": "XML",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".md": "Markdown"
}


# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
REQUEST_TIMEOUT = 30


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def detect_language(filename):
    filename = filename.lower()

    for extension, language in LANGUAGE_EXTENSIONS.items():
        if filename.endswith(extension):
            return language

    return "Other"


# ============================================================
# REPOSITORY URL VALIDATION
# ============================================================

def extract_repository_details(repo_url):
    parsed_url = urlparse(repo_url.strip())

    if (
        parsed_url.scheme not in ["http", "https"]
        or parsed_url.netloc.lower() not in [
            "github.com",
            "www.github.com"
        ]
    ):
        raise ValueError("Invalid GitHub repository URL")

    parts = [
        part for part in parsed_url.path.strip("/").split("/")
        if part
    ]

    if len(parts) != 2:
        raise ValueError("Please provide a valid GitHub repository URL")

    owner = parts[0]
    repo = parts[1]

    if repo.endswith(".git"):
        repo = repo[:-4]

    return owner, repo


# ============================================================
# GITHUB REPOSITORY ANALYSIS
# ============================================================

def analyze_github_repository(repo_url):

    try:

        # Extract owner and repository name
        owner, repo = extract_repository_details(repo_url)

        api_url = (
            f"{GITHUB_API_URL}/repos/"
            f"{owner}/{repo}/git/trees/HEAD?recursive=1"
        )

        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "CodeAtlas-Repository-Analyzer"
        }

        response = requests.get(
            api_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )

        # Handle GitHub API errors
        if response.status_code != 200:

            return {
                "error": "Unable to access repository",
                "status_code": response.status_code
            }

        data = response.json()

        tree = data.get("tree", [])

        files = []
        folders = set()

        language_counts = Counter()

        # Check every repository item
        for item in tree:

            path = item.get("path", "")
            item_type = item.get("type", "")

            if item_type == "blob":

                filename = path.split("/")[-1]

                language = detect_language(filename)

                # Store file information, including size
                files.append({
                    "name": filename,
                    "path": path,
                    "type": "file",
                    "language": language,
                    "size": item.get("size", 0)
                })

                language_counts[language] += 1

                # Detect parent folders
                path_parts = path.split("/")

                for index in range(1, len(path_parts)):
                    folders.add(
                        "/".join(path_parts[:index])
                    )

            elif item_type == "tree":

                folders.add(path)

        # ====================================================
        # LANGUAGE DISTRIBUTION
        # ====================================================

        total_files = len(files)

        language_distribution = []

        for language, count in language_counts.most_common():

            percentage = (
                round((count / total_files) * 100, 2)
                if total_files > 0 else 0
            )

            language_distribution.append({
                "language": language,
                "files": count,
                "percentage": percentage
            })

        # ====================================================
        # FINAL RESULT
        # ====================================================

        return {
            "repository": repo,
            "owner": owner,
            "total_files": total_files,
            "total_folders": len(folders),
            "files": files,
            "folders": sorted(folders),
            "language_distribution": language_distribution
        }

    except ValueError as error:

        return {
            "error": str(error),
            "status_code": 400
        }

    except requests.Timeout:

        return {
            "error": "GitHub request timed out. Please try again.",
            "status_code": 504
        }

    except requests.RequestException as error:

        return {
            "error": f"GitHub connection error: {str(error)}",
            "status_code": 502
        }

    except (IndexError, KeyError, TypeError, ValueError) as error:

        return {
            "error": f"Repository analysis failed: {str(error)}",
            "status_code": 500
        }