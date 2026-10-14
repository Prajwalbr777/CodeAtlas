// CodeAtlas - Frontend JavaScript

const API_URL = "http://127.0.0.1:8000";

// Analyze GitHub Repository
async function analyzeRepository() {

    const repoInput = document.getElementById("repoUrl");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const message = document.getElementById("message");
    const results = document.getElementById("results");

    const repoUrl = repoInput.value.trim();

    // Check empty input
    if (!repoUrl) {
        message.textContent = "Please enter a GitHub repository URL.";
        message.style.color = "#f87171";
        return;
    }

    // Show loading state
    analyzeBtn.disabled = true;
    analyzeBtn.textContent = "Analyzing...";
    message.textContent = "Connecting to GitHub. Please wait...";
    message.style.color = "#60a5fa";

    results.innerHTML = `
        <div class="empty-state">
            <h3>Analyzing Repository...</h3>
            <p>Fetching repository files from GitHub.</p>
        </div>
    `;

    try {

        // Send request to FastAPI
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

        // Handle API errors
        if (!response.ok) {
            throw new Error(data.detail || "Repository analysis failed.");
        }

        // Get analysis information
        const analysis = data.analysis;
        const files = analysis.files || [];

        // Update statistics
        document.getElementById("repoCount").textContent = "1";
        document.getElementById("fileCount").textContent = files.length;
        document.getElementById("issueCount").textContent = "0";

        // Create file list safely
        const fileItems = files.map(file => `
            <li>
                ${file.type === "dir" ? "📁" : "📄"}
                ${escapeHTML(file.path)}
            </li>
        `).join("");

        // Display results
        results.innerHTML = `
            <div class="repo-details">
                <h3>Repository Analysis Successful!</h3>

                <p><strong>Repository:</strong>
                    ${escapeHTML(analysis.repository)}
                </p>

                <p><strong>Owner:</strong>
                    ${escapeHTML(analysis.owner)}
                </p>

                <p><strong>Total root items:</strong>
                    ${files.length}
                </p>

                <div class="file-list">
                    <h3>Repository Files & Folders</h3>
                    <ul>
                        ${fileItems || "<li>No files found.</li>"}
                    </ul>
                </div>
            </div>
        `;

        message.textContent = "Repository analyzed successfully!";
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


// Escape HTML to safely display GitHub file names
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