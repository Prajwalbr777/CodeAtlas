import re
import ast


# ============================================================
# CODEATLAS - ADVANCED CODE QUALITY SCANNER
# Heuristic static analysis. Findings require human review.
# ============================================================


SECRET_PLACEHOLDERS = {
    "config", "secret_key", "your_api_key", "your_password",
    "your_token", "replace_me", "example", "placeholder",
    "changeme", "xxxxxxxx", "your_secret", "test", "dummy",
    "sample", "none", "null", "undefined"
}


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
            "A variable may contain a hardcoded password, token, "
            "or secret. Review the value carefully."
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


# ============================================================
# CLEAN SOURCE CODE
# ============================================================

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

        if in_block_comment:

            if next_two == "*/":
                in_block_comment = False
                index += 2
            else:
                comments.append(char)
                index += 1

            continue

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

        if slash_comments and next_two == "/*":

            in_block_comment = True
            index += 2
            continue

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


# ============================================================
# SECRET DETECTION
# ============================================================

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

    if len(value) < 8:
        return False

    has_letter = bool(re.search(r"[a-zA-Z]", value))
    has_digit = bool(re.search(r"\d", value))

    return has_letter and has_digit


# ============================================================
# PYTHON UNUSED IMPORT AND VARIABLE DETECTION
# ============================================================

def scan_python_unused_items(file_path, source_code):

    issues = []

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return issues

    loaded_names = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.Name) and isinstance(
            node.ctx, ast.Load
        ):
            loaded_names.add(node.id)

    source_lines = source_code.splitlines()
    reported_imports = set()

    # Check unused imports.
    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for alias in node.names:

                name = alias.asname or alias.name.split(".")[0]

                if (
                    name not in loaded_names
                    and name not in reported_imports
                    and not name.startswith("_")
                ):

                    reported_imports.add(name)

                    issues.append({
                        "rule_id": "UNUSED_IMPORT",
                        "title": "Possibly Unused Import",
                        "severity": "Low",
                        "file": file_path,
                        "line": node.lineno,
                        "language": "Python",
                        "description": (
                            f"The imported name '{name}' does not appear "
                            "to be used in this file."
                        ),
                        "code": source_lines[
                            node.lineno - 1
                        ].strip()[:200]
                    })

        elif isinstance(node, ast.ImportFrom):

            if node.module == "__future__":
                continue

            for alias in node.names:

                if alias.name == "*":
                    continue

                name = alias.asname or alias.name

                if (
                    name not in loaded_names
                    and name not in reported_imports
                    and not name.startswith("_")
                ):

                    reported_imports.add(name)

                    issues.append({
                        "rule_id": "UNUSED_IMPORT",
                        "title": "Possibly Unused Import",
                        "severity": "Low",
                        "file": file_path,
                        "line": node.lineno,
                        "language": "Python",
                        "description": (
                            f"The imported name '{name}' does not appear "
                            "to be used in this file."
                        ),
                        "code": source_lines[
                            node.lineno - 1
                        ].strip()[:200]
                    })

    # Check possibly unused variables.
    reported_variables = set()

    for node in ast.walk(tree):

        target_names = []

        if isinstance(node, ast.Assign):

            for target in node.targets:
                target_names.extend(get_assigned_names(target))

        elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)):

            target_names.extend(get_assigned_names(node.target))

        for name, line_number in target_names:

            if (
                name not in loaded_names
                and name not in reported_variables
                and not name.startswith("_")
            ):

                reported_variables.add(name)

                code_line = (
                    source_lines[line_number - 1].strip()[:200]
                    if 0 < line_number <= len(source_lines)
                    else ""
                )

                issues.append({
                    "rule_id": "UNUSED_VARIABLE",
                    "title": "Possibly Unused Variable",
                    "severity": "Low",
                    "file": file_path,
                    "line": line_number,
                    "language": "Python",
                    "description": (
                        f"The variable '{name}' is assigned a value "
                        "but does not appear to be used."
                    ),
                    "code": code_line
                })

    return issues


def get_assigned_names(target):

    names = []

    if isinstance(target, ast.Name):
        names.append((target.id, target.lineno))

    elif isinstance(target, (ast.Tuple, ast.List)):

        for element in target.elts:
            names.extend(get_assigned_names(element))

    return names


# ============================================================
# SCAN ONE SOURCE FILE
# ============================================================

def scan_source_code(file_path, source_code, language):

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

            if rule_id == "HARDCODED_SECRET":

                for match in rule["pattern"].finditer(code_with_strings):

                    if is_possible_secret(match):
                        findings.append(rule)

            elif rule_id in ["TODO", "FIXME"]:

                if comments and rule["pattern"].search(comments):
                    findings.append(rule)

            else:

                if not code_without_strings.strip():
                    continue

                if rule["pattern"].search(code_without_strings):
                    findings.append(rule)

        reported_rules = set()

        for rule in findings:

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

    # Additional Python-specific checks.
    if language == "Python":

        issues.extend(
            scan_python_unused_items(file_path, source_code)
        )

    return issues


# ============================================================
# FAST DUPLICATE CODE DETECTION
# ============================================================

def find_duplicate_code(files, minimum_lines=4):

    issues = []

    # Dictionary allows fast lookup of previously seen blocks.
    seen_blocks = {}

    for file in files:

        file_path = file.get("path", "")
        source_code = file.get("content", "")
        language = file.get("language", "Other")

        if not isinstance(source_code, str) or not source_code.strip():
            continue

        normalized_lines = []
        original_line_numbers = []

        in_block_comment = False

        for line_number, line in enumerate(
            source_code.splitlines(), start=1
        ):

            if not line.strip():
                continue

            (
                _,
                code_without_strings,
                _,
                in_block_comment
            ) = clean_source_line(
                line,
                language,
                in_block_comment
            )

            normalized = re.sub(
                r"\s+",
                "",
                code_without_strings
            )

            if len(normalized) < 5:
                continue

            normalized_lines.append(normalized)
            original_line_numbers.append(line_number)

        if len(normalized_lines) < minimum_lines:
            continue

        # Examine each consecutive block in this file.
        for start in range(
            len(normalized_lines) - minimum_lines + 1
        ):

            block = tuple(
                normalized_lines[
                    start:start + minimum_lines
                ]
            )

            first_occurrence = seen_blocks.get(block)

            # First time this block is seen.
            if first_occurrence is None:

                seen_blocks[block] = {
                    "path": file_path,
                    "line": original_line_numbers[start]
                }

                continue

            # Do not report repeated blocks from the same file.
            if first_occurrence["path"] == file_path:
                continue

            # Report a duplicate across different files.
            issues.append({
                "rule_id": "DUPLICATE_CODE",
                "title": "Possible Duplicate Code",
                "severity": "Medium",
                "file": file_path,
                "line": original_line_numbers[start],
                "language": "Multiple",
                "description": (
                    "A block of code appears to be repeated "
                    f"in '{first_occurrence['path']}' and "
                    f"'{file_path}'. Consider reusing a function "
                    "or shared component."
                ),
                "code": (
                    f"Similar code found in "
                    f"{first_occurrence['path']} and {file_path}."
                )
            })

            # Mark this block as already reported.
            # This avoids repeatedly reporting the same block.
            seen_blocks[block] = {
                "path": file_path,
                "line": original_line_numbers[start],
                "reported": True
            }

    return issues


# ============================================================
# GENERATE ISSUE SUMMARY
# ============================================================

def summarize_issues(issues):

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


# ============================================================
# ANALYZE MULTIPLE SOURCE FILES
# ============================================================

def analyze_source_files(files):

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

    # Check for repeated code across different files.
    all_issues.extend(
        find_duplicate_code(files)
    )

    return {
        "summary": summarize_issues(all_issues),
        "issues": all_issues
    }