import requests


def analyze_github_repository(repo_url):
    try:
        parts = repo_url.rstrip("/").split("/")

        owner = parts[-2]
        repo = parts[-1].replace(".git", "")

        api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"

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

        for item in tree:
            path = item.get("path", "")
            item_type = item.get("type", "")

            if item_type == "blob":
                files.append({
                    "name": path.split("/")[-1],
                    "path": path,
                    "type": "file"
                })

                parts_in_path = path.split("/")

                for index in range(1, len(parts_in_path)):
                    folders.add("/".join(parts_in_path[:index]))

            elif item_type == "tree":
                folders.add(path)

        return {
            "repository": repo,
            "owner": owner,
            "total_files": len(files),
            "total_folders": len(folders),
            "files": files,
            "folders": sorted(folders)
        }

    except requests.RequestException as error:
        return {"error": str(error)}

    except (IndexError, ValueError):
        return {"error": "Invalid GitHub repository URL"}