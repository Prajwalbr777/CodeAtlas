from backend.code_quality_scanner import (
    scan_source_code,
    summarize_issues,
    analyze_source_files
)


# Sample Python code containing intentional issues
sample_code = """
password = "mysecretpassword123"

result = eval(user_input)

exec(user_code)

print("Debugging application")

# TODO: Complete authentication

# FIXME: Fix input validation

import pdb
pdb.set_trace()
"""


print("===================================")
print("       CODEATLAS SCANNER TEST")
print("===================================")


# Test 1: Scan individual source code
issues = scan_source_code(
    "sample.py",
    sample_code,
    "Python"
)

print("\nTEST 1: Individual File Scan")

for issue in issues:
    print(
        f"\n[{issue['severity']}] {issue['title']}"
    )
    print(f"File: {issue['file']}")
    print(f"Line: {issue['line']}")
    print(f"Description: {issue['description']}")


# Test 2: Generate issue summary
summary = summarize_issues(issues)

print("\nTEST 2: Issue Summary")
print("Total Issues:", summary["total_issues"])
print("High:", summary["high"])
print("Medium:", summary["medium"])
print("Low:", summary["low"])


# Test 3: Scan multiple files
sample_files = [
    {
        "path": "sample.py",
        "language": "Python",
        "content": sample_code
    },
    {
        "path": "app.js",
        "language": "JavaScript",
        "content": """
console.log("Debug message");
eval(userInput);
"""
    }
]

result = analyze_source_files(sample_files)

print("\nTEST 3: Multiple File Scan")
print("Total Issues:", result["summary"]["total_issues"])

print("\n===================================")
print("       TESTING COMPLETED")
print("===================================")