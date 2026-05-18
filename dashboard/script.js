document.addEventListener('DOMContentLoaded', () => {
    const stateUrl = '/state';
    const logsUrl = '/logs';

    // UI Elements
    const elements = {
        agentId: document.getElementById('agent-id-mini'),
        reputationScore: document.getElementById('reputation-score'),
        totalEarning: document.getElementById('total-earning'),
        todayReward: document.getElementById('today-reward'),
        balance: document.getElementById('balance-val'),
        referrals: document.getElementById('referral-val'),
        rank: document.getElementById('rank-val'),
        storageText: document.getElementById('storage-val'),
        cpuText: document.getElementById('cpu-val'),
        analysisFeed: document.getElementById('analysis-feed'),
        arcSegments: document.querySelectorAll('.arc-segment'),
        barChart: document.querySelector('.bar-chart')
    };

    let lastLogCount = 0;

    /**
     * Updates the dashboard with fresh data
     */
    async function updateDashboard() {
        try {
            const response = await fetch(stateUrl);
            const data = await response.json();

            // 1. Top Bar & Header
            if (elements.agentId) elements.agentId.innerText = `ID: ${data.agent_id}`;
            if (elements.balance) elements.balance.innerText = `${data.balance.toLocaleString()} PTS`;
            if (elements.referrals) elements.referrals.innerText = data.referrals;
            if (elements.rank) elements.rank.innerText = data.rank;

            // 2. Core Stats with animation
            animateValue(elements.reputationScore, parseInt(elements.reputationScore.innerText) || 0, data.reputation_score, 1000);
            elements.totalEarning.innerHTML = `${data.total_earning.toLocaleString()} <span style="font-size: 1rem; opacity: 0.6;">PTS</span>`;
            elements.todayReward.innerHTML = `${data.today_reward.toLocaleString()} <span style="font-size: 1rem; opacity: 0.6;">PTS</span>`;

            // 3. Infrastructure stats
            if (elements.storageText) elements.storageText.innerText = `${data.storage_used}MB / ${data.storage_total}MB`;
            if (elements.cpuText) elements.cpuText.innerText = `${data.cpu_load}% Load`;

            // 4. Update Gauges & Charts
            updateArcGauge(data.reputation_score);
            updateVolumeChart(data.volume_history);

        } catch (error) {
            console.warn('Dashboard sync error:', error);
        }
    }

    /**
     * Dynamically builds the bar chart based on history
     */
    function updateVolumeChart(history) {
        if (!elements.barChart || !history) return;
        
        // Clear and rebuild bars
        elements.barChart.innerHTML = '';
        history.forEach((val, i) => {
            const bar = document.createElement('div');
            bar.className = 'chart-bar';
            // Highlight the most recent activity
            if (i === history.length - 1) bar.classList.add('active');
            else if (val > 70) bar.classList.add('highlight');
            
            bar.style.height = `${val}%`;
            elements.barChart.appendChild(bar);
        });
    }

    /**
     * Updates arc segments (0-1000 range)
     */
    function updateArcGauge(score) {
        const totalSegments = elements.arcSegments.length;
        const activeCount = Math.floor((score / 1000) * totalSegments);
        elements.arcSegments.forEach((seg, i) => {
            if (i < activeCount) seg.classList.add('active');
            else seg.classList.remove('active');
        });
    }

    /**
     * Streams logs to the terminal terminal-strip
     */
    async function updateLogs() {
        try {
            const response = await fetch(logsUrl);
            const logs = await response.json();

            if (logs.length > lastLogCount) {
                logs.slice(lastLogCount).forEach(log => {
                    const line = document.createElement('div');
                    line.className = 'terminal-line';
                    const time = log.timestamp || new Date().toLocaleTimeString();
                    const msg = log.message || log;
                    line.innerHTML = `[${time}] <b>DATA</b> ${msg}`;
                    elements.analysisFeed.appendChild(line);
                });
                lastLogCount = logs.length;
                elements.analysisFeed.scrollTop = elements.analysisFeed.scrollHeight;
            }
        } catch (e) {}
    }

    /**
     * Animation helper
     */
    function animateValue(obj, start, end, duration) {
        if (!obj || start === end) return;
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) window.requestAnimationFrame(step);
        };
        window.requestAnimationFrame(step);
    }

    /**
     * UI Interactions
     */
    window.copyApiHook = () => {
        const url = window.location.origin + '/trigger-run';
        navigator.clipboard.writeText(url).then(() => {
            showToast('API Hook Copied to Clipboard!');
        });
    };

    function showToast(msg) {
        const toast = document.createElement('div');
        toast.className = 'toast-msg';
        toast.innerText = msg;
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Init
    updateDashboard();
    setInterval(updateDashboard, 5000);
    setInterval(updateLogs, 3000);
});
