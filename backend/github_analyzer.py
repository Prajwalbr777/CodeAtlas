import requests


def analyze_github_repository(repo_url):

    try:
        # Extract owner and repository name
        parts = repo_url.rstrip("/").split("/")

        owner = parts[-2]
        repo = parts[-1].replace(".git", "")

        # GitHub API URL
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"

        # Send request to GitHub
        response = requests.get(api_url, timeout=15)

        if response.status_code != 200:
            return {
                "error": "Unable to access repository",
                "status_code": response.status_code
            }

        # Get repository contents
        files = response.json()

        result = []

        for item in files:
            result.append({
                "name": item["name"],
                "type": item["type"],
                "path": item["path"]
            })

        return {
            "repository": repo,
            "owner": owner,
            "files": result
        }

    except requests.RequestException as error:
        return {"error": str(error)}
    except (IndexError, ValueError):
        return {"error": "Invalid GitHub repository URL"}