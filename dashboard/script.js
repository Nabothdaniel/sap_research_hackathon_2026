// dashboard/script.js

/**
 * SAP Research Agent Dashboard Logic
 * Handles real-time updates from the FastAPI bridge and UI animations.
 */

// Use relative path for production (Render) - handle cases where / is or is not at root
const API_BASE = window.location.origin; 
const STATE_URL = API_BASE.includes('localhost') ? `${API_BASE}/state` : '/state';

// --- UI State Management ---

const updateUI = (data) => {
    window.hasRealData = true;

    // Update Scores
    const scoreMiniEl = document.getElementById('autonomy-score-mini');
    const score = data.reputation_score || 98.4;
    if (scoreMiniEl) scoreMiniEl.textContent = score;

    // Update Earnings
    const earningEl = document.getElementById('epoch-earning');
    if (earningEl) earningEl.innerHTML = `${(data.total_earning || 850).toFixed(0)} <span>PTS</span>`;

    const rewardEl = document.getElementById('today-reward');
    if (rewardEl) rewardEl.innerHTML = `${(data.today_reward || 12).toFixed(1)} <span>PTS</span>`;

    // Update Autonomous Volume
    const volText = document.getElementById('volume-text');
    if (volText) {
        const vol = (data.total_earning || 850);
        volText.textContent = `${vol.toFixed(0)}/1000`;
    }

    // --- Live Research Feed Logic ---
    if (data.last_run && data.last_run.tasks) {
        const feed = document.getElementById('analysis-feed');
        if (feed) {
            // Clear placeholder on first real data
            if (feed.querySelector('.placeholder')) feed.innerHTML = '';
            
            // Add new tasks that aren't already in the feed
            data.last_run.tasks.forEach(task => {
                const taskId = `task-${task.task_id.substring(0, 8)}`;
                if (!document.getElementById(taskId)) {
                    const item = document.createElement('div');
                    item.id = taskId;
                    item.className = 'feed-item';
                    item.innerHTML = `
                        <h4><i data-lucide="search"></i> ${task.topic}</h4>
                        <p>${task.summary.substring(0, 150)}...</p>
                        <div class="analysis-meta">
                            <span class="tag-sentiment">Sentiment: ${task.sentiment}</span>
                            <span>Task ID: ${task.task_id.substring(0, 8)}</span>
                        </div>
                    `;
                    feed.prepend(item);
                    if (window.lucide) lucide.createIcons();
                }
            });
        }
    }
};

// --- Real-time Polling ---

const fetchLatestState = async () => {
    try {
        const response = await fetch(STATE_URL);
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();
        updateUI(data);
    } catch (error) {
        console.warn('Dashboard bridge not online. Running in demo mode.');
        // Fallback to random micro-animations for demo
        simulateActivity();
    }
};

const simulateActivity = () => {
    // Randomize bar chart heights
    const bars = document.querySelectorAll('.bar');
    bars.forEach(bar => {
        const currentHeight = parseInt(bar.style.height) || 50;
        const drift = Math.floor(Math.random() * 10) - 5;
        const newHeight = Math.min(Math.max(currentHeight + drift, 20), 90);
        bar.style.height = `${newHeight}%`;
    });

    // Pulse the score slightly
    const scoreEl = document.getElementById('autonomy-score');
    if (scoreEl && !window.hasRealData) {
        const drift = (Math.random() * 0.1) - 0.05;
        const currentScore = parseFloat(scoreEl.textContent);
        scoreEl.textContent = (currentScore + drift).toFixed(1);
    }

    // Update "Tool Load" circle progress
    const toolLoadCircle = document.querySelectorAll('svg path')[7]; // Target Tool Load path
    if (toolLoadCircle) {
        const load = 40 + Math.floor(Math.random() * 15);
        toolLoadCircle.setAttribute('stroke-dasharray', `${load}, 100`);
        const loadText = document.querySelectorAll('.percent')[1].firstChild;
        if (loadText) loadText.textContent = `${load}%`;
    }
};

// --- Initialization ---

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // Start polling or simulation
    setInterval(fetchLatestState, 5000);
    
    // Initial call
    fetchLatestState();

    // Copy Referral Code Action
    const copyBtn = document.querySelector('.btn-copy');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const originalText = copyBtn.textContent;
            copyBtn.textContent = 'Copied!';
            setTimeout(() => copyBtn.textContent = originalText, 2000);
        });
    }

    console.log("SAP Dashboard Initialized.");
});
