import json
import re
from pathlib import PurePosixPath


# Supported dependency manifest files
DEPENDENCY_MANIFESTS = {
    "Python": ["requirements.txt", "pyproject.toml", "Pipfile"],
    "JavaScript": ["package.json"],
    "Java": ["pom.xml"],
    "Go": ["go.mod"],
    "Rust": ["Cargo.toml"],
    "PHP": ["composer.json"],
    "Ruby": ["Gemfile"]
}


def parse_requirements_txt(content):
    """Extract dependencies from Python requirements.txt."""

    dependencies = []

    for line in content.splitlines():
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith(("-e ", "--", "-r ", "-c ")):
            continue

        match = re.match(
            r"^([A-Za-z0-9_.-]+)\s*(?:\[[^\]]+\])?\s*(.*)$",
            line
        )

        if match:
            name = match.group(1)
            version = match.group(2).strip() or "Not specified"

            dependencies.append({
                "name": name,
                "version": version
            })

    return dependencies


def parse_package_json(content):
    """Extract dependencies from JavaScript package.json."""

    try:
        package_data = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return []

    dependencies = []

    for section in [
        "dependencies",
        "devDependencies",
        "peerDependencies",
        "optionalDependencies"
    ]:
        section_data = package_data.get(section, {})

        if not isinstance(section_data, dict):
            continue

        for name, version in section_data.items():
            dependencies.append({
                "name": name,
                "version": str(version),
                "type": section
            })

    return dependencies


def parse_pom_xml(content):
    """Extract direct dependencies from a Maven pom.xml."""

    dependencies = []

    dependency_pattern = re.compile(
        r"<dependency\b[^>]*>(.*?)</dependency>",
        re.DOTALL
    )

    for block in dependency_pattern.findall(content):
        group = re.search(
            r"<groupId>\s*(.*?)\s*</groupId>",
            block,
            re.DOTALL
        )

        artifact = re.search(
            r"<artifactId>\s*(.*?)\s*</artifactId>",
            block,
            re.DOTALL
        )

        version = re.search(
            r"<version>\s*(.*?)\s*</version>",
            block,
            re.DOTALL
        )

        if group and artifact:
            dependencies.append({
                "name": f"{group.group(1)}:{artifact.group(1)}",
                "version": (
                    version.group(1).strip()
                    if version
                    else "Not specified"
                )
            })

    return dependencies


def parse_go_mod(content):
    """Extract dependencies from a Go go.mod file."""

    dependencies = []
    inside_require_block = False

    for line in content.splitlines():
        line = line.strip()

        if line.startswith("require ("):
            inside_require_block = True
            continue

        if inside_require_block and line == ")":
            inside_require_block = False
            continue

        if line.startswith("require "):
            line = line[len("require "):]

        elif not inside_require_block:
            continue

        parts = line.split()

        if len(parts) >= 2 and not line.startswith("//"):
            dependencies.append({
                "name": parts[0],
                "version": parts[1]
            })

    return dependencies


def parse_cargo_toml(content):
    """Extract dependencies from Rust Cargo.toml."""

    dependencies = []
    inside_dependencies = False

    for line in content.splitlines():
        line = line.strip()

        if line.startswith("[") and line.endswith("]"):
            inside_dependencies = (
                line == "[dependencies]"
                or line.startswith("[dependencies.")
            )
            continue

        if not inside_dependencies or not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        name, version = line.split("=", 1)

        dependencies.append({
            "name": name.strip(),
            "version": version.strip()
        })

    return dependencies


def parse_composer_json(content):
    """Extract PHP dependencies from composer.json."""

    try:
        package_data = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return []

    dependencies = []

    for section in ["require", "require-dev"]:
        section_data = package_data.get(section, {})

        if not isinstance(section_data, dict):
            continue

        for name, version in section_data.items():

            if name == "php":
                continue

            dependencies.append({
                "name": name,
                "version": str(version),
                "type": section
            })

    return dependencies


def parse_gemfile(content):
    """Extract Ruby dependencies from Gemfile."""

    dependencies = []

    pattern = re.compile(
        r"""^\s*gem\s+['"]([^'"]+)['"]\s*(?:,\s*['"]([^'"]+)['"])?""",
        re.MULTILINE
    )

    for match in pattern.finditer(content):
        dependencies.append({
            "name": match.group(1),
            "version": match.group(2) or "Not specified"
        })

    return dependencies


def analyze_dependencies(files):
    """
    Analyze supported dependency manifest files.

    Args:
        files: List of dictionaries containing path and content.

    Returns:
        Dependency analysis summary and extracted dependencies.
    """

    parsers = {
        "requirements.txt": parse_requirements_txt,
        "package.json": parse_package_json,
        "pom.xml": parse_pom_xml,
        "go.mod": parse_go_mod,
        "Cargo.toml": parse_cargo_toml,
        "composer.json": parse_composer_json,
        "Gemfile": parse_gemfile
    }

    manifest_results = []
    all_dependencies = []

    for file_info in files:

        path = file_info.get("path", "")
        content = file_info.get("content", "")

        filename = PurePosixPath(path).name

        parser = parsers.get(filename)

        if parser is None:
            continue

        dependencies = parser(content)

        manifest_results.append({
            "manifest_file": path,
            "dependency_count": len(dependencies),
            "dependencies": dependencies
        })

        for dependency in dependencies:
            all_dependencies.append({
                **dependency,
                "manifest_file": path
            })

    return {
        "total_manifests": len(manifest_results),
        "total_dependencies": len(all_dependencies),
        "manifests": manifest_results,
        "dependencies": all_dependencies
    }