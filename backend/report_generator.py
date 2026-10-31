from io import BytesIO
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)


# ==========================================
# CODEATLAS PDF REPORT GENERATOR
# ==========================================

def generate_pdf_report(report_data):
    """
    Generate a professional PDF report from CodeAtlas
    repository analysis results.

    Returns:
        bytes: Generated PDF file content.
    """

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title="CodeAtlas Repository Analysis Report",
        author="CodeAtlas"
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=23,
        leading=28,
        textColor=colors.HexColor("#172554"),
        alignment=TA_CENTER,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1D4ED8"),
        spaceBefore=15,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="SmallText",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11
    ))

    styles.add(ParagraphStyle(
        name="CellText",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
        wordWrap="CJK"
    ))

    story = []

    # ==========================================
    # HELPER FUNCTIONS
    # ==========================================

    def safe_text(value, default="Not available"):
        if value is None or value == "":
            value = default

        return escape(str(value)).replace("\n", "<br/>")

    def make_paragraph(value, style="CellText"):
        return Paragraph(safe_text(value), styles[style])

    def add_section(title):
        story.append(Paragraph(title, styles["SectionHeading"]))

    def add_table(headers, rows, widths=None):

        table_data = [
            [make_paragraph(header) for header in headers]
        ]

        for row in rows:
            table_data.append([
                make_paragraph(value) for value in row
            ])

        if len(table_data) == 1:
            table_data.append([
                make_paragraph("No data available")
                for _ in headers
            ])

        table = Table(
            table_data,
            colWidths=widths,
            repeatRows=1,
            hAlign="LEFT"
        )

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0),
             colors.HexColor("#1E3A8A")),

            ("TEXTCOLOR", (0, 0), (-1, 0),
             colors.white),

            ("FONTNAME", (0, 0), (-1, 0),
             "Helvetica-Bold"),

            ("BACKGROUND", (0, 1), (-1, -1),
             colors.HexColor("#F8FAFC")),

            ("GRID", (0, 0), (-1, -1),
             0.4, colors.HexColor("#CBD5E1")),

            ("VALIGN", (0, 0), (-1, -1), "TOP"),

            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7)
        ]))

        story.append(table)
        story.append(Spacer(1, 8))

    # ==========================================
    # EXTRACT ANALYSIS DATA
    # ==========================================

    analysis = report_data.get("analysis", {})

    ecosystem_analysis = report_data.get(
        "ecosystem_analysis", {}
    )

    code_quality = report_data.get(
        "code_quality", {}
    )

    dependency_analysis = report_data.get(
        "dependency_analysis", {}
    )

    version_analysis = report_data.get(
        "dependency_version_analysis", {}
    )

    vulnerability_analysis = report_data.get(
        "vulnerability_analysis", {}
    )

    languages = analysis.get(
        "language_distribution", []
    )

    ecosystems = ecosystem_analysis.get(
        "ecosystems", []
    )

    issues = code_quality.get("issues", [])

    manifests = dependency_analysis.get(
        "manifests", []
    )

    dependencies = dependency_analysis.get(
        "dependencies", []
    )

    version_results = version_analysis.get(
        "results", []
    )

    vulnerability_results = vulnerability_analysis.get(
        "results", []
    )

    quality_summary = code_quality.get(
        "summary", {}
    )

    # ==========================================
    # REPORT COVER / HEADER
    # ==========================================

    story.append(Spacer(1, 25))

    story.append(Paragraph(
        "CODEATLAS",
        styles["ReportTitle"]
    ))

    story.append(Paragraph(
        "Repository Analysis Report",
        styles["Heading2"]
    ))

    story.append(Spacer(1, 12))

    repository_url = (
        report_data.get("repo_url")
        or analysis.get("repo_url")
        or "Not available"
    )

    generated_date = datetime.now(
        timezone.utc
    ).strftime("%d %B %Y, %H:%M UTC")

    story.append(Paragraph(
        f"<b>Repository:</b> {safe_text(repository_url)}",
        styles["BodyText"]
    ))

    story.append(Spacer(1, 5))

    story.append(Paragraph(
        f"<b>Generated:</b> {generated_date}",
        styles["BodyText"]
    ))

    story.append(Spacer(1, 20))

    # ==========================================
    # REPOSITORY OVERVIEW
    # ==========================================

    add_section("1. Repository Overview")

    overview_rows = [
        [
            "Total Files",
            analysis.get("total_files", len(
                analysis.get("files", [])
            ))
        ],
        [
            "Total Folders",
            analysis.get("total_folders", len(
                analysis.get("folders", [])
            ))
        ],
        [
            "Total Code Issues",
            quality_summary.get(
                "total_issues", len(issues)
            )
        ],
        [
            "Total Dependencies",
            dependency_analysis.get(
                "total_dependencies", len(dependencies)
            )
        ]
    ]

    add_table(
        ["Metric", "Value"],
        overview_rows,
        [85 * mm, 85 * mm]
    )

    # ==========================================
    # PROGRAMMING LANGUAGES
    # ==========================================

    add_section("2. Programming Language Distribution")

    language_rows = []

    for language in languages:

        language_rows.append([
            language.get("language", "Unknown"),
            language.get("files", 0),
            f"{language.get('percentage', 0)}%"
        ])

    add_table(
        ["Language", "Files", "Percentage"],
        language_rows,
        [75 * mm, 45 * mm, 50 * mm]
    )

    # ==========================================
    # TECHNOLOGY ECOSYSTEMS
    # ==========================================

    add_section("3. Technology Ecosystem Analysis")

    ecosystem_rows = []

    for ecosystem in ecosystems:

        ecosystem_rows.append([
            ecosystem.get("ecosystem", "Unknown"),
            ecosystem.get("source_files", 0),
            ", ".join(
                ecosystem.get("manifest_files", [])
            ) or "None"
        ])

    add_table(
        ["Ecosystem", "Source Files", "Manifest Files"],
        ecosystem_rows,
        [45 * mm, 35 * mm, 90 * mm]
    )

    # ==========================================
    # CODE QUALITY ANALYSIS
    # ==========================================

    add_section("4. Code Quality Analysis")

    quality_rows = [
        [
            "Total Issues",
            quality_summary.get(
                "total_issues", len(issues)
            )
        ],
        [
            "High Severity",
            quality_summary.get("high", 0)
        ],
        [
            "Medium Severity",
            quality_summary.get("medium", 0)
        ],
        [
            "Low Severity",
            quality_summary.get("low", 0)
        ]
    ]

    add_table(
        ["Severity Metric", "Count"],
        quality_rows,
        [85 * mm, 85 * mm]
    )

    story.append(Paragraph(
        "<b>Detected Issues</b>",
        styles["BodyText"]
    ))

    issue_rows = []

    for issue in issues:

        issue_rows.append([
            issue.get("title", "Unknown"),
            issue.get("severity", "Unknown"),
            issue.get("file", "Unknown"),
            issue.get("line", "Unknown"),
            issue.get("description", "")
        ])

    add_table(
        [
            "Issue",
            "Severity",
            "File",
            "Line",
            "Description"
        ],
        issue_rows,
        [34 * mm, 20 * mm, 42 * mm, 15 * mm, 59 * mm]
    )

    # ==========================================
    # DEPENDENCY ANALYSIS
    # ==========================================

    add_section("5. Dependency Analysis")

    dependency_rows = []

    for dependency in dependencies:

        dependency_rows.append([
            dependency.get("name", "Unknown"),
            dependency.get("version", "Not specified"),
            dependency.get("manifest_file", "Unknown")
        ])

    add_table(
        ["Dependency", "Version", "Manifest"],
        dependency_rows,
        [55 * mm, 45 * mm, 70 * mm]
    )

    # ==========================================
    # DEPENDENCY VERSION CHECKING
    # ==========================================

    add_section("6. Dependency Version Analysis")

    version_rows = []

    for item in version_results:

        version_rows.append([
            item.get("name", "Unknown"),
            item.get("declared_version", "Unknown"),
            item.get("latest_version", "Unknown"),
            item.get("status", "Unknown")
        ])

    add_table(
        [
            "Package",
            "Declared",
            "Latest",
            "Status"
        ],
        version_rows,
        [45 * mm, 35 * mm, 35 * mm, 55 * mm]
    )

    # ==========================================
    # SECURITY VULNERABILITY ANALYSIS
    # ==========================================

    add_section("7. Security Vulnerability Analysis")

    vulnerability_summary_rows = [
        [
            "Total Dependencies",
            vulnerability_analysis.get(
                "total_dependencies", 0
            )
        ],
        [
            "Checked Dependencies",
            vulnerability_analysis.get(
                "checked_dependencies", 0
            )
        ],
        [
            "Vulnerable Dependencies",
            vulnerability_analysis.get(
                "vulnerable_dependencies", 0
            )
        ],
        [
            "No Known Vulnerabilities",
            vulnerability_analysis.get(
                "no_known_vulnerabilities", 0
            )
        ],
        [
            "Cannot Check",
            vulnerability_analysis.get(
                "cannot_check", 0
            )
        ],
        [
            "Check Failed",
            vulnerability_analysis.get(
                "check_failed", 0
            )
        ]
    ]

    add_table(
        ["Security Metric", "Count"],
        vulnerability_summary_rows,
        [85 * mm, 85 * mm]
    )

    vulnerability_rows = []

    for item in vulnerability_results:

        vulnerability_rows.append([
            item.get("name", "Unknown"),
            item.get("declared_version", "Unknown"),
            item.get("status", "Unknown"),
            item.get("vulnerability_count", 0)
        ])

    add_table(
        [
            "Package",
            "Version",
            "Status",
            "Vulnerability Count"
        ],
        vulnerability_rows,
        [45 * mm, 35 * mm, 50 * mm, 40 * mm]
    )

    # ==========================================
    # DISCLAIMER
    # ==========================================

    story.append(Spacer(1, 15))

    story.append(Paragraph(
        "<b>Disclaimer:</b> This report is generated using "
        "automated static analysis and publicly available "
        "vulnerability information. Findings may require "
        "manual verification. The absence of detected issues "
        "does not guarantee that a repository is completely secure.",
        styles["SmallText"]
    ))

    # ==========================================
    # PAGE NUMBER FOOTER
    # ==========================================

    def add_page_number(canvas, document):

        canvas.saveState()

        canvas.setFont("Helvetica", 8)

        canvas.setFillColor(
            colors.HexColor("#64748B")
        )

        canvas.drawString(
            18 * mm,
            12 * mm,
            "Generated by CodeAtlas"
        )

        canvas.drawRightString(
            A4[0] - 18 * mm,
            12 * mm,
            f"Page {document.page}"
        )

        canvas.restoreState()

    # ==========================================
    # BUILD PDF
    # ==========================================

    document.build(
        story,
        onFirstPage=add_page_number,
        onLaterPages=add_page_number
    )

    pdf_bytes = buffer.getvalue()

    buffer.close()

    return pdf_bytes