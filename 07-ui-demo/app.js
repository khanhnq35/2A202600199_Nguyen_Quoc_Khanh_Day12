const API_BASE = "http://localhost:8080";

// --- State Management ---
let token = localStorage.getItem("agent_token");

const elements = {
    loginOverlay: document.getElementById("login-overlay"),
    loginForm: document.getElementById("login-form"),
    loginMsg: document.getElementById("login-msg"),
    chatHistory: document.getElementById("chat-history"),
    chatInput: document.getElementById("chat-input"),
    sendBtn: document.getElementById("send-btn"),
    instanceDisplay: document.getElementById("instance-id"),
    costDisplay: document.getElementById("cost-display"),
    userRole: document.getElementById("user-role"),
    statusText: document.getElementById("status-text"),
    logoutBtn: document.getElementById("logout-btn")
};

// --- Initialization ---
function init() {
    if (token) {
        elements.loginOverlay.style.display = "none";
        updateStatus("Online", "#4ade80");
        fetchMetrics();
    } else {
        updateStatus("Unauthorized", "#f87171");
    }
}

function updateStatus(text, color) {
    elements.statusText.innerText = text;
    document.getElementById("status-dot").style.background = color;
}

// --- Auth logic ---
elements.loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    elements.loginMsg.innerText = "Authenticating...";
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: e.target.username.value,
                password: e.target.password.value
            })
        });

        if (!response.ok) throw new Error("Invalid credentials");

        const data = await response.json();
        token = data.access_token;
        localStorage.setItem("agent_token", token);
        
        elements.loginOverlay.style.display = "none";
        updateStatus("Online", "#4ade80");
        appendMessage("bot", "Access granted! I am ready to assist you.");
        fetchMetrics();
    } catch (err) {
        elements.loginMsg.innerText = err.message;
    }
});

elements.logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("agent_token");
    location.reload();
});

// --- Chat logic ---
async function sendMessage() {
    const text = elements.chatInput.value.trim();
    if (!text) return;

    // Add user msg to UI
    appendMessage("user", text);
    elements.chatInput.value = "";

    try {
        const response = await fetch(`${API_BASE}/ask`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ question: text })
        });

        if (response.status === 401) {
            appendMessage("bot", "Session expired. Please login again.");
            return;
        }

        const data = await response.json();
        appendMessage("bot", data.answer);
        
        // Update Instance Monitor
        elements.instanceDisplay.innerText = data.instance;
        elements.instanceDisplay.parentElement.classList.add("pulse-fast");
        setTimeout(() => elements.instanceDisplay.parentElement.classList.remove("pulse-fast"), 1000);

    } catch (err) {
        appendMessage("bot", "Error: Backend unreachable. Make sure Docker is running.");
    }
}

function appendMessage(role, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role}`;
    msgDiv.innerText = text;
    elements.chatHistory.appendChild(msgDiv);
    elements.chatHistory.scrollTop = elements.chatHistory.scrollHeight;
}

async function fetchMetrics() {
    try {
        // Simple call to root to get version/instance
        const res = await fetch(`${API_BASE}/`);
        const data = await res.json();
        elements.instanceDisplay.innerText = data.instance;
    } catch (e) {}
}

elements.sendBtn.addEventListener("click", sendMessage);
elements.chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
});

init();
