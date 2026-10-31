
import requests
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed


# Source-code extensions that CodeAtlas can inspect.
SOURCE_EXTENSIONS = {
    ".py", ".java", ".js", ".jsx", ".ts", ".tsx",
    ".cpp", ".cc", ".c", ".h", ".hpp", ".cs",
    ".php", ".rb", ".go", ".rs", ".swift",
    ".kt", ".kts", ".dart", ".scala", ".sh",
    ".bash", ".ps1", ".sql"
}


# Dependency manifest files supported by CodeAtlas.
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

# Maximum number of files to download.
MAX_SOURCE_FILES = 500
MAX_MANIFEST_FILES = 100

# Number of simultaneous downloads.
MAX_WORKERS = 8

# Network timeout for individual file downloads.
REQUEST_TIMEOUT = 15


# Common headers for GitHub requests.
GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "CodeAtlas"
}


def is_ignored_path(path):
    """Check whether a file belongs to an ignored folder."""

    parts = path.lower().split("/")

    return any(
        folder in IGNORED_FOLDERS
        for folder in parts[:-1]
    )


def is_source_file(path):
    """Check whether a file is a supported source-code file."""

    if not path or is_ignored_path(path):
        return False

    filename = path.lower().split("/")[-1]

    return any(
        filename.endswith(extension)
        for extension in SOURCE_EXTENSIONS
    )


def is_manifest_file(path):
    """Check whether a file is a supported dependency manifest."""

    if not path or is_ignored_path(path):
        return False

    filename = path.split("/")[-1].lower()

    return filename in MANIFEST_FILENAMES


def fetch_raw_file(owner, repo, branch, path):
    """Download one file from a public GitHub repository."""

    encoded_path = quote(path, safe="/")

    raw_url = (
        f"https://raw.githubusercontent.com/"
        f"{owner}/{repo}/{quote(branch, safe='')}/{encoded_path}"
    )

    response = requests.get(
        raw_url,
        headers={"User-Agent": "CodeAtlas"},
        timeout=REQUEST_TIMEOUT
    )

    if response.status_code != 200:
        return None

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

    # Protect against files larger than the configured limit.
    if len(response.content) > MAX_FILE_SIZE:
        return None

    return response.text


def download_file(task):
    """
    Download one source file or manifest.

    This function is executed by the thread pool.
    """

    owner, repo, branch, file_info = task

    path = file_info.get("path", "")
    file_type = file_info.get("type")

    try:
        content = fetch_raw_file(
            owner,
            repo,
            branch,
            path
        )

        if content is None:
            return path, file_type, None, None

        return path, file_type, content, None

    except requests.RequestException as error:
        return path, file_type, None, str(error)


def fetch_source_files(owner, repo, files):
    """
    Fetch source files and dependency manifests concurrently.

    Uses a limited thread pool to reduce network waiting time.
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
                "skipped_files": 0,
                "skipped_manifests": 0
            }

        default_branch = repo_response.json().get(
            "default_branch", "main"
        )

        # Step 2: Identify source files and manifests.
        source_candidates = []
        manifest_candidates = []

        skipped_files = 0
        skipped_manifests = 0

        for file in files:

            path = file.get("path", "")

            if not path:
                continue

            if is_ignored_path(path):
                continue

            file_size = file.get("size", 0)

            # Identify dependency manifests.
            if is_manifest_file(path):

                if file_size > MAX_FILE_SIZE:
                    skipped_manifests += 1
                    continue

                manifest_candidates.append({
                    "path": path,
                    "type": "manifest"
                })

                continue

            # Identify supported source files.
            if is_source_file(path):

                language = file.get("language", "Other")

                if language == "Other":
                    skipped_files += 1
                    continue

                if file_size > MAX_FILE_SIZE:
                    skipped_files += 1
                    continue

                source_candidates.append({
                    "path": path,
                    "language": language,
                    "type": "source"
                })

        # Step 3: Apply download limits.
        if len(source_candidates) > MAX_SOURCE_FILES:
            skipped_files += (
                len(source_candidates) - MAX_SOURCE_FILES
            )

            source_candidates = source_candidates[
                :MAX_SOURCE_FILES
            ]

        if len(manifest_candidates) > MAX_MANIFEST_FILES:
            skipped_manifests += (
                len(manifest_candidates) - MAX_MANIFEST_FILES
            )

            manifest_candidates = manifest_candidates[
                :MAX_MANIFEST_FILES
            ]

        # Step 4: Prepare all download tasks.
        tasks = []

        for file_info in source_candidates:
            tasks.append((
                owner,
                repo,
                default_branch,
                file_info
            ))

        for file_info in manifest_candidates:
            tasks.append((
                owner,
                repo,
                default_branch,
                file_info
            ))

        fetched_files = []
        manifest_files = []

        # Step 5: Download files concurrently.
        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS
        ) as executor:

            futures = [
                executor.submit(download_file, task)
                for task in tasks
            ]

            for future in as_completed(futures):

                path, file_type, content, error = future.result()

                if content is None:

                    if file_type == "source":
                        skipped_files += 1
                    else:
                        skipped_manifests += 1

                    continue

                if file_type == "source":

                    # Retrieve the original language.
                    language = next(
                        (
                            item["language"]
                            for item in source_candidates
                            if item["path"] == path
                        ),
                        "Other"
                    )

                    fetched_files.append({
                        "path": path,
                        "language": language,
                        "content": content
                    })

                else:

                    manifest_files.append({
                        "path": path,
                        "content": content
                    })

        # Step 6: Return results in a consistent order.
        fetched_files.sort(
            key=lambda item: item["path"].lower()
        )

        manifest_files.sort(
            key=lambda item: item["path"].lower()
        )

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
            "skipped_files": 0,
            "skipped_manifests": 0
        }

    except (ValueError, TypeError, AttributeError) as error:

        return {
            "error": f"Could not process repository files: {error}",
            "files": [],
            "manifest_files": [],
            "scanned_source_files": 0,
            "skipped_files": 0,
            "skipped_manifests": 0
        }
