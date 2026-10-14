from backend.dependency_version_checker import (
    is_exact_version,
    compare_versions,
    check_dependency_versions
)


def test_exact_version():
    assert is_exact_version("2.1.0") is True
    assert is_exact_version("1.5") is True
    assert is_exact_version("^2.1.0") is False
    assert is_exact_version("Not specified") is False


def test_version_comparison():
    assert compare_versions("1.0.0", "1.0.0") == "Up to date"
    assert compare_versions("1.0.0", "2.0.0") == "Outdated"
    assert compare_versions("3.0.0", "2.0.0") == "Newer than latest"


def test_unsupported_ecosystem():
    dependency = {
        "name": "example-package",
        "version": "1.0.0",
        "manifest_file": "pom.xml"
    }

    result = check_dependency_versions([dependency])

    assert result["total_checked"] == 1
    assert result["cannot_compare"] == 1
    assert result["results"][0]["status"] == "Cannot compare"


def run_tests():
    test_exact_version()
    test_version_comparison()
    test_unsupported_ecosystem()

    print("All dependency version checker tests passed!")


if __name__ == "__main__":
    run_tests()