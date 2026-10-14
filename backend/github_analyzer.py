import requests
from collections import Counter


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


def detect_language(filename):
    filename = filename.lower()

    for extension, language in LANGUAGE_EXTENSIONS.items():
        if filename.endswith(extension):
            return language

    return "Other"


def analyze_github_repository(repo_url):
    try:
        parts = repo_url.rstrip("/").split("/")

        owner = parts[-2]
        repo = parts[-1].replace(".git", "")

        api_url = (
            f"https://api.github.com/repos/"
            f"{owner}/{repo}/git/trees/HEAD?recursive=1"
        )

        response = requests.get(api_url, timeout=30)

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

        for item in tree:
            path = item.get("path", "")
            item_type = item.get("type", "")

            if item_type == "blob":
                filename = path.split("/")[-1]
                language = detect_language(filename)

                files.append({
                    "name": filename,
                    "path": path,
                    "type": "file",
                    "language": language
                })

                language_counts[language] += 1

                path_parts = path.split("/")

                for index in range(1, len(path_parts)):
                    folders.add("/".join(path_parts[:index]))

            elif item_type == "tree":
                folders.add(path)

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

        return {
            "repository": repo,
            "owner": owner,
            "total_files": total_files,
            "total_folders": len(folders),
            "files": files,
            "folders": sorted(folders),
            "language_distribution": language_distribution
        }

    except requests.RequestException as error:
        return {"error": str(error)}

    except (IndexError, ValueError):
        return {"error": "Invalid GitHub repository URL"}