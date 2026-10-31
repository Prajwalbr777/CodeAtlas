from backend.report_generator import generate_pdf_report


sample_data = {
    "repo_url": "https://github.com/psf/requests",

    "analysis": {
        "total_files": 130,
        "total_folders": 23,
        "language_distribution": [
            {
                "language": "Python",
                "files": 100,
                "percentage": 85
            },
            {
                "language": "Markdown",
                "files": 15,
                "percentage": 15
            }
        ]
    },

    "ecosystem_analysis": {
        "ecosystems": [
            {
                "ecosystem": "Python",
                "source_files": 100,
                "manifest_files": ["pyproject.toml"]
            }
        ]
    },

    "code_quality": {
        "summary": {
            "total_issues": 2,
            "high": 0,
            "medium": 1,
            "low": 1
        },
        "issues": [
            {
                "title": "Possible unused import",
                "severity": "Medium",
                "file": "sample.py",
                "line": 5,
                "description": "An imported module may not be used."
            },
            {
                "title": "Debug print statement",
                "severity": "Low",
                "file": "main.py",
                "line": 10,
                "description": "A print statement was detected."
            }
        ]
    },

    "dependency_analysis": {
        "total_dependencies": 2,
        "dependencies": [
            {
                "name": "requests",
                "version": "2.31.0",
                "manifest_file": "requirements.txt"
            },
            {
                "name": "urllib3",
                "version": "2.0.0",
                "manifest_file": "requirements.txt"
            }
        ],
        "manifests": []
    },

    "dependency_version_analysis": {
        "results": [
            {
                "name": "requests",
                "declared_version": "2.31.0",
                "latest_version": "2.32.0",
                "status": "Outdated"
            }
        ]
    },

    "vulnerability_analysis": {
        "total_dependencies": 2,
        "checked_dependencies": 2,
        "vulnerable_dependencies": 0,
        "no_known_vulnerabilities": 2,
        "cannot_check": 0,
        "check_failed": 0,
        "results": []
    }
}


pdf = generate_pdf_report(sample_data)

with open("CodeAtlas_Test_Report.pdf", "wb") as file:
    file.write(pdf)

print("PDF report generated successfully!")
print("File: CodeAtlas_Test_Report.pdf")
print("PDF size:", len(pdf), "bytes")