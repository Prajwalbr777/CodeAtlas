from backend.dependency_analyzer import analyze_dependencies


def test_python_dependencies():
    files = [
        {
            "path": "requirements.txt",
            "content": """
fastapi==0.115.0
requests>=2.31.0
uvicorn==0.30.0
"""
        }
    ]

    result = analyze_dependencies(files)

    assert result["total_manifests"] == 1
    assert result["total_dependencies"] == 3


def test_javascript_dependencies():
    files = [
        {
            "path": "package.json",
            "content": """
{
    "dependencies": {
        "react": "^18.0.0",
        "express": "^4.18.0"
    },
    "devDependencies": {
        "vite": "^5.0.0"
    }
}
"""
        }
    ]

    result = analyze_dependencies(files)

    assert result["total_dependencies"] == 3


def test_java_dependencies():
    files = [
        {
            "path": "pom.xml",
            "content": """
<project>
    <dependencies>
        <dependency>
            <groupId>org.springframework</groupId>
            <artifactId>spring-core</artifactId>
            <version>6.0.0</version>
        </dependency>
    </dependencies>
</project>
"""
        }
    ]

    result = analyze_dependencies(files)

    assert result["total_dependencies"] == 1


def test_empty_repository():
    result = analyze_dependencies([])

    assert result["total_manifests"] == 0
    assert result["total_dependencies"] == 0


if __name__ == "__main__":
    test_python_dependencies()
    test_javascript_dependencies()
    test_java_dependencies()
    test_empty_repository()

    print("All dependency analyzer tests passed!")