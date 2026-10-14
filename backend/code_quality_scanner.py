import re


# ============================================================
# CODEATLAS - SMART CODE QUALITY SCANNER
# Heuristic static analysis. Findings require human review.
# ============================================================


# Common placeholder values that should not be reported as secrets.
SECRET_PLACEHOLDERS = {
    "config",
    "secret_key",
    "your_api_key",
    "your_password",
    "your_token",
    "replace_me",
    "example",
    "placeholder",
    "changeme",
    "xxxxxxxx",
    "your_secret",
    "test",
    "dummy",
    "sample",
    "none",
    "null",
    "undefined"
}


# Secret detection pattern.
SECRET_PATTERN = re.compile(
    r"""(?i)\b(api_key|apikey|secret_key|password|passwd|access_token|auth_token)\b\s*[:=]\s*["']([^"']+)["']"""
)


SECURITY_RULES = [
    {
        "id": "HARDCODED_SECRET",
        "title": "Possible Hardcoded Secret",
        "severity": "High",
        "pattern": SECRET_PATTERN,
        "description": (
            "A variable may contain a hardcoded password, "
            "token, or secret. Review the value carefully."
        )
    },
    {
        "id": "PYTHON_EVAL",
        "title": "Use of eval()",
        "severity": "High",
        "pattern": re.compile(r"\beval\s*\("),
        "languages": ["Python"],
        "description": (
            "eval() executes dynamically supplied expressions "
            "and can be dangerous with untrusted input."
        )
    },
    {
        "id": "PYTHON_EXEC",
        "title": "Use of exec()",
        "severity": "High",
        "pattern": re.compile(r"\bexec\s*\("),
        "languages": ["Python"],
        "description": (
            "exec() executes dynamically supplied code "
            "and should be carefully reviewed."
        )
    },
    {
        "id": "JS_EVAL",
        "title": "JavaScript eval()",
        "severity": "High",
        "pattern": re.compile(r"\beval\s*\("),
        "languages": ["JavaScript", "TypeScript"],
        "description": (
            "JavaScript eval() can execute dynamically supplied code."
        )
    },
    {
        "id": "SHELL_TRUE",
        "title": "Subprocess with shell=True",
        "severity": "High",
        "pattern": re.compile(r"\bshell\s*=\s*True\b"),
        "languages": ["Python"],
        "description": (
            "Using shell=True with untrusted input can introduce "
            "command injection risks."
        )
    },
    {
        "id": "DEBUGGER",
        "title": "Debugger Statement",
        "severity": "Low",
        "pattern": re.compile(
            r"\bdebugger\s*;?|\bpdb\.set_trace\s*\(\s*\)"
        ),
        "description": (
            "A debugger statement may have been left in the source code."
        )
    },
    {
        "id": "TODO",
        "title": "Unfinished TODO",
        "severity": "Low",
        "pattern": re.compile(r"\bTODO\b", re.IGNORECASE),
        "description": (
            "A TODO comment indicates work that may still be unfinished."
        )
    },
    {
        "id": "FIXME",
        "title": "Unresolved FIXME",
        "severity": "Medium",
        "pattern": re.compile(r"\bFIXME\b", re.IGNORECASE),
        "description": (
            "A FIXME comment indicates a known problem "
            "that may need attention."
        )
    }
]


DEBUG_RULES = [
    {
        "id": "PYTHON_PRINT",
        "title": "Print Statement",
        "severity": "Low",
        "pattern": re.compile(r"^\s*print\s*\("),
        "languages": ["Python"],
        "description": (
            "A print statement may be leftover debugging code."
        )
    },
    {
        "id": "JS_CONSOLE_LOG",
        "title": "Console Log",
        "severity": "Low",
        "pattern": re.compile(r"\bconsole\.log\s*\("),
        "languages": ["JavaScript", "TypeScript"],
        "description": (
            "A console.log statement may be leftover debugging code."
        )
    }
]


ALL_RULES = SECURITY_RULES + DEBUG_RULES


# ------------------------------------------------------------
# Remove comments and mask string literals for code-only rules.
# Keep a separate version containing strings for secret detection.
# ------------------------------------------------------------

def clean_source_line(line, language, in_block_comment=False):
    code_with_strings = []
    code_without_strings = []
    comments = []

    quote = None
    escaped = False
    triple_quote = False

    index = 0
    length = len(line)

    python_language = language == "Python"

    hash_comments = language in [
        "Python", "Shell", "PowerShell", "R"
    ]

    slash_comments = language in [
        "JavaScript", "TypeScript", "Java", "C",
        "C++", "C#", "Go", "Rust", "Swift", "Kotlin"
    ]

    sql_comments = language == "SQL"

    while index < length:

        char = line[index]
        next_two = line[index:index + 2]
        next_three = line[index:index + 3]

        # Continue an existing multiline block comment.
        if in_block_comment:
            if next_two == "*/":
                in_block_comment = False
                index += 2
            else:
                comments.append(char)
                index += 1
            continue

        # Continue an existing multiline string.
        if quote is not None:
            code_with_strings.append(char)
            code_without_strings.append(" ")

            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif triple_quote and next_three == quote * 3:
                code_with_strings.extend([" ", " "])
                code_without_strings.extend([" ", " "])
                index += 2
                quote = None
                triple_quote = False
            elif not triple_quote and char == quote:
                quote = None

            index += 1
            continue

        # Start a string literal.
        if python_language and next_three in ('"""', "'''"):
            quote = line[index]
            triple_quote = True
            code_with_strings.extend([" ", " ", " "])
            code_without_strings.extend([" ", " ", " "])
            index += 3
            continue

        if char in ('"', "'"):
            quote = char
            code_with_strings.append(char)
            code_without_strings.append(" ")
            index += 1
            continue

        # Start a block comment.
        if slash_comments and next_two == "/*":
            in_block_comment = True
            index += 2
            continue

        # Start a single-line comment.
        if hash_comments and char == "#":
            comments.append(line[index:])
            break

        if slash_comments and next_two == "//":
            comments.append(line[index:])
            break

        if sql_comments and next_two == "--":
            comments.append(line[index:])
            break

        code_with_strings.append(char)
        code_without_strings.append(char)

        index += 1

    return (
        "".join(code_with_strings),
        "".join(code_without_strings),
        "".join(comments),
        in_block_comment
    )


# ------------------------------------------------------------
# Check whether a potential secret looks like a real value.
# ------------------------------------------------------------

def is_possible_secret(match):
    value = match.group(2).strip()

    lowered_value = value.lower()

    if lowered_value in SECRET_PLACEHOLDERS:
        return False

    if any(
        placeholder in lowered_value
        for placeholder in SECRET_PLACEHOLDERS
    ):
        return False

    # Very short values are usually configuration labels.
    if len(value) < 8:
        return False

    # Require a mixture of letters and digits.
    has_letter = bool(re.search(r"[a-zA-Z]", value))
    has_digit = bool(re.search(r"\d", value))

    if not (has_letter and has_digit):
        return False

    return True


# ------------------------------------------------------------
# Scan one source file.
# ------------------------------------------------------------

def scan_source_code(file_path, source_code, language):
    """
    Scan one source file and return potential code issues.
    """

    issues = []

    if not isinstance(source_code, str):
        return issues

    lines = source_code.splitlines()

    in_block_comment = False

    for line_number, line in enumerate(lines, start=1):

        if not line.strip():
            continue

        (
            code_with_strings,
            code_without_strings,
            comments,
            in_block_comment
        ) = clean_source_line(
            line,
            language,
            in_block_comment
        )

        findings = []

        for rule in ALL_RULES:

            rule_id = rule["id"]

            supported_languages = rule.get("languages")

            if (
                supported_languages
                and language not in supported_languages
            ):
                continue

            # Secret detection needs string values.
            if rule_id == "HARDCODED_SECRET":

                for match in rule["pattern"].finditer(
                    code_with_strings
                ):
                    if is_possible_secret(match):
                        findings.append((rule, match))

            # TODO and FIXME should only be detected in comments.
            elif rule_id in ["TODO", "FIXME"]:

                if not comments:
                    continue

                for match in rule["pattern"].finditer(comments):
                    findings.append((rule, match))

            # Other rules should only inspect executable code.
            else:

                if not code_without_strings.strip():
                    continue

                match = rule["pattern"].search(
                    code_without_strings
                )

                if match:
                    findings.append((rule, match))

        # Prevent duplicate rule findings on the same line.
        reported_rules = set()

        for rule, match in findings:

            if rule["id"] in reported_rules:
                continue

            reported_rules.add(rule["id"])

            issues.append({
                "rule_id": rule["id"],
                "title": rule["title"],
                "severity": rule["severity"],
                "file": file_path,
                "line": line_number,
                "language": language,
                "description": rule["description"],
                "code": line.strip()[:200]
            })

    return issues


# ------------------------------------------------------------
# Generate severity summary.
# ------------------------------------------------------------

def summarize_issues(issues):
    """
    Generate issue counts by severity.
    """

    summary = {
        "total_issues": len(issues),
        "high": 0,
        "medium": 0,
        "low": 0
    }

    for issue in issues:

        severity = issue.get("severity", "").lower()

        if severity in summary:
            summary[severity] += 1

    return summary


# ------------------------------------------------------------
# Analyze multiple source files.
# ------------------------------------------------------------

def analyze_source_files(files):
    """
    Scan a collection of source files.

    Each file must contain:
    path, content, and language.
    """

    all_issues = []

    for file in files:

        file_path = file.get("path", "")
        source_code = file.get("content", "")
        language = file.get("language", "Other")

        if not source_code:
            continue

        issues = scan_source_code(
            file_path,
            source_code,
            language
        )

        all_issues.extend(issues)

    return {
        "summary": summarize_issues(all_issues),
        "issues": all_issues
    }