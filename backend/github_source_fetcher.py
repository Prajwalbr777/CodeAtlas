import requests


# File extensions whose source code we want to inspect.
SOURCE_EXTENSIONS = {
    ".py", ".java", ".js", ".jsx", ".ts", ".tsx",
    ".cpp", ".cc", ".c", ".h", ".hpp", ".cs",
    ".php", ".rb", ".go", ".rs", ".swift",
    ".kt", ".kts", ".dart", ".scala", ".sh",
    ".bash", ".ps1", ".sql"
}

# Folders that should not be scanned.
IGNORED_FOLDERS = {
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    "dist",
    "build",
    "vendor"
}

# Maximum source file size: 200 KB.
MAX_FILE_SIZE = 200 * 1024


def is_source_file(path):
    parts = path.lower().split("/")

    if any(folder in IGNORED_FOLDERS for folder in parts[:-1]):
        return False

    return any(
        parts[-1].endswith(extension)
        for extension in SOURCE_EXTENSIONS
    )


def fetch_source_files(owner, repo, files):
    """
    Fetch supported source files from a public GitHub repository.
    """

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "CodeAtlas"
    }

    try:
        # Get the repository's default branch.
        repo_api_url = (
            f"https://api.github.com/repos/{owner}/{repo}"
        )

        repo_response = requests.get(
            repo_api_url,
            headers=headers,
            timeout=20
        )

        if repo_response.status_code != 200:
            return {
                "error": "Unable to retrieve repository information",
                "status_code": repo_response.status_code,
                "files": []
            }

        default_branch = repo_response.json().get(
            "default_branch", "main"
        )

        fetched_files = []
        skipped_files = 0

        for file in files:

            path = file.get("path", "")

            if not is_source_file(path):
                continue

            # Skip oversized files.
            if file.get("size", 0) > MAX_FILE_SIZE:
                skipped_files += 1
                continue

            raw_url = (
                f"https://raw.githubusercontent.com/"
                f"{owner}/{repo}/{default_branch}/{path}"
            )

            try:
                response = requests.get(
                    raw_url,
                    headers={"User-Agent": "CodeAtlas"},
                    timeout=15
                )

                if response.status_code != 200:
                    skipped_files += 1
                    continue

                # Skip binary or non-text responses.
                content_type = response.headers.get(
                    "Content-Type", ""
                ).lower()

                if "text/" not in content_type and (
                    "json" not in content_type
                    and "javascript" not in content_type
                    and "xml" not in content_type
                ):
                    skipped_files += 1
                    continue

                source_code = response.text

                # Detect language from the existing file metadata.
                language = file.get("language", "Other")

                if language == "Other":
                    skipped_files += 1
                    continue

                fetched_files.append({
                    "path": path,
                    "language": language,
                    "content": source_code
                })

            except requests.RequestException:
                skipped_files += 1

        return {
            "files": fetched_files,
            "scanned_source_files": len(fetched_files),
            "skipped_files": skipped_files
        }

    except requests.RequestException as error:
        return {
            "error": str(error),
            "files": []
        }