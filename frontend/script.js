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
    message.textContent = "Scanning repository and detecting languages...";
    message.style.color = "#60a5fa";

    results.innerHTML = `
        <div class="empty-state">
            <h3>Analyzing Repository...</h3>
            <p>Detecting files, folders and programming languages.</p>
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

        const analysis = data.analysis;
        const files = analysis.files || [];
        const folders = analysis.folders || [];
        const languages = analysis.language_distribution || [];

        document.getElementById("repoCount").textContent = "1";
        document.getElementById("fileCount").textContent =
            analysis.total_files ?? files.length;
        document.getElementById("issueCount").textContent = "0";

        const folderItems = folders.map(folder => `
            <li>📁 ${escapeHTML(folder)}</li>
        `).join("");

        const fileItems = files.map(file => `
            <li>
                📄 ${escapeHTML(file.path)}
                <span class="language-label">
                    ${escapeHTML(file.language)}
                </span>
            </li>
        `).join("");

        const languageItems = languages.map(language => `
            <div class="language-card">
                <div class="language-info">
                    <strong>${escapeHTML(language.language)}</strong>
                    <span>${language.files} files (${language.percentage}%)</span>
                </div>
                <div class="language-bar">
                    <div class="language-progress"
                         style="width: ${Math.min(100, Math.max(0, Number(language.percentage) || 0))}%">
                    </div>
                </div>
            </div>
        `).join("");

        results.innerHTML = `
            <div class="repo-details">
                <h3>Repository Analysis Successful!</h3>

                <p><strong>Repository:</strong>
                    ${escapeHTML(analysis.repository)}
                </p>

                <p><strong>Owner:</strong>
                    ${escapeHTML(analysis.owner)}
                </p>

                <p><strong>Total Files:</strong>
                    ${analysis.total_files}
                </p>

                <p><strong>Total Folders:</strong>
                    ${analysis.total_folders}
                </p>

                <div class="file-list">
                    <h3>Programming Language Detection</h3>
                    ${languageItems || "<p>No languages detected.</p>"}
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
            "Repository scan and language detection completed successfully!";
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

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => {
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