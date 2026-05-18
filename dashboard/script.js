document.addEventListener('DOMContentLoaded', () => {
    const stateUrl = '/state';
    const logsUrl = '/logs';

    // UI Elements
    const elements = {
        reputationScore: document.getElementById('reputation-score'),
        totalEarning: document.getElementById('total-earning'),
        todayReward: document.getElementById('today-reward'),
        analysisFeed: document.getElementById('analysis-feed'),
        arcSegments: document.querySelectorAll('.arc-segment')
    };

    let lastLogCount = 0;

    /**
     * Updates the dashboard with fresh data
     */
    async function updateDashboard() {
        try {
            const response = await fetch(stateUrl);
            const data = await response.json();

            // Update Numeric Values with animation
            animateValue(elements.reputationScore, parseInt(elements.reputationScore.innerText) || 0, data.reputation_score, 1000);
            
            elements.totalEarning.innerHTML = `${data.total_earning.toLocaleString()} <span style="font-size: 1rem; opacity: 0.6;">PTS</span>`;
            elements.todayReward.innerHTML = `${data.today_reward.toLocaleString()} <span style="font-size: 1rem; opacity: 0.6;">PTS</span>`;

            // Update Arch Gauge Segments
            updateArcGauge(data.reputation_score);

        } catch (error) {
            console.warn('Backend connection pending or error:', error);
        }
    }

    /**
     * Updates the arc segments based on reputation score (0-1000)
     */
    function updateArcGauge(score) {
        const totalSegments = elements.arcSegments.length;
        const activeCount = Math.floor((score / 1000) * totalSegments);
        
        elements.arcSegments.forEach((seg, i) => {
            if (i < activeCount) {
                seg.classList.add('active');
            } else {
                seg.classList.remove('active');
            }
        });
    }

    /**
     * Adds logs to the terminal strip
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
                // Auto scroll to bottom
                elements.analysisFeed.scrollTop = elements.analysisFeed.scrollHeight;
            }
        } catch (e) {}
    }

    /**
     * Numeric animation helper
     */
    function animateValue(obj, start, end, duration) {
        if (start === end) return;
        let startTimestamp = null;
        const step = (timestamp) => {
            if (!startTimestamp) startTimestamp = timestamp;
            const progress = Math.min((timestamp - startTimestamp) / duration, 1);
            obj.innerHTML = Math.floor(progress * (end - start) + start);
            if (progress < 1) {
                window.requestAnimationFrame(step);
            }
        };
        window.requestAnimationFrame(step);
    }

    // Initialize intervals
    updateDashboard();
    setInterval(updateDashboard, 5000);
    setInterval(updateLogs, 3000);

    // Initial flair log
    setTimeout(() => {
        const line = document.createElement('div');
        line.className = 'terminal-line';
        line.innerHTML = `[${new Date().toLocaleTimeString()}] <b>SYSTEM</b> Research Engine v1.4.2 Boot Sequence... OK.`;
        elements.analysisFeed.appendChild(line);
    }, 800);
});
