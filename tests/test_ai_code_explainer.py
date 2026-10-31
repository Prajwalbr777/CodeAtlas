from backend.ai_code_explainer import explain_code_issue
import json

issue = {
    "title": "Possible Hardcoded Secret",
    "severity": "High",
    "description": "A variable may contain a hardcoded password or secret.",
    "file": "sample.py",
    "code": 'password = "mysecretpassword123"'
}

result = explain_code_issue(issue)

print(json.dumps(result, indent=2))