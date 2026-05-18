document.addEventListener('DOMContentLoaded', () => {
    const stateUrl = '/state';
    const logsUrl = '/logs';

    // UI Elements
    const elements = {
        reputationScore: document.getElementById('reputation-score'),
        totalEarning: document.getElementById('total-earning'),
        todayReward: document.getElementById('today-reward'),
        cpuLoad: document.getElementById('cpu-load'),
        storageUsed: document.getElementById('storage-used'),
        analysisFeed: document.getElementById('analysis-feed'),
        volumeChart: document.getElementById('volume-chart')
    };

    let lastLogCount = 0;

    /**
     * Updates the dashboard with fresh data
     */
    async function updateDashboard() {
        try {
            const response = await fetch(stateUrl);
            const data = await response.json();

            // 1. Core Metrics with Animation
            animateValue(elements.reputationScore, parseInt(elements.reputationScore.innerText) || 0, data.reputation_score, 1000);
            
            elements.totalEarning.innerText = data.total_earning.toLocaleString();
            elements.todayReward.innerText = data.today_reward.toLocaleString();
            elements.cpuLoad.innerText = data.cpu_load;
            elements.storageUsed.innerText = data.storage_used;

            // 2. Volume Chart
            updateVolumeChart(data.volume_history);

        } catch (error) {
            console.warn('Sync error:', error);
        }
    }

    /**
     * Renders bars for the volume chart
     */
    function updateVolumeChart(history) {
        if (!elements.volumeChart || !history) return;
        elements.volumeChart.innerHTML = '';
        history.forEach((val, i) => {
            const bar = document.createElement('div');
            bar.className = 'chart-bar';
            if (i === history.length - 1) bar.classList.add('active');
            bar.style.height = `${val}%`;
            elements.volumeChart.appendChild(bar);
        });
    }

    /**
     * Streams logs to the terminal
     */
    async function updateLogs() {
        try {
            const response = await fetch(logsUrl);
            const logs = await response.json();

            if (logs.length > lastLogCount) {
                logs.slice(lastLogCount).forEach(log => {
                    const line = document.createElement('div');
                    line.className = 'term-line';
                    const time = log.timestamp || new Date().toLocaleTimeString();
                    const msg = log.message || log;
                    line.innerHTML = `
                        <span class="term-time">[${time}]</span>
                        <span class="term-tag">RESEARCH</span>
                        <span class="term-msg">${msg}</span>
                    `;
                    elements.analysisFeed.appendChild(line);
                });
                lastLogCount = logs.length;
                elements.analysisFeed.scrollTop = elements.analysisFeed.scrollHeight;
            }
        } catch (e) {}
    }

    /**
     * Animation utility
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
     * Actions
     */
    window.copyApiHook = () => {
        const url = window.location.origin + '/trigger-run';
        navigator.clipboard.writeText(url).then(() => {
            showToast('API Trigger Hook Copied!');
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
            setTimeout(() => toast.remove(), 400);
        }, 3000);
    }

    // Init
    updateDashboard();
    setInterval(updateDashboard, 5000);
    setInterval(updateLogs, 3000);
    
    // Initial sequence
    setTimeout(() => {
        const line = document.createElement('div');
        line.className = 'term-line';
        line.innerHTML = `<span class="term-time">[${new Date().toLocaleTimeString()}]</span> <span class="term-tag">SYSTEM</span> <span class="term-msg">SAP v1.4.2 Active. System Healthy.</span>`;
        elements.analysisFeed.appendChild(line);
    }, 1000);
});
