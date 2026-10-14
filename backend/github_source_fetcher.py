import requests
from urllib.parse import quote


# Source-code extensions that CodeAtlas can inspect.
SOURCE_EXTENSIONS = {
    ".py", ".java", ".js", ".jsx", ".ts", ".tsx",
    ".cpp", ".cc", ".c", ".h", ".hpp", ".cs",
    ".php", ".rb", ".go", ".rs", ".swift",
    ".kt", ".kts", ".dart", ".scala", ".sh",
    ".bash", ".ps1", ".sql"
}


# Dependency manifest files supported by our Dependency Analyzer.
MANIFEST_FILENAMES = {
    "requirements.txt",
    "package.json",
    "pom.xml",
    "go.mod",
    "cargo.toml",
    "composer.json",
    "gemfile"
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


# Maximum file size: 200 KB.
MAX_FILE_SIZE = 200 * 1024


# Common headers for GitHub requests.
GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "CodeAtlas"
}


def is_ignored_path(path):
    """
    Check whether a file belongs to an ignored folder.
    """

    parts = path.lower().split("/")

    return any(
        folder in IGNORED_FOLDERS
        for folder in parts[:-1]
    )


def is_source_file(path):
    """
    Check whether a file is a supported source-code file.
    """

    if not path:
        return False

    if is_ignored_path(path):
        return False

    filename = path.lower().split("/")[-1]

    return any(
        filename.endswith(extension)
        for extension in SOURCE_EXTENSIONS
    )


def is_manifest_file(path):
    """
    Check whether a file is a supported dependency manifest.
    """

    if not path:
        return False

    if is_ignored_path(path):
        return False

    filename = path.split("/")[-1].lower()

    return filename in MANIFEST_FILENAMES


def fetch_raw_file(owner, repo, branch, path):
    """
    Download the contents of a file from a GitHub repository.
    """

    encoded_path = quote(path, safe="/")

    raw_url = (
        f"https://raw.githubusercontent.com/"
        f"{owner}/{repo}/{quote(branch, safe='')}/{encoded_path}"
    )

    response = requests.get(
        raw_url,
        headers={"User-Agent": "CodeAtlas"},
        timeout=15
    )

    if response.status_code != 200:
        return None

    # Skip binary or unsupported content types.
    content_type = response.headers.get(
        "Content-Type", ""
    ).lower()

    supported_content = (
        "text/" in content_type
        or "json" in content_type
        or "javascript" in content_type
        or "xml" in content_type
        or "octet-stream" in content_type
    )

    if not supported_content:
        return None

    return response.text


def fetch_source_files(owner, repo, files):
    """
    Fetch source-code files and dependency manifests
    from a public GitHub repository.
    """

    try:

        # Step 1: Retrieve the repository's default branch.
        repo_api_url = (
            f"https://api.github.com/repos/{owner}/{repo}"
        )

        repo_response = requests.get(
            repo_api_url,
            headers=GITHUB_HEADERS,
            timeout=20
        )

        if repo_response.status_code != 200:
            return {
                "error": "Unable to retrieve repository information",
                "status_code": repo_response.status_code,
                "files": [],
                "manifest_files": [],
                "scanned_source_files": 0,
                "skipped_files": 0
            }

        default_branch = repo_response.json().get(
            "default_branch", "main"
        )

        # Separate collections for the two analyzers.
        fetched_files = []
        manifest_files = []

        skipped_files = 0
        skipped_manifests = 0

        # Step 2: Process repository files.
        for file in files:

            path = file.get("path", "")

            if not path:
                continue

            # Ignore files inside excluded folders.
            if is_ignored_path(path):
                continue

            file_size = file.get("size", 0)

            # Step 3: Fetch dependency manifest files.
            if is_manifest_file(path):

                if file_size > MAX_FILE_SIZE:
                    skipped_manifests += 1
                    continue

                try:
                    content = fetch_raw_file(
                        owner,
                        repo,
                        default_branch,
                        path
                    )

                    if content is None:
                        skipped_manifests += 1
                        continue

                    manifest_files.append({
                        "path": path,
                        "content": content
                    })

                except requests.RequestException:
                    skipped_manifests += 1

                continue

            # Step 4: Fetch supported source-code files.
            if not is_source_file(path):
                continue

            if file_size > MAX_FILE_SIZE:
                skipped_files += 1
                continue

            language = file.get("language", "Other")

            if language == "Other":
                skipped_files += 1
                continue

            try:
                source_code = fetch_raw_file(
                    owner,
                    repo,
                    default_branch,
                    path
                )

                if source_code is None:
                    skipped_files += 1
                    continue

                fetched_files.append({
                    "path": path,
                    "language": language,
                    "content": source_code
                })

            except requests.RequestException:
                skipped_files += 1

        # Step 5: Return both collections separately.
        return {
            "files": fetched_files,
            "scanned_source_files": len(fetched_files),
            "skipped_files": skipped_files,

            "manifest_files": manifest_files,
            "skipped_manifests": skipped_manifests
        }

    except requests.RequestException as error:

        return {
            "error": str(error),
            "files": [],
            "manifest_files": [],
            "scanned_source_files": 0,
            "skipped_files": 0
        }