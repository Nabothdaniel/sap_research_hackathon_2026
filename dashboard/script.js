document.addEventListener('DOMContentLoaded', () => {
    const stateUrl = '/state';
    const logsUrl = '/logs';

    // UI Elements
    const elements = {
        reputationScore: document.getElementById('reputation-score'),
        totalEarning: document.getElementById('total-earning'),
        todayReward: document.getElementById('today-reward'),
        balance: document.getElementById('balance-val'),
        rank: document.getElementById('rank-val'),
        cpuLoad: document.getElementById('cpu-load'),
        cpuBar: document.getElementById('cpu-bar'),
        storageUsed: document.getElementById('storage-used'),
        storageBar: document.getElementById('storage-bar'),
        analysisFeed: document.getElementById('analysis-feed'),
        volumeChart: document.getElementById('volume-chart'),
        transactionList: document.getElementById('transaction-list')
    };

    let lastLogCount = 0;

    /**
     * Updates the dashboard with fresh data
     */
    async function updateDashboard() {
        try {
            const response = await fetch(stateUrl);
            const data = await response.json();

            // 1. High-Impact Metrics
            if (elements.reputationScore) animateValue(elements.reputationScore, parseInt(elements.reputationScore.innerText) || 0, data.reputation_score, 1000);
            
            elements.totalEarning.innerText = data.total_earning.toLocaleString();
            elements.todayReward.innerText = data.today_reward.toLocaleString();
            elements.balance.innerText = `${data.balance.toLocaleString()} PTS`;
            if (elements.rank) elements.rank.innerText = data.rank;

            // 2. Hardware Progress Bars (Dramatic)
            elements.cpuLoad.innerText = data.cpu_load;
            elements.cpuBar.style.width = `${data.cpu_load}%`;
            
            elements.storageUsed.innerText = data.storage_used;
            const storagePercent = (data.storage_used / data.storage_total) * 100;
            elements.storageBar.style.width = `${storagePercent}%`;

            // 3. Analytics & Ledger
            updateVolumeChart(data.volume_history);
            updateTransactionList(data.volume_transactions);

        } catch (error) {
            console.warn('Sync error:', error);
        }
    }

    /**
     * Renders professional research transactions
     */
    function updateTransactionList(transactions) {
        if (!elements.transactionList || !transactions) return;
        elements.transactionList.innerHTML = '';
        transactions.forEach(tx => {
            const item = document.createElement('div');
            item.className = 'ledger-item';
            item.innerHTML = `
                <div>
                    <div class="ledger-topic">${tx.topic}</div>
                    <div class="ledger-meta">${tx.time} • SAP PROTOCOL v1.4</div>
                </div>
                <div class="ledger-value">+${tx.bounty} PTS</div>
            `;
            elements.transactionList.appendChild(item);
        });
    }

    /**
     * Renders dramatic bar chart
     */
    function updateVolumeChart(history) {
        if (!elements.volumeChart || !history) return;
        elements.volumeChart.innerHTML = '';
        history.forEach((val, i) => {
            const bar = document.createElement('div');
            bar.className = 'bar';
            if (val > 60) bar.classList.add('accent');
            bar.style.height = `${val}%`;
            elements.volumeChart.appendChild(bar);
        });
    }

    /**
     * Streams logs to the intelligence terminal
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
     * Numeric animation helper
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
     * Button Actions
     */
    window.copyApiHook = () => {
        const url = window.location.origin + '/trigger-run';
        navigator.clipboard.writeText(url).then(() => {
            showToast('Premium API Trigger Hook Copied!');
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

    // Initialize Loops
    updateDashboard();
    setInterval(updateDashboard, 5000);
    setInterval(updateLogs, 3000);
});
