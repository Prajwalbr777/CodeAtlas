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
        "Scanning repository, ecosystems, code quality and dependencies...";

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

                    <h4 style="margin-bottom: 12px;">
                        📦 ${escapeHTML(manifest.manifest_file)}
                    </h4>

                    <p style="
                        color: #9ca3af;
                        margin-bottom: 12px;
                    ">
                        Dependencies found:

                        <strong style="color: #4ade80;">
                            ${escapeHTML(
                                manifest.dependency_count ??
                                manifestDependencies.length
                            )}
                        </strong>
                    </p>

                    ${dependencyTableHTML}

                </div>
            `;
        }).join("");

        // ==========================================
        // COMPLETE DEPENDENCY LIST
        // ==========================================

        const allDependencyItems =
            dependencies.map(dependency => {

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

                        <td style="
                            padding: 10px;
                            border-bottom: 1px solid #374151;
                        ">
                            ${escapeHTML(
                                dependency.manifest_file || "Unknown"
                            )}
                        </td>

                    </tr>
                `;
            }).join("");

        let completeDependencyHTML;

        if (allDependencyItems) {
            completeDependencyHTML = `
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

                                <th style="padding: 10px;">
                                    Manifest File
                                </th>
                            </tr>
                        </thead>

                        <tbody>
                            ${allDependencyItems}
                        </tbody>

                    </table>

                </div>
            `;
        } else {
            completeDependencyHTML = `
                <p>No dependencies were extracted.</p>
            `;
        }

        // ==========================================
        // DEPENDENCY ANALYSIS SUMMARY
        // ==========================================

        const dependencyManifestHTML =
            manifestItems ||
            "<p>No supported dependency manifests were found.</p>";

        const dependencySummaryHTML = `
            <div style="
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                margin: 15px 0;
            ">

                <div style="
                    background: #123047;
                    padding: 14px;
                    border-radius: 8px;
                ">
                    <strong style="color: #38bdf8;">
                        Manifests Scanned
                    </strong>

                    <h2>
                        ${escapeHTML(
                            dependencyAnalysis.scanned_manifests ?? 0
                        )}
                    </h2>
                </div>

                <div style="
                    background: #123b2d;
                    padding: 14px;
                    border-radius: 8px;
                ">
                    <strong style="color: #4ade80;">
                        Total Dependencies
                    </strong>

                    <h2>
                        ${escapeHTML(
                            dependencyAnalysis.total_dependencies ?? 0
                        )}
                    </h2>
                </div>

                <div style="
                    background: #3d321b;
                    padding: 14px;
                    border-radius: 8px;
                ">
                    <strong style="color: #fbbf24;">
                        Skipped Manifests
                    </strong>

                    <h2>
                        ${escapeHTML(
                            dependencyAnalysis.skipped_manifests ?? 0
                        )}
                    </h2>
                </div>

            </div>
        `;

        // ==========================================
        // CODE QUALITY SUMMARY
        // ==========================================

        const qualitySummaryHTML = `
            <div style="
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                margin: 15px 0;
            ">

                <div style="
                    background: #3b1f27;
                    padding: 12px;
                    border-radius: 8px;
                ">
                    <strong style="color: #f87171;">
                        High
                    </strong>

                    <h2>${escapeHTML(summary.high ?? 0)}</h2>
                </div>

                <div style="
                    background: #3d321b;
                    padding: 12px;
                    border-radius: 8px;
                ">
                    <strong style="color: #fbbf24;">
                        Medium
                    </strong>

                    <h2>${escapeHTML(summary.medium ?? 0)}</h2>
                </div>

                <div style="
                    background: #1e344b;
                    padding: 12px;
                    border-radius: 8px;
                ">
                    <strong style="color: #60a5fa;">
                        Low
                    </strong>

                    <h2>${escapeHTML(summary.low ?? 0)}</h2>
                </div>

            </div>
        `;

        const issueHTML =
            issueItems ||
            `
                <p>
                    No potential issues were detected
                    by the current scanning rules.
                </p>
            `;

        // ==========================================
        // FINAL DASHBOARD HTML
        // ==========================================

        results.innerHTML = `

    <div class="repo-details">

        <h3>Repository Analysis Successful!</h3>

        <p>
            <strong>Repository:</strong>
            ${escapeHTML(analysis.repository)}
        </p>

        <p>
            <strong>Owner:</strong>
            ${escapeHTML(analysis.owner)}
        </p>

        <p>
            <strong>Total Files:</strong>
            ${escapeHTML(analysis.total_files)}
        </p>

        <p>
            <strong>Total Folders:</strong>
            ${escapeHTML(analysis.total_folders)}
        </p>

        <!-- PROGRAMMING LANGUAGES -->

        <div class="file-list">

            <h3>Programming Language Detection</h3>

            ${languageItems || "<p>No languages detected.</p>"}

        </div>

        <!-- ECOSYSTEM ANALYSIS -->

        <div class="file-list">

            <h3>Technology Ecosystem Analysis</h3>

            <p>
                <strong>Total Ecosystems Detected:</strong>
                ${escapeHTML(
                    ecosystemAnalysis.total_ecosystems ?? 0
                )}
            </p>

            ${ecosystemItems ||
                "<p>No technology ecosystems were detected.</p>"}

        </div>

        <!-- DEPENDENCY ANALYSIS -->

        <div class="file-list">

            <h3>Dependency Analysis</h3>

            ${dependencySummaryHTML}

            <h3>Dependency Manifest Files</h3>

            ${dependencyManifestHTML}

            <h3 style="margin-top: 20px;">
                Complete Dependency List
            </h3>

            ${completeDependencyHTML}

            <p style="
                margin-top: 15px;
                color: #9ca3af;
                font-size: 13px;
            ">
                Note: This analysis extracts declared dependencies
                and their version requirements. It does not yet
                verify the latest versions or known vulnerabilities.
            </p>

        </div>

        <!-- CODE QUALITY ANALYSIS -->

        <div class="file-list">

            <h3>Code Quality Analysis</h3>

            <p>
                <strong>Source Files Scanned:</strong>
                ${escapeHTML(quality.scanned_source_files ?? 0)}
            </p>

            <p>
                <strong>Files Skipped:</strong>
                ${escapeHTML(quality.skipped_files ?? 0)}
            </p>

            <p>
                <strong>Total Potential Issues:</strong>
                ${escapeHTML(
                    summary.total_issues ?? issues.length
                )}
            </p>

            ${qualitySummaryHTML}

            <h3>Detected Issues</h3>

            ${issueHTML}

        </div>

        <!-- REPOSITORY FOLDERS -->

        <div class="file-list">

            <h3>Repository Folders</h3>

            <ul>
                ${folderItems || "<li>No folders found.</li>"}
            </ul>

        </div>

        <!-- REPOSITORY FILES -->

        <div class="file-list">

            <h3>Repository Files</h3>

            <ul>
                ${fileItems || "<li>No files found.</li>"}
            </ul>

        </div>

    </div>
`;

// ==========================================
// SUCCESS MESSAGE
// ==========================================

message.textContent =
    "Repository, ecosystem, code quality and dependency analysis completed successfully!";

message.style.color = "#4ade80";

} catch (error) {

    // ERROR HANDLING

    message.textContent = error.message;
    message.style.color = "#f87171";

    results.innerHTML = `
        <div class="empty-state">
            <h3>Analysis Failed</h3>
            <p>${escapeHTML(error.message)}</p>
        </div>
    `;

} finally {

    // RESTORE ANALYZE BUTTON

    analyzeBtn.disabled = false;
    analyzeBtn.textContent = "Analyze Repository →";

}

}


// ==========================================
// HTML ESCAPE FUNCTION
// ==========================================

function escapeHTML(value) {

    return String(value ?? "").replace(/[&<>"']/g, character => {

        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[character];

    });

}
            