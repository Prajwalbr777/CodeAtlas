const API_URL = "http://127.0.0.1:8000";

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

        // Vulnerability analysis returned by the OSV scanner
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

        const issueItems = issues.map(issue => {

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
                    ? `<p style="margin-top: 8px;">
                        <strong>Aliases:</strong>
                        ${escapeHTML(aliases.join(", "))}
                       </p>`
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
        // FINAL DASHBOARD DISPLAY
        // ==========================================

        results.innerHTML = `

            <div class="dashboard-section">

                <h2>Repository Overview</h2>

                <div class="stats-grid">

                    <div class="stat-card">
                        <h3>${escapeHTML(analysis.total_files ?? files.length)}</h3>
                        <p>Total Files</p>
                    </div>

                    <div class="stat-card">
                        <h3>${escapeHTML(analysis.total_folders ?? folders.length)}</h3>
                        <p>Total Folders</p>
                    </div>

                    <div class="stat-card">
                        <h3>${escapeHTML(summary.total_issues ?? issues.length)}</h3>
                        <p>Code Issues</p>
                    </div>

                    <div class="stat-card">
                        <h3>${escapeHTML(dependencyAnalysis.total_dependencies ?? dependencies.length)}</h3>
                        <p>Dependencies</p>
                    </div>

                </div>

            </div>

            <div class="dashboard-section">

                <h2>Programming Languages</h2>

                ${
                    languageItems ||
                    "<p>No programming languages detected.</p>"
                }

            </div>

            <div class="dashboard-section">

                <h2>Technology Ecosystems</h2>

                ${
                    ecosystemItems ||
                    "<p>No technology ecosystems detected.</p>"
                }

            </div>

            <div class="dashboard-section">

                <h2>Code Quality Analysis</h2>

                <div class="stats-grid">

                    <div class="stat-card">
                        <h3>${escapeHTML(summary.total_issues ?? issues.length)}</h3>
                        <p>Total Issues</p>
                    </div>

                    <div class="stat-card">
                        <h3>${escapeHTML(summary.high ?? 0)}</h3>
                        <p>High Severity</p>
                    </div>

                    <div class="stat-card">
                        <h3>${escapeHTML(summary.medium ?? 0)}</h3>
                        <p>Medium Severity</p>
                    </div>

                    <div class="stat-card">
                        <h3>${escapeHTML(summary.low ?? 0)}</h3>
                        <p>Low Severity</p>
                    </div>

                </div>

                ${
                    issueItems ||
                    "<p>No code quality issues detected by the current scanner.</p>"
                }

            </div>

            <div class="dashboard-section">

                <h2>Dependency Manifest Analysis</h2>

                <p style="color: #9ca3af; margin-bottom: 15px;">
                    Detected dependency manifest files and their declared packages.
                </p>

                ${
                    manifestItems ||
                    "<p>No dependency manifest files detected.</p>"
                }

            </div>

            <div class="dashboard-section">

                <h2>Dependency Version Analysis</h2>

                ${versionSummaryHTML}

                ${
                    versionCards ||
                    "<p>No dependency version results available.</p>"
                }

                <p style="
                    color: #9ca3af;
                    font-size: 12px;
                    margin-top: 12px;
                ">
                    Version checks currently support Python and JavaScript packages
                    with exact versions. Version ranges and unsupported ecosystems
                    may not be compared.
                </p>

            </div>

            <div class="dashboard-section">

                <h2>Security Vulnerability Analysis</h2>

                <p style="color: #9ca3af; margin-bottom: 15px;">
                    Security checks are performed using the OSV vulnerability database.
                </p>

                ${vulnerabilitySummaryHTML}

                ${
                    vulnerabilityCards ||
                    "<p>No vulnerability scan results are available.</p>"
                }

                <p style="
                    color: #9ca3af;
                    font-size: 12px;
                    margin-top: 12px;
                ">
                    This scanner checks supported dependencies with exact versions.
                    No known vulnerabilities found does not guarantee that a package
                    is completely secure.
                </p>

            </div>

            <div class="dashboard-section">

                <h2>Repository Folders</h2>

                <ul>
                    ${
                        folderItems ||
                        "<li>No folders found.</li>"
                    }
                </ul>

            </div>

            <div class="dashboard-section">

                <h2>Repository Files</h2>

                <ul>
                    ${
                        fileItems ||
                        "<li>No files found.</li>"
                    }
                </ul>

            </div>

        `;

        message.textContent =
            "Repository analysis completed successfully!";

        message.style.color = "#4ade80";

    } catch (error) {

        console.error("CodeAtlas Error:", error);

        message.textContent =
            "Analysis failed: " + error.message;

        message.style.color = "#f87171";

        results.innerHTML = `
            <div class="empty-state">
                <h3>Analysis Failed</h3>
                <p>${escapeHTML(error.message)}</p>
            </div>
        `;

    } finally {

        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze Repository";

    }
}


// ==========================================
// HTML ESCAPE FUNCTION
// ==========================================

function escapeHTML(value) {

    if (value === null || value === undefined) {
        return "";
    }

    return String(value).replace(/[&<>"']/g, character => {

        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#039;"
        };

        return entities[character];

    });

}