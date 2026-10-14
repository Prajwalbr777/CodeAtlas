const API_URL = "http://127.0.0.1:8000";


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
    message.textContent = "Scanning repository and checking code quality...";
    message.style.color = "#60a5fa";

    results.innerHTML = `
        <div class="empty-state">
            <h3>Analyzing Repository...</h3>
            <p>Detecting files, languages and potential code issues.</p>
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
            throw new Error(data.detail || "Repository analysis failed.");
        }

        // Repository analysis data
        const analysis = data.analysis || {};
        const files = analysis.files || [];
        const folders = analysis.folders || [];
        const languages = analysis.language_distribution || [];

        // Code quality analysis data
        const quality = data.code_quality || {};
        const summary = quality.summary || {};

        const issues = quality.issues || [];

        // Update dashboard statistics
        document.getElementById("repoCount").textContent = "1";

        document.getElementById("fileCount").textContent =
            analysis.total_files ?? files.length;

        document.getElementById("issueCount").textContent =
            summary.total_issues ?? issues.length;


        // Repository folders
        const folderItems = folders.map(folder => `
            <li>📁 ${escapeHTML(folder)}</li>
        `).join("");


        // Repository files
        const fileItems = files.map(file => `
            <li>
                📄 ${escapeHTML(file.path)}
                <span class="language-label">
                    ${escapeHTML(file.language)}
                </span>
            </li>
        `).join("");


        // Programming language distribution
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
                        <div class="language-progress"
                             style="width: ${percentage}%">
                        </div>
                    </div>
                </div>
            `;
        }).join("");


        // Code quality issue cards
        const issueItems = issues.map(issue => {
            const severity = String(issue.severity || "low").toLowerCase();

            const severityColor = {
                high: "#f87171",
                medium: "#fbbf24",
                low: "#60a5fa"
            };

            const color = severityColor[severity] || "#60a5fa";

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
                        <strong>${escapeHTML(issue.title)}</strong>

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

                    <p style="font-size: 13px; color: #9ca3af;">
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

                    <p style="font-size: 12px; color: #9ca3af;">
                        Rule ID: ${escapeHTML(issue.rule_id)}
                    </p>
                </div>
            `;
        }).join("");


        // Complete dashboard results
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


                <div class="file-list">
                    <h3>Programming Language Detection</h3>

                    ${languageItems || "<p>No languages detected.</p>"}
                </div>


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
                        ${escapeHTML(summary.total_issues ?? issues.length)}
                    </p>

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

                    <h3>Detected Issues</h3>

                    ${issueItems || `
                        <p>
                            No potential issues were detected
                            by the current scanning rules.
                        </p>
                    `}
                </div>


                <div class="file-list">
                    <h3>Repository Folders</h3>

                    <ul>
                        ${folderItems || "<li>No folders found.</li>"}
                    </ul>
                </div>


                <div class="file-list">
                    <h3>Repository Files</h3>

                    <ul>
                        ${fileItems || "<li>No files found.</li>"}
                    </ul>
                </div>

            </div>
        `;

        message.textContent =
            "Repository and code quality analysis completed successfully!";

        message.style.color = "#4ade80";

    } catch (error) {

        message.textContent = error.message;
        message.style.color = "#f87171";

        results.innerHTML = `
            <div class="empty-state">
                <h3>Analysis Failed</h3>
                <p>${escapeHTML(error.message)}</p>
            </div>
        `;

    } finally {

        analyzeBtn.disabled = false;
        analyzeBtn.textContent = "Analyze Repository →";

    }
}


// Prevent HTML injection when displaying repository data
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