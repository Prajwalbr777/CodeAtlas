from backend.ecosystem_scanner import detect_ecosystems


def test_detect_python_and_javascript():
    files = [
        {"path": "requirements.txt"},
        {"path": "app.py"},
        {"path": "package.json"},
        {"path": "src/index.js"},
        {"path": "README.md"}
    ]

    result = detect_ecosystems(files)

    assert result["total_ecosystems"] == 2

    ecosystem_names = [
        item["ecosystem"]
        for item in result["ecosystems"]
    ]

    assert "Python" in ecosystem_names
    assert "JavaScript" in ecosystem_names


def test_detect_java():
    files = [
        {"path": "pom.xml"},
        {"path": "src/Main.java"}
    ]

    result = detect_ecosystems(files)

    assert result["total_ecosystems"] == 1
    assert result["ecosystems"][0]["ecosystem"] == "Java"


def test_empty_repository():
    result = detect_ecosystems([])

    assert result["total_ecosystems"] == 0
    assert result["ecosystems"] == []


if __name__ == "__main__":
    test_detect_python_and_javascript()
    test_detect_java()
    test_empty_repository()

    print("All ecosystem scanner tests passed!")