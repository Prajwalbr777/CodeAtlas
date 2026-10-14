import re
import requests
from urllib.parse import quote


PYPI_URL = "https://pypi.org/pypi/{package}/json"
NPM_URL = "https://registry.npmjs.org/{package}/latest"

REQUEST_TIMEOUT = 10

HEADERS = {
    "User-Agent": "CodeAtlas-Dependency-Checker"
}


def is_exact_version(version):
    """
    Check whether a version looks like an exact version
    rather than a version range or an unspecified value.
    """

    if not version or not isinstance(version, str):
        return False

    version = version.strip()

    if version.lower() in {
        "not specified",
        "latest",
        "*",
        "unknown"
    }:
        return False

    # Version ranges and common constraint operators
    range_symbols = ["^", "~", ">", "<", "*", ",", "||"]

    if any(symbol in version for symbol in range_symbols):
        return False

    if version.startswith(("=", "v")):
        version = version.lstrip("=v").strip()

    return bool(re.fullmatch(r"\d+(?:\.\d+)*(?:[-+][A-Za-z0-9.-]+)?", version))


def normalize_version(version):
    """Remove common prefixes from exact version strings."""

    return version.strip().lstrip("=v").strip()


def compare_versions(declared_version, latest_version):
    """
    Compare simple numeric version components.

    This is intentionally conservative. It does not attempt
    to fully implement every package manager's version rules.
    """

    declared = normalize_version(declared_version)
    latest = normalize_version(latest_version)

    declared_match = re.match(r"^(\d+(?:\.\d+)*)", declared)
    latest_match = re.match(r"^(\d+(?:\.\d+)*)", latest)

    if not declared_match or not latest_match:
        return "Cannot compare"

    try:
        declared_parts = tuple(
            int(part) for part in declared_match.group(1).split(".")
        )

        latest_parts = tuple(
            int(part) for part in latest_match.group(1).split(".")
        )

        length = max(len(declared_parts), len(latest_parts))

        declared_parts += (0,) * (length - len(declared_parts))
        latest_parts += (0,) * (length - len(latest_parts))

        if declared_parts == latest_parts:
            return "Up to date"

        if declared_parts < latest_parts:
            return "Outdated"

        return "Newer than latest"

    except ValueError:
        return "Cannot compare"


def get_latest_python_version(package_name):
    """Get the latest published Python package version from PyPI."""

    try:
        encoded_name = quote(package_name, safe="")
        url = PYPI_URL.format(package=encoded_name)

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 404:
            return None, "Package not found on PyPI"

        response.raise_for_status()

        package_data = response.json()
        latest_version = package_data.get("info", {}).get("version")

        if not latest_version:
            return None, "Latest version unavailable"

        return latest_version, None

    except requests.Timeout:
        return None, "Registry request timed out"

    except requests.RequestException:
        return None, "Could not reach PyPI"

    except (ValueError, AttributeError):
        return None, "Invalid registry response"


def get_latest_npm_version(package_name):
    """Get the latest published JavaScript package version from npm."""

    try:
        encoded_name = quote(package_name, safe="@/")
        url = NPM_URL.format(package=encoded_name)

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT
        )

        if response.status_code == 404:
            return None, "Package not found on npm"

        response.raise_for_status()

        package_data = response.json()
        latest_version = package_data.get("version")

        if not latest_version:
            return None, "Latest version unavailable"

        return latest_version, None

    except requests.Timeout:
        return None, "Registry request timed out"

    except requests.RequestException:
        return None, "Could not reach npm"

    except (ValueError, AttributeError):
        return None, "Invalid registry response"


def check_dependency_version(dependency, ecosystem, cache=None):
    """
    Check one dependency against its public package registry.

    Supported ecosystems:
    - Python
    - JavaScript

    Other ecosystems are marked as unsupported for now.
    """

    if cache is None:
        cache = {}

    name = str(dependency.get("name", "")).strip()
    declared_version = str(
        dependency.get("version", "Not specified")
    ).strip()

    result = {
        "name": name,
        "ecosystem": ecosystem,
        "declared_version": declared_version,
        "latest_version": None,
        "status": "Cannot compare",
        "message": ""
    }

    if not name:
        result["message"] = "Dependency name is missing"
        return result

    if not is_exact_version(declared_version):
        result["message"] = (
            "Declared version is a range or is not specified. "
            "An exact version is needed for this comparison."
        )
        return result

    normalized_ecosystem = ecosystem.lower()

    if normalized_ecosystem == "python":
        registry = "pypi"
        fetch_latest = get_latest_python_version

    elif normalized_ecosystem in {"javascript", "node", "npm"}:
        registry = "npm"
        fetch_latest = get_latest_npm_version

    else:
        result["message"] = (
            "Version checking is not yet supported for this ecosystem"
        )
        return result

    cache_key = f"{registry}:{name.lower()}"

    if cache_key not in cache:
        cache[cache_key] = fetch_latest(name)

    latest_version, error = cache[cache_key]

    if error:
        result["message"] = error
        return result

    result["latest_version"] = latest_version
    result["status"] = compare_versions(
        declared_version,
        latest_version
    )

    result["message"] = (
        "Version comparison completed"
        if result["status"] != "Cannot compare"
        else "The versions could not be compared safely"
    )

    return result


def check_dependency_versions(dependencies):
    """
    Check a list of extracted dependencies.

    Returns a summary and individual version-check results.
    """

    cache = {}
    results = []

    for dependency in dependencies:
        ecosystem = dependency.get("ecosystem", "")

        if not ecosystem:
            manifest_file = str(
                dependency.get("manifest_file", "")
            ).lower()

            if manifest_file.endswith("requirements.txt"):
                ecosystem = "Python"
            elif manifest_file.endswith("package.json"):
                ecosystem = "JavaScript"
            elif manifest_file.endswith("pom.xml"):
                ecosystem = "Java"
            elif manifest_file.endswith("go.mod"):
                ecosystem = "Go"
            elif manifest_file.endswith("cargo.toml"):
                ecosystem = "Rust"
            elif manifest_file.endswith("composer.json"):
                ecosystem = "PHP"
            elif manifest_file.endswith("gemfile"):
                ecosystem = "Ruby"
            else:
                ecosystem = "Unknown"

        results.append(
            check_dependency_version(
                dependency,
                ecosystem,
                cache
            )
        )

    return {
        "total_checked": len(results),
        "up_to_date": sum(
            item["status"] == "Up to date" for item in results
        ),
        "outdated": sum(
            item["status"] == "Outdated" for item in results
        ),
        "cannot_compare": sum(
            item["status"] == "Cannot compare" for item in results
        ),
        "newer_than_latest": sum(
            item["status"] == "Newer than latest" for item in results
        ),
        "results": results
    }