
import re
import requests
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed


PYPI_URL = "https://pypi.org/pypi/{package}/json"
NPM_URL = "https://registry.npmjs.org/{package}/latest"

REQUEST_TIMEOUT = 10
MAX_WORKERS = 8

HEADERS = {
    "User-Agent": "CodeAtlas-Dependency-Checker"
}


def is_exact_version(version):
    """Check whether a version is an exact version."""

    if not version or not isinstance(version, str):
        return False

    version = version.strip()

    if version.lower() in {
        "not specified", "latest", "*", "unknown"
    }:
        return False

    range_symbols = ["^", "~", ">", "<", "*", ",", "||"]

    if any(symbol in version for symbol in range_symbols):
        return False

    if version.startswith(("=", "v")):
        version = version.lstrip("=v").strip()

    return bool(
        re.fullmatch(
            r"\d+(?:\.\d+)*(?:[-+][A-Za-z0-9.-]+)?",
            version
        )
    )


def normalize_version(version):
    """Remove common prefixes from exact version strings."""

    return version.strip().lstrip("=v").strip()


def compare_versions(declared_version, latest_version):
    """Compare simple numeric version components."""

    declared = normalize_version(declared_version)
    latest = normalize_version(latest_version)

    declared_match = re.match(r"^(\d+(?:\.\d+)*)", declared)
    latest_match = re.match(r"^(\d+(?:\.\d+)*)", latest)

    if not declared_match or not latest_match:
        return "Cannot compare"

    try:
        declared_parts = tuple(
            int(part)
            for part in declared_match.group(1).split(".")
        )

        latest_parts = tuple(
            int(part)
            for part in latest_match.group(1).split(".")
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
    """Get the latest Python package version from PyPI."""

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
    """Get the latest JavaScript package version from npm."""

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


def get_dependency_ecosystem(dependency):
    """Identify ecosystem from dependency manifest filename."""

    ecosystem = dependency.get("ecosystem")

    if ecosystem:
        return ecosystem

    manifest_file = str(
        dependency.get("manifest_file", "")
    ).lower()

    if manifest_file.endswith("requirements.txt"):
        return "Python"

    if manifest_file.endswith("package.json"):
        return "JavaScript"

    if manifest_file.endswith("pom.xml"):
        return "Java"

    if manifest_file.endswith("go.mod"):
        return "Go"

    if manifest_file.endswith("cargo.toml"):
        return "Rust"

    if manifest_file.endswith("composer.json"):
        return "PHP"

    if manifest_file.endswith("gemfile"):
        return "Ruby"

    return "Unknown"


def get_registry_details(ecosystem):
    """Return registry name and version-fetching function."""

    normalized = ecosystem.lower()

    if normalized == "python":
        return "pypi", get_latest_python_version

    if normalized in {"javascript", "node", "npm"}:
        return "npm", get_latest_npm_version

    return None, None


def check_dependency_version(dependency, ecosystem, cache=None):
    """Check one dependency against its public package registry."""

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

    registry, fetch_latest = get_registry_details(ecosystem)

    if not registry:
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
    Check dependencies using concurrent registry requests.

    Each unique supported package is fetched only once.
    """

    cache = {}
    results = []

    # Step 1: Identify unique packages that need registry checks.
    package_tasks = {}

    for dependency in dependencies:

        ecosystem = get_dependency_ecosystem(dependency)

        name = str(
            dependency.get("name", "")
        ).strip()

        version = str(
            dependency.get("version", "Not specified")
        ).strip()

        if not name or not is_exact_version(version):
            continue

        registry, fetch_latest = get_registry_details(ecosystem)

        if not registry:
            continue

        cache_key = f"{registry}:{name.lower()}"

        if cache_key not in package_tasks:
            package_tasks[cache_key] = (
                name,
                fetch_latest
            )

    # Step 2: Fetch unique packages concurrently.
    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        future_to_key = {}

        for cache_key, task in package_tasks.items():

            name, fetch_latest = task

            future = executor.submit(
                fetch_latest,
                name
            )

            future_to_key[future] = cache_key

        for future in as_completed(future_to_key):

            cache_key = future_to_key[future]

            try:
                cache[cache_key] = future.result()

            except Exception:
                cache[cache_key] = (
                    None,
                    "Could not retrieve package version"
                )

    # Step 3: Build individual results using the cache.
    for dependency in dependencies:

        ecosystem = get_dependency_ecosystem(dependency)

        results.append(
            check_dependency_version(
                dependency,
                ecosystem,
                cache
            )
        )

    # Step 4: Return the original summary structure.
    return {
        "total_checked": len(results),

        "up_to_date": sum(
            item["status"] == "Up to date"
            for item in results
        ),

        "outdated": sum(
            item["status"] == "Outdated"
            for item in results
        ),

        "cannot_compare": sum(
            item["status"] == "Cannot compare"
            for item in results
        ),

        "newer_than_latest": sum(
            item["status"] == "Newer than latest"
            for item in results
        ),

        "results": results
    }
