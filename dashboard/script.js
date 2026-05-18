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

    // 1. Update Segmented Gauge (713 -> segments)
    const score = data.reputation_score || 713;
    const scoreEl = document.getElementById('autonomy-score');
    if (scoreEl) scoreEl.textContent = score;

    const segments = document.querySelectorAll('.gauge-segment');
    const activeCount = Math.floor((score / 1000) * segments.length);
    segments.forEach((seg, i) => {
        if (i < activeCount) seg.classList.add('active');
        else seg.classList.remove('active');
    });

    // 2. Update Balance & Earnings
    const balancePill = document.querySelector('.action-pill span strong');
    if (balancePill) balancePill.textContent = `${(data.total_earning * 1.5 || 2250).toFixed(0)} points`;

    const epochEarning = document.getElementById('epoch-earning');
    if (epochEarning) epochEarning.innerHTML = `${(data.total_earning || 350).toFixed(0)} <span style="font-size: 1rem; opacity: 0.5;">points</span>`;

    const todayReward = document.getElementById('today-reward');
    if (todayReward) todayReward.innerHTML = `${(data.today_reward || 50).toFixed(0)} <span style="font-size: 1rem; opacity: 0.5;">points</span>`;

    // 3. Update Research Capacity (The Circle)
    const vol = (data.total_earning || 850);
    const volText = document.getElementById('volume-text');
    if (volText) volText.textContent = `${vol.toFixed(0)}/1000 tx used`;

    const progressCircle = document.querySelector('.progress-circle');
    if (progressCircle) {
        const percent = Math.min((vol / 1000) * 100, 100);
        progressCircle.textContent = `${percent.toFixed(0)}%`;
        progressCircle.style.borderTopColor = '#818cf8';
    }

    // 4. Live Research Feed (The Engine's Soul)
    if (data.last_run && data.last_run.tasks) {
        const feed = document.getElementById('analysis-feed');
        if (feed) {
            if (feed.querySelector('.placeholder')) feed.innerHTML = '';
            
            data.last_run.tasks.forEach(task => {
                const taskId = `task-${task.task_id.substring(0, 8)}`;
                if (!document.getElementById(taskId)) {
                    const item = document.createElement('div');
                    item.id = taskId;
                    item.className = 'feed-item';
                    item.style.marginBottom = '12px';
                    item.innerHTML = `
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <strong style="color: #4f46e5; font-size: 0.85rem;">${task.topic}</strong>
                            <span style="font-size: 0.7rem; color: #10b981; font-weight: 700;">Verified</span>
                        </div>
                        <p style="font-size: 0.75rem; color: #64748b; line-height: 1.4;">${task.summary.substring(0, 120)}...</p>
                    `;
                    feed.prepend(item);
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
