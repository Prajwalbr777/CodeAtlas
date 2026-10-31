const API_URL = "http://127.0.0.1:8000";
let lastAnalysisData = null;

// ==========================================
// MAIN REPOSITORY ANALYSIS FUNCTION
// ==========================================

async function analyzeRepository() {
    const repoInput = document.getElementById("repoUrl");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const message = document.getElementById("message");
    const results = document.getElementById("results");

    const repoUrl = repoInput.value.trim();

    if (!repoUrl) {
        message.textContent = "Please enter a GitHub repository URL.";
        message.style.color = "#f87171";
        return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";

    message.textContent =
        "Scanning repository, code quality, dependencies and security...";

    message.style.color = "#60a5fa";

    results.innerHTML = `
        <div class="empty-state">
            <h3>Analyzing Repository...</h3>
            <p>Detecting files, languages, ecosystems, potential code issues and dependencies.</p>
        </div>
    `;

    try {
        const response = await fetch(`${API_URL}/analyze`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                repo_url: repoUrl
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Repository analysis failed."
            );
        }

        // Save complete analysis data for PDF generation.
        lastAnalysisData = data;

        // ==========================================
        // EXTRACT BACKEND RESPONSE DATA
        // ==========================================

        const analysis = data.analysis || {};

        const files = analysis.files || [];
        const folders = analysis.folders || [];
        const languages = analysis.language_distribution || [];

        const ecosystemAnalysis = data.ecosystem_analysis || {};
        const ecosystems = ecosystemAnalysis.ecosystems || [];

        const quality = data.code_quality || {};
        const summary = quality.summary || {};
        const issues = quality.issues || [];

        const dependencyAnalysis = data.dependency_analysis || {};
        const manifests = dependencyAnalysis.manifests || [];
        const dependencies = dependencyAnalysis.dependencies || [];

        const vulnerabilityAnalysis = data.vulnerability_analysis || {};
        const vulnerabilityResults = vulnerabilityAnalysis.results || [];

        // ==========================================
        // UPDATE DASHBOARD STATISTICS
        // ==========================================

        document.getElementById("repoCount").textContent = "1";

        document.getElementById("fileCount").textContent =
            analysis.total_files ?? files.length;

        document.getElementById("issueCount").textContent =
            summary.total_issues ?? issues.length;

        // ==========================================
        // REPOSITORY FOLDERS
        // ==========================================

        const folderItems = folders.map(folder => {
            return `<li>📁 ${escapeHTML(folder)}</li>`;
        }).join("");

        // ==========================================
        // REPOSITORY FILES
        // ==========================================

        const fileItems = files.map(file => {
            return `
                <li>
                    📄 ${escapeHTML(file.path)}
                    <span class="language-label">
                        ${escapeHTML(file.language)}
                    </span>
                </li>
            `;
        }).join("");

        // ==========================================
        // PROGRAMMING LANGUAGE DISTRIBUTION
        // ==========================================

        const languageItems = languages.map(language => {
            const percentage = Math.min(
                100,
                Math.max(0, Number(language.percentage) || 0)
            );

            return `
                <div class="language-card">

                    <div class="language-info">
                        <strong>${escapeHTML(language.language)}</strong>

                        <span>
                            ${escapeHTML(language.files)} files
                            (${escapeHTML(language.percentage)}%)
                        </span>
                    </div>

                    <div class="language-bar">
                        <div
                            class="language-progress"
                            style="width: ${percentage}%">
                        </div>
                    </div>

                </div>
            `;
        }).join("");

        // ==========================================
        // TECHNOLOGY ECOSYSTEM ANALYSIS
        // ==========================================

        const ecosystemItems = ecosystems.map(ecosystem => {

            const ecosystemManifestItems =
                (ecosystem.manifest_files || []).map(file => {
                    return `<li>📄 ${escapeHTML(file)}</li>`;
                }).join("");

            const ecosystemManifestHTML =
                ecosystemManifestItems ||
                "<li>No manifest files detected.</li>";

            return `
                <div class="issue-card"
                    style="
                        border: 1px solid #374151;
                        border-left: 4px solid #a78bfa;
                        padding: 15px;
                        margin-bottom: 12px;
                        border-radius: 8px;
                        background: #1f2937;
                    ">

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        gap: 10px;
                        flex-wrap: wrap;
                    ">

                        <strong style="font-size: 17px;">
                            ${escapeHTML(ecosystem.ecosystem)}
                        </strong>

                        <span style="
                            color: #4ade80;
                            font-weight: bold;
                            font-size: 12px;
                        ">
                            DETECTED
                        </span>

                    </div>

                    <p style="margin-top: 12px;">
                        <strong>Source Files:</strong>
                        ${escapeHTML(ecosystem.source_files ?? 0)}
                    </p>

                    <div style="margin-top: 10px;">
                        <strong>Manifest Files:</strong>

                        <ul style="
                            margin-top: 8px;
                            padding-left: 20px;
                            color: #cbd5e1;
                        ">
                            ${ecosystemManifestHTML}
                        </ul>
                    </div>

                </div>
            `;
        }).join("");

        // ==========================================
        // CODE QUALITY ANALYSIS
        // ==========================================

        window.codeAtlasIssues = issues;

        const issueItems = issues.map((issue, index) => {

            const severity = String(
                issue.severity || "low"
            ).toLowerCase();

            const severityColors = {
                high: "#f87171",
                medium: "#fbbf24",
                low: "#60a5fa"
            };

            const color =
                severityColors[severity] || "#60a5fa";

            return `
                <div class="issue-card"
                    style="
                        border: 1px solid #374151;
                        border-left: 4px solid ${color};
                        padding: 15px;
                        margin-bottom: 12px;
                        border-radius: 8px;
                        background: #1f2937;
                    ">

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        gap: 10px;
                        flex-wrap: wrap;
                    ">

                        <strong>
                            ${escapeHTML(issue.title)}
                        </strong>

                        <span style="
                            color: ${color};
                            font-weight: bold;
                            text-transform: uppercase;
                            font-size: 12px;
                        ">
                            ${escapeHTML(severity)}
                        </span>

                    </div>

                    <p style="margin-top: 10px;">
                        ${escapeHTML(issue.description)}
                    </p>

                    <p style="
                        font-size: 13px;
                        color: #9ca3af;
                    ">
                        📄 ${escapeHTML(issue.file)}
                        &nbsp; | &nbsp;
                        Line: ${escapeHTML(issue.line)}
                        &nbsp; | &nbsp;
                        Language: ${escapeHTML(issue.language)}
                    </p>

                    <p style="
                        font-size: 13px;
                        color: #d1d5db;
                        background: #111827;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-wrap: anywhere;
                    ">
                        ${escapeHTML(issue.code)}
                    </p>

                    <p style="
                        font-size: 12px;
                        color: #9ca3af;
                    ">
                        Rule ID: ${escapeHTML(issue.rule_id)}
                    </p>

                    <button
                        type="button"
                        onclick="explainIssue(${index}, this)"
                        style="
                            background: #7c3aed;
                            color: white;
                            border: none;
                            padding: 9px 14px;
                            border-radius: 6px;
                            cursor: pointer;
                            font-weight: 600;
                            margin-top: 8px;
                        "
                    >
                        Explain with AI
                    </button>

                    <div
                        id="ai-explanation-${index}"
                        style="
                            display: none;
                            margin-top: 14px;
                            padding: 14px;
                            border: 1px solid #4c1d95;
                            border-radius: 8px;
                            background: #111827;
                            color: #e5e7eb;
                            white-space: pre-wrap;
                            overflow-wrap: anywhere;
                            line-height: 1.6;
                        "
                    ></div>

                </div>
            `;
        }).join("");

        // ==========================================
        // DEPENDENCY MANIFEST ANALYSIS
        // ==========================================

        const manifestItems = manifests.map(manifest => {

            const manifestDependencies =
                manifest.dependencies || [];

            const dependencyRows =
                manifestDependencies.map(dependency => {

                    return `
                        <tr>

                            <td style="
                                padding: 10px;
                                border-bottom: 1px solid #374151;
                            ">
                                ${escapeHTML(dependency.name)}
                            </td>

                            <td style="
                                padding: 10px;
                                border-bottom: 1px solid #374151;
                            ">
                                ${escapeHTML(
                                    dependency.version || "Not specified"
                                )}
                            </td>

                        </tr>
                    `;
                }).join("");

            let dependencyTableHTML;

            if (dependencyRows) {
                dependencyTableHTML = `
                    <div style="overflow-x: auto;">

                        <table style="
                            width: 100%;
                            border-collapse: collapse;
                            text-align: left;
                        ">

                            <thead>
                                <tr style="background: #111827;">
                                    <th style="padding: 10px;">
                                        Dependency
                                    </th>

                                    <th style="padding: 10px;">
                                        Declared Version
                                    </th>
                                </tr>
                            </thead>

                            <tbody>
                                ${dependencyRows}
                            </tbody>

                        </table>

                    </div>
                `;
            } else {
                dependencyTableHTML = `
                    <p style="color: #9ca3af;">
                        No dependencies were extracted from this manifest.
                    </p>
                `;
            }

            return `
                <div class="issue-card"
                    style="
                        border: 1px solid #374151;
                        border-left: 4px solid #38bdf8;
                        padding: 15px;
                        margin-bottom: 15px;
                        border-radius: 8px;
                        background: #1f2937;
                    ">

                    <h4>${escapeHTML(manifest.manifest_file)}</h4>

                    <p style="margin-top: 8px;">
                        Dependencies found:
                        ${escapeHTML(manifest.dependency_count ?? manifestDependencies.length)}
                    </p>

                    ${dependencyTableHTML}

                </div>
            `;
        }).join("");
                // ==========================================
        // DEPENDENCY VERSION ANALYSIS
        // ==========================================

        const versionAnalysis =
            data.dependency_version_analysis || {};

        const versionResults =
            versionAnalysis.results || [];

        const versionCards = versionResults.map(item => {

            const status = String(
                item.status || "Unknown"
            );

            let statusColor = "#9ca3af";

            if (status.toLowerCase().includes("outdated")) {
                statusColor = "#fbbf24";
            } else if (
                status.toLowerCase().includes("up to date")
            ) {
                statusColor = "#4ade80";
            }

            return `
                <div style="
                    background: #1f2937;
                    border: 1px solid #374151;
                    border-left: 4px solid ${statusColor};
                    border-radius: 8px;
                    padding: 14px;
                    margin-bottom: 10px;
                ">

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        gap: 10px;
                        flex-wrap: wrap;
                    ">

                        <strong>
                            ${escapeHTML(item.name)}
                        </strong>

                        <span style="
                            color: ${statusColor};
                            font-weight: bold;
                        ">
                            ${escapeHTML(status)}
                        </span>

                    </div>

                    <p style="margin-top: 8px;">
                        Declared version:
                        ${escapeHTML(item.declared_version || "Not specified")}
                    </p>

                    <p>
                        Latest version:
                        ${escapeHTML(item.latest_version || "Not available")}
                    </p>

                    <p style="
                        color: #9ca3af;
                        font-size: 12px;
                        margin-top: 6px;
                    ">
                        Ecosystem:
                        ${escapeHTML(item.ecosystem || "Unknown")}
                    </p>

                </div>
            `;
        }).join("");

        const versionSummaryHTML = `
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
                gap: 12px;
                margin-bottom: 18px;
            ">

                <div class="stat-card">
                    <h3>${escapeHTML(versionAnalysis.total_checked ?? 0)}</h3>
                    <p>Checked</p>
                </div>

                <div class="stat-card">
                    <h3>${escapeHTML(versionAnalysis.up_to_date ?? 0)}</h3>
                    <p>Up to Date</p>
                </div>

                <div class="stat-card">
                    <h3>${escapeHTML(versionAnalysis.outdated ?? 0)}</h3>
                    <p>Outdated</p>
                </div>

                <div class="stat-card">
                    <h3>${escapeHTML(versionAnalysis.cannot_compare ?? 0)}</h3>
                    <p>Cannot Compare</p>
                </div>

            </div>
        `;


        // ==========================================
        // VULNERABILITY ANALYSIS SUMMARY
        // ==========================================

        const vulnerabilitySummaryHTML = `
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
                gap: 12px;
                margin-bottom: 18px;
            ">

                <div class="stat-card">
                    <h3>
                        ${escapeHTML(
                            vulnerabilityAnalysis.total_dependencies ?? 0
                        )}
                    </h3>
                    <p>Total Dependencies</p>
                </div>

                <div class="stat-card">
                    <h3>
                        ${escapeHTML(
                            vulnerabilityAnalysis.checked_dependencies ?? 0
                        )}
                    </h3>
                    <p>Checked</p>
                </div>

                <div class="stat-card">
                    <h3 style="color: #f87171;">
                        ${escapeHTML(
                            vulnerabilityAnalysis.vulnerable_dependencies ?? 0
                        )}
                    </h3>
                    <p>Vulnerable</p>
                </div>

                <div class="stat-card">
                    <h3 style="color: #4ade80;">
                        ${escapeHTML(
                            vulnerabilityAnalysis.no_known_vulnerabilities ?? 0
                        )}
                    </h3>
                    <p>No Known Issues</p>
                </div>

                <div class="stat-card">
                    <h3>
                        ${escapeHTML(
                            vulnerabilityAnalysis.cannot_check ?? 0
                        )}
                    </h3>
                    <p>Cannot Check</p>
                </div>

                <div class="stat-card">
                    <h3>
                        ${escapeHTML(
                            vulnerabilityAnalysis.check_failed ?? 0
                        )}
                    </h3>
                    <p>Check Failed</p>
                </div>

            </div>
        `;


        // ==========================================
        // VULNERABILITY DETAILS
        // ==========================================

        const vulnerabilityCards = vulnerabilityResults.map(item => {

            const isVulnerable =
                item.status === "Vulnerable";

            const isSafe =
                item.status === "No known vulnerabilities found";

            const statusColor = isVulnerable
                ? "#f87171"
                : isSafe
                    ? "#4ade80"
                    : "#fbbf24";

            const vulnerabilityDetails =
                item.vulnerabilities || [];

            const detailCards = vulnerabilityDetails.map(vulnerability => {

                const aliases =
                    vulnerability.aliases || [];

                const references =
                    vulnerability.references || [];

                const aliasHTML = aliases.length
                    ? `
                        <p style="margin-top: 8px;">
                            <strong>Aliases:</strong>
                            ${escapeHTML(aliases.join(", "))}
                        </p>
                    `
                    : "";

                const referenceHTML = references.length
                    ? `
                        <div style="margin-top: 8px;">
                            <strong>References:</strong>

                            <ul style="padding-left: 20px;">
                                ${references.slice(0, 5).map(reference => `
                                    <li>
                                        <a
                                            href="${escapeHTML(reference)}"
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            style="color: #60a5fa;"
                                        >
                                            ${escapeHTML(reference)}
                                        </a>
                                    </li>
                                `).join("")}
                            </ul>
                        </div>
                    `
                    : "";

                return `
                    <div style="
                        background: #111827;
                        border: 1px solid #374151;
                        padding: 12px;
                        margin-top: 10px;
                        border-radius: 6px;
                    ">

                        <strong style="color: #fca5a5;">
                            ${escapeHTML(vulnerability.id || "Unknown ID")}
                        </strong>

                        <p style="margin-top: 8px;">
                            ${escapeHTML(
                                vulnerability.summary ||
                                "No summary available."
                            )}
                        </p>

                        ${vulnerability.severity ? `
                            <p style="margin-top: 8px;">
                                <strong>Severity:</strong>
                                ${escapeHTML(vulnerability.severity)}
                            </p>
                        ` : ""}

                        ${aliasHTML}

                        ${referenceHTML}

                    </div>
                `;
            }).join("");

            return `
                <div style="
                    background: #1f2937;
                    border: 1px solid #374151;
                    border-left: 4px solid ${statusColor};
                    padding: 15px;
                    margin-bottom: 14px;
                    border-radius: 8px;
                ">

                    <div style="
                        display: flex;
                        justify-content: space-between;
                        gap: 10px;
                        flex-wrap: wrap;
                    ">

                        <strong style="font-size: 16px;">
                            ${escapeHTML(item.name || "Unknown Package")}
                        </strong>

                        <span style="
                            color: ${statusColor};
                            font-weight: bold;
                        ">
                            ${escapeHTML(item.status || "Unknown")}
                        </span>

                    </div>

                    <p style="margin-top: 10px;">
                        <strong>Version:</strong>
                        ${escapeHTML(item.declared_version || "Not specified")}
                    </p>

                    <p>
                        <strong>Ecosystem:</strong>
                        ${escapeHTML(item.ecosystem || "Unknown")}
                    </p>

                    <p>
                        <strong>Vulnerability Count:</strong>
                        ${escapeHTML(item.vulnerability_count ?? vulnerabilityDetails.length)}
                    </p>

                    ${
                        detailCards ||
                        `<p style="
                            color: #9ca3af;
                            margin-top: 10px;
                        ">
                            ${
                                isSafe
                                    ? "No known vulnerabilities were found for this checked version."
                                    : "No additional vulnerability details are available."
                            }
                        </p>`
                    }

                </div>
            `;
        }).join("");
                // ==========================================
        // PREPARE DASHBOARD HTML
        // ==========================================

        const foldersHTML = folderItems
            ? `<ul>${folderItems}</ul>`
            : "<p>No folders found.</p>";

        const filesHTML = fileItems
            ? `<ul>${fileItems}</ul>`
            : "<p>No files found.</p>";

        const languagesHTML = languageItems
            ? languageItems
            : "<p>No programming languages detected.</p>";

        const ecosystemsHTML = ecosystemItems
            ? ecosystemItems
            : "<p>No technology ecosystems detected.</p>";

        const codeQualityHTML = issueItems
            ? issueItems
            : "<p>No code quality findings detected.</p>";

        const dependencyHTML = manifestItems
            ? manifestItems
            : "<p>No dependency manifests detected.</p>";

        const versionHTML = `
            ${versionSummaryHTML}
            ${
                versionCards ||
                "<p>No dependency version information available.</p>"
            }
        `;

        const vulnerabilityHTML = `
            ${vulnerabilitySummaryHTML}
            ${
                vulnerabilityCards ||
                "<p>No vulnerability information available.</p>"
            }
        `;


        // ==========================================
        // FINAL DASHBOARD DISPLAY
        // ==========================================

        results.innerHTML = `
            <div class="results-header">
                <div>
                    <h2>Repository Analysis Complete</h2>
                    <p>Your repository has been successfully analyzed.</p>
                </div>
            </div>

            <div style="
                display: flex;
                justify-content: flex-end;
                margin-bottom: 20px;
            ">
                <button
                    type="button"
                    onclick="downloadPDFReport(this)"
                    style="
                        background: linear-gradient(135deg, #2563eb, #4f46e5);
                        color: white;
                        border: none;
                        padding: 12px 20px;
                        border-radius: 8px;
                        font-weight: 600;
                        cursor: pointer;
                        font-size: 14px;
                    "
                >
                    📄 Download PDF Report
                </button>
            </div>

            <!-- REPOSITORY OVERVIEW -->

            <section class="result-section">
                <h3>Repository Overview</h3>

                <div class="overview-grid">

                    <div class="overview-card">
                        <span>Repository</span>
                        <strong>
                            ${escapeHTML(
                                analysis.repository_name ||
                                analysis.name ||
                                repoUrl.split("/").slice(-1)[0] ||
                                "GitHub Repository"
                            )}
                        </strong>
                    </div>

                    <div class="overview-card">
                        <span>Total Files</span>
                        <strong>
                            ${analysis.total_files ?? files.length}
                        </strong>
                    </div>

                    <div class="overview-card">
                        <span>Total Folders</span>
                        <strong>
                            ${analysis.total_folders ?? folders.length}
                        </strong>
                    </div>

                    <div class="overview-card">
                        <span>Languages</span>
                        <strong>
                            ${languages.length}
                        </strong>
                    </div>

                </div>
            </section>


            <!-- REPOSITORY STRUCTURE -->

            <section class="result-section">
                <h3>Repository Structure</h3>

                <div class="result-card">

                    <h4>Folders</h4>
                    ${foldersHTML}

                    <h4 style="margin-top: 20px;">Files</h4>
                    ${filesHTML}

                </div>
            </section>


            <!-- PROGRAMMING LANGUAGES -->

            <section class="result-section">
                <h3>Programming Languages</h3>

                <div class="result-card">
                    ${languagesHTML}
                </div>
            </section>


            <!-- TECHNOLOGY ECOSYSTEMS -->

            <section class="result-section">
                <h3>Detected Ecosystems</h3>

                <div class="result-card">
                    ${ecosystemsHTML}
                </div>
            </section>


            <!-- CODE QUALITY -->

            <section class="result-section">
                <h3>Code Quality Analysis</h3>

                <div class="result-card">

                    <div class="overview-grid">

                        <div class="overview-card">
                            <span>Total Issues</span>
                            <strong>
                                ${summary.total_issues ?? issues.length}
                            </strong>
                        </div>

                        <div class="overview-card">
                            <span>High Severity</span>
                            <strong>
                                ${summary.high ?? 0}
                            </strong>
                        </div>

                        <div class="overview-card">
                            <span>Medium Severity</span>
                            <strong>
                                ${summary.medium ?? 0}
                            </strong>
                        </div>

                        <div class="overview-card">
                            <span>Low Severity</span>
                            <strong>
                                ${summary.low ?? 0}
                            </strong>
                        </div>

                    </div>

                    ${codeQualityHTML}

                </div>
            </section>


            <!-- DEPENDENCY ANALYSIS -->

            <section class="result-section">
                <h3>Dependency Analysis</h3>

                <div class="result-card">
                    ${dependencyHTML}
                </div>
            </section>


            <!-- DEPENDENCY VERSION ANALYSIS -->

            <section class="result-section">
                <h3>Dependency Version Analysis</h3>

                <div class="result-card">
                    ${versionHTML}
                </div>
            </section>


            <!-- SECURITY VULNERABILITY ANALYSIS -->

            <section class="result-section">
                <h3>Vulnerability Analysis</h3>

                <div class="result-card">
                    ${vulnerabilityHTML}
                </div>
            </section>
        `;

        message.textContent =
            "Repository analysis completed successfully.";

        message.style.color = "#4ade80";


    } catch (error) {

        console.error("Repository analysis error:", error);

        results.innerHTML = `
            <div class="error-card">
                <h3>Analysis Failed</h3>

                <p>
                    ${escapeHTML(
                        error.message || "Something went wrong."
                    )}
                </p>

                <p>
                    Please check your backend server and try again.
                </p>
            </div>
        `;

        message.textContent = "Repository analysis failed.";
        message.style.color = "#ef4444";

    } finally {

        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze Repository";

    }
}
// ==========================================
// AI CODE EXPLANATION
// ==========================================

async function explainIssue(issueIndex, button) {

    const originalText = button.textContent;

    button.disabled = true;
    button.textContent = "Generating explanation...";

    try {

        const response = await fetch(`${API_URL}/explain-issue`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                issue_index: issueIndex,
                analysis_data: lastAnalysisData
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Unable to generate AI explanation."
            );
        }

        const explanation =
            data.explanation ||
            data.result ||
            data.message ||
            "No explanation was returned.";

        const explanationBox = document.getElementById(
            `ai-explanation-${issueIndex}`
        );

        if (explanationBox) {

            explanationBox.style.display = "block";

            explanationBox.textContent = explanation;

        }

        button.textContent = "Explanation Generated";

    } catch (error) {

        console.error("AI explanation error:", error);

        alert(
            error.message ||
            "Failed to generate AI explanation."
        );

        button.textContent = originalText;

    } finally {

        button.disabled = false;

    }
}


// ==========================================
// HTML ESCAPE HELPER
// ==========================================

function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


// ==========================================
// PDF REPORT DOWNLOAD
// ==========================================

async function downloadPDFReport(button) {

    if (!lastAnalysisData) {

        alert(
            "Please analyze a GitHub repository before downloading the PDF report."
        );

        return;
    }

    const originalText = button
        ? button.textContent
        : "📄 Download PDF Report";

    if (button) {
        button.disabled = true;
        button.textContent = "Generating PDF...";
    }

    try {

        const response = await fetch(`${API_URL}/download-report`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(lastAnalysisData)
        });

        if (!response.ok) {

            let errorMessage = "PDF report generation failed.";

            try {

                const errorData = await response.json();

                errorMessage =
                    errorData.detail || errorMessage;

            } catch (error) {
                // Keep the default error message.
            }

            throw new Error(errorMessage);
        }

        const pdfBlob = await response.blob();

        const downloadUrl =
            window.URL.createObjectURL(pdfBlob);

        const downloadLink =
            document.createElement("a");

        downloadLink.href = downloadUrl;

        downloadLink.download = "CodeAtlas_Report.pdf";

        document.body.appendChild(downloadLink);

        downloadLink.click();

        downloadLink.remove();

        setTimeout(() => {
            window.URL.revokeObjectURL(downloadUrl);
        }, 1000);

        alert("PDF report downloaded successfully!");

    } catch (error) {

        console.error("PDF download error:", error);

        alert(
            error.message ||
            "Unable to download the PDF report. Please try again."
        );

    } finally {

        if (button) {

            button.disabled = false;

            button.textContent = originalText;

        }
    }
}


// Make PDF function available to dashboard button.
window.downloadPDFReport = downloadPDFReport;


// ==========================================
// DASHBOARD INTERACTIONS
// ==========================================

document.addEventListener("DOMContentLoaded", function () {

    // ======================================
    // SCROLL PROGRESS INDICATOR
    // ======================================

    const scrollProgress =
        document.getElementById("scrollProgress");

    window.addEventListener("scroll", function () {

        if (scrollProgress) {

            const scrollTop =
                document.documentElement.scrollTop ||
                document.body.scrollTop;

            const scrollHeight =
                document.documentElement.scrollHeight -
                document.documentElement.clientHeight;

            const progress = scrollHeight > 0
                ? (scrollTop / scrollHeight) * 100
                : 0;

            scrollProgress.style.width =
                progress + "%";
        }

    });


    // ======================================
    // BACK TO TOP BUTTON
    // ======================================

    const backToTop =
        document.getElementById("backToTop");

    if (backToTop) {

        window.addEventListener("scroll", function () {

            if (window.scrollY > 300) {

                backToTop.style.display = "flex";

            } else {

                backToTop.style.display = "none";

            }

        });

        backToTop.addEventListener("click", function () {

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

        });

    }


    // ======================================
    // SIDEBAR NAVIGATION
    // ======================================

    const navLinks =
        document.querySelectorAll(".main-nav a");

    navLinks.forEach(function (link) {

        link.addEventListener("click", function () {

            navLinks.forEach(function (item) {

                item.classList.remove("active");

            });

            link.classList.add("active");

        });

    });


    // ======================================
    // ENTER KEY TO ANALYZE REPOSITORY
    // ======================================

    const repoInput =
        document.getElementById("repoUrl");

    if (repoInput) {

        repoInput.addEventListener("keydown", function (event) {

            if (event.key === "Enter") {

                event.preventDefault();

                analyzeRepository();

            }

        });

    }

});


// ==========================================
// END OF CODEATLAS FRONTEND SCRIPT
// ==========================================