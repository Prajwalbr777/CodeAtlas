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
    message.textContent = "Scanning repository files and folders...";
    message.style.color = "#60a5fa";

    results.innerHTML = `
        <div class="empty-state">
            <h3>Scanning Repository...</h3>
            <p>Discovering files and nested folders. Please wait.</p>
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

        document.getElementById("repoCount").textContent = "1";
        document.getElementById("fileCount").textContent =
            analysis.total_files ?? files.length;
        document.getElementById("issueCount").textContent = "0";

        const folderItems = folders.map(folder => `
            <li>
                📁 ${escapeHTML(folder)}
            </li>
        `).join("");

        const fileItems = files.map(file => `
            <li>
                📄 ${escapeHTML(file.path)}
            </li>
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
                    <h3>Repository Folders</h3>
                    <ul>
                        ${folderItems || "<li>No folders found.</li>"}
                    </ul>

                    <h3>Repository Files</h3>
                    <ul>
                        ${fileItems || "<li>No files found.</li>"}
                    </ul>
                </div>
            </div>
        `;

        message.textContent =
            "Recursive repository scan completed successfully!";
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