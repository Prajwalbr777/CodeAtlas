from pathlib import PurePosixPath


# Technology ecosystem definitions
ECOSYSTEM_RULES = {
    "Python": {
        "files": [
            "requirements.txt",
            "pyproject.toml",
            "Pipfile",
            "setup.py",
            "setup.cfg"
        ],
        "extensions": [".py"]
    },
    "JavaScript": {
        "files": [
            "package.json",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml"
        ],
        "extensions": [".js", ".jsx", ".mjs", ".cjs"]
    },
    "TypeScript": {
        "files": [
            "tsconfig.json"
        ],
        "extensions": [".ts", ".tsx"]
    },
    "Java": {
        "files": [
            "pom.xml",
            "build.gradle",
            "build.gradle.kts"
        ],
        "extensions": [".java"]
    },
    "C/C++": {
        "files": [
            "CMakeLists.txt",
            "Makefile"
        ],
        "extensions": [".c", ".cpp", ".cc", ".h", ".hpp"]
    },
    "Go": {
        "files": ["go.mod", "go.sum"],
        "extensions": [".go"]
    },
    "Rust": {
        "files": ["Cargo.toml", "Cargo.lock"],
        "extensions": [".rs"]
    },
    "PHP": {
        "files": ["composer.json"],
        "extensions": [".php"]
    },
    "Ruby": {
        "files": ["Gemfile", "Gemfile.lock"],
        "extensions": [".rb"]
    },
    "Kotlin": {
        "files": ["build.gradle.kts"],
        "extensions": [".kt", ".kts"]
    },
    "Swift": {
        "files": ["Package.swift"],
        "extensions": [".swift"]
    },
    "Dart": {
        "files": ["pubspec.yaml"],
        "extensions": [".dart"]
    },
    "Scala": {
        "files": ["build.sbt"],
        "extensions": [".scala"]
    }
}


def detect_ecosystems(files):
    """
    Detect technology ecosystems using repository file paths.

    Args:
        files: List of repository file dictionaries.

    Returns:
        Dictionary containing detected ecosystems and summary.
    """

    detected = {}

    for ecosystem, rules in ECOSYSTEM_RULES.items():
        detected[ecosystem] = {
            "ecosystem": ecosystem,
            "manifest_files": [],
            "source_files": 0,
            "detected": False
        }

    for file_info in files:
        file_path = file_info.get("path", "")
        filename = PurePosixPath(file_path).name
        extension = PurePosixPath(filename).suffix.lower()

        for ecosystem, rules in ECOSYSTEM_RULES.items():

            if filename in rules["files"]:
                if file_path not in detected[ecosystem]["manifest_files"]:
                    detected[ecosystem]["manifest_files"].append(file_path)

                detected[ecosystem]["detected"] = True

            elif extension in rules["extensions"]:
                detected[ecosystem]["source_files"] += 1
                detected[ecosystem]["detected"] = True

    results = [
        ecosystem_data
        for ecosystem_data in detected.values()
        if ecosystem_data["detected"]
    ]

    results.sort(
        key=lambda item: (
            bool(item["manifest_files"]),
            item["source_files"]
        ),
        reverse=True
    )

    return {
        "total_ecosystems": len(results),
        "ecosystems": results
    }