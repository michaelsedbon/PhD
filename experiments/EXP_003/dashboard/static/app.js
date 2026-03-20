/**
 * EXP_003 Simulation Dashboard — Frontend Logic
 * Handles tab switching, health polling, Chart.js rendering,
 * simulation run browsing, and markdown docs display.
 */

// ── Namespace ─────────────────────────────────────────────────
const App = {
    currentTab: 'health',
    pollInterval: null,
    charts: {},
    health: {},
    runs: {},
    docs: {},
};

// ── Chart.js defaults ─────────────────────────────────────────
const CHART_COLORS = {
    green: '#10b981',
    amber: '#f59e0b',
    red: '#ef4444',
    blue: '#3b82f6',
    purple: '#a78bfa',
    accent: '#818cf8',
    text: '#8b8e9e',
    grid: '#252833',
    gridLight: '#1a1c25',
};

const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 300 },
    plugins: {
        legend: {
            labels: { color: CHART_COLORS.text, font: { family: 'Inter', size: 11 } },
        },
    },
    scales: {
        x: {
            ticks: { color: CHART_COLORS.text, font: { family: 'Inter', size: 10 } },
            grid: { color: CHART_COLORS.gridLight },
        },
        y: {
            ticks: { color: CHART_COLORS.text, font: { family: 'Inter', size: 10 } },
            grid: { color: CHART_COLORS.grid },
        },
    },
};

// ══════════════════════════════════════════════════════════════
// TAB MANAGER
// ══════════════════════════════════════════════════════════════

const TOOLBAR_TITLES = {
    health:  '<i data-lucide="monitor" class="lucide-icon toolbar-icon"></i> Server Health<span>Real-time monitoring</span>',
    results: '<i data-lucide="bar-chart-3" class="lucide-icon toolbar-icon"></i> Simulation Results<span>Browse & compare runs</span>',
    docs:    '<i data-lucide="drafting-compass" class="lucide-icon toolbar-icon"></i> Architecture & Design<span>Flow diagram & documentation</span>',
    sweep:   '<i data-lucide="flask-conical" class="lucide-icon toolbar-icon"></i> Sweep Explorer<span>Parameter search analysis</span>',
};

function switchTab(tab) {
    if (tab === App.currentTab) return;
    App.currentTab = tab;

    // Update nav
    document.querySelectorAll('.nav-tab').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tab);
    });

    // Update panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    const target = document.getElementById(`panel-${tab}`);
    if (target) {
        target.classList.add('active');
        // Re-trigger animation
        target.style.animation = 'none';
        target.offsetHeight; // reflow
        target.style.animation = '';
    }

    // Update toolbar title
    document.getElementById('toolbar-title').innerHTML = TOOLBAR_TITLES[tab] || '';
    lucide.createIcons();

    // Load docs on first open
    if (tab === 'docs' && !App.docs.loaded) {
        App.docs.load();
    }

    // Load runs on first open
    if (tab === 'results' && !App.runs.loaded) {
        App.runs.loadList();
    }

    // Load sweep on first open
    if (tab === 'sweep' && !App.sweep.loaded) {
        App.sweep.loadSweeps();
    }
}

// Bind navigation
document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.dataset.tab));
});


// ══════════════════════════════════════════════════════════════
// HEALTH MODULE
// ══════════════════════════════════════════════════════════════

App.health = {
    connected: false,
    errorCount: 0,

    init() {
        this.createCharts();
        this.poll();
        App.pollInterval = setInterval(() => this.poll(), 2000);
    },

    async poll() {
        try {
            const res = await fetch('/api/health');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();

            this.errorCount = 0;
            this.setConnected(true);
            this.updateUI(data);
            this.updateSidebar(data);

            // Also fetch history for charts
            const hres = await fetch('/api/health/history');
            if (hres.ok) {
                const history = await hres.json();
                this.updateCharts(history);
            }
        } catch (e) {
            this.errorCount++;
            if (this.errorCount > 3) {
                this.setConnected(false);
            }
        }
    },

    setConnected(state) {
        this.connected = state;
        const dot = document.getElementById('connection-dot');
        const text = document.getElementById('connection-text');
        if (state) {
            dot.className = 'status-dot healthy';
            text.textContent = 'Connected';
        } else {
            dot.className = 'status-dot offline';
            text.textContent = 'Disconnected';
        }
    },

    updateUI(d) {
        // GPU
        const hasGpu = d.gpu_temp !== null;

        if (hasGpu) {
            document.getElementById('gpu-card-name').textContent = d.gpu_name || 'GPU';
            document.getElementById('gpu-temp-value').textContent = d.gpu_temp;

            const circle = document.getElementById('gpu-temp-circle');
            circle.className = 'temp-circle' + (d.gpu_temp > 90 ? ' hot' : d.gpu_temp > 80 ? ' warm' : '');

            const tempStatus = document.getElementById('gpu-temp-status');
            if (d.gpu_temp > 90) tempStatus.textContent = '🔴 CRITICAL';
            else if (d.gpu_temp > 80) tempStatus.textContent = '🟡 Warm';
            else tempStatus.textContent = '🟢 Normal';

            document.getElementById('gpu-vram-text').textContent =
                `${d.gpu_memory_used_mb} / ${d.gpu_memory_total_mb} MB`;
            const vramPct = (d.gpu_memory_used_mb / d.gpu_memory_total_mb) * 100;
            const vramBar = document.getElementById('gpu-vram-bar');
            vramBar.style.width = vramPct + '%';
            vramBar.className = 'progress-bar ' + (vramPct > 90 ? 'red' : vramPct > 70 ? 'amber' : 'green');

            document.getElementById('gpu-util-text').textContent = d.gpu_utilization + ' %';
            document.getElementById('gpu-util-bar').style.width = d.gpu_utilization + '%';

            // Status badge
            const badge = document.getElementById('gpu-status-badge');
            if (d.gpu_temp > 90) { badge.className = 'card-badge red'; badge.textContent = 'Critical'; }
            else if (d.gpu_temp > 80) { badge.className = 'card-badge amber'; badge.textContent = 'Warm'; }
            else { badge.className = 'card-badge green'; badge.textContent = 'Healthy'; }
        } else {
            document.getElementById('gpu-card-name').textContent = 'GPU (unavailable)';
            document.getElementById('gpu-temp-value').textContent = '—';
            document.getElementById('gpu-temp-status').textContent = 'No GPU detected';
            document.getElementById('gpu-status-badge').className = 'card-badge';
            document.getElementById('gpu-status-badge').textContent = 'N/A';
        }

        // Alert banner
        const alert = document.getElementById('health-alert');
        const alertText = document.getElementById('health-alert-text');
        if (hasGpu && d.gpu_temp > 90) {
            alert.style.display = 'flex';
            alert.className = 'alert-banner danger';
            alertText.textContent = `GPU temperature critical: ${d.gpu_temp}°C — consider reducing workload.`;
        } else if (hasGpu && d.gpu_temp > 80) {
            alert.style.display = 'flex';
            alert.className = 'alert-banner warning';
            alertText.textContent = `GPU temperature elevated: ${d.gpu_temp}°C`;
        } else {
            alert.style.display = 'none';
        }

        // CPU
        document.getElementById('cpu-value').innerHTML = `${d.cpu_percent}<span class="unit">%</span>`;
        const cpuBar = document.getElementById('cpu-bar');
        cpuBar.style.width = d.cpu_percent + '%';
        cpuBar.className = 'progress-bar ' + (d.cpu_percent > 90 ? 'red' : d.cpu_percent > 70 ? 'amber' : 'green');

        // RAM
        document.getElementById('ram-value').innerHTML = `${d.ram_used_gb}<span class="unit">GB</span>`;
        document.getElementById('ram-sub').textContent = `${d.ram_used_gb} / ${d.ram_total_gb} GB`;
        const ramPct = (d.ram_used_gb / d.ram_total_gb) * 100;
        const ramBar = document.getElementById('ram-bar');
        ramBar.style.width = ramPct + '%';
        ramBar.className = 'progress-bar ' + (ramPct > 90 ? 'red' : ramPct > 70 ? 'amber' : 'blue');

        // Disk
        document.getElementById('disk-value').innerHTML = `${d.disk_used_gb}<span class="unit">GB</span>`;
        document.getElementById('disk-sub').textContent = `${d.disk_used_gb} / ${d.disk_total_gb} GB`;
        const diskPct = (d.disk_used_gb / d.disk_total_gb) * 100;
        const diskBar = document.getElementById('disk-bar');
        diskBar.style.width = diskPct + '%';
        diskBar.className = 'progress-bar ' + (diskPct > 90 ? 'red' : diskPct > 70 ? 'amber' : 'green');

        // Uptime
        document.getElementById('uptime-value').textContent = formatUptime(d.uptime);

        // nvidia-smi raw
        if (d.nvidia_smi_raw) {
            document.getElementById('nvidia-smi-output').textContent = d.nvidia_smi_raw;
        } else {
            document.getElementById('nvidia-smi-output').textContent = 'nvidia-smi not available on this system.';
        }
    },

    updateSidebar(d) {
        const dot = document.getElementById('sidebar-status-dot');
        if (d.gpu_temp !== null) {
            if (d.gpu_temp > 90) dot.className = 'status-dot critical';
            else if (d.gpu_temp > 80) dot.className = 'status-dot warm';
            else dot.className = 'status-dot healthy';

            document.getElementById('sidebar-gpu-temp').textContent = d.gpu_temp + '°C';
            document.getElementById('sidebar-gpu-temp').className =
                'value' + (d.gpu_temp > 90 ? ' crit' : d.gpu_temp > 80 ? ' warn' : '');

            const vramPct = Math.round((d.gpu_memory_used_mb / d.gpu_memory_total_mb) * 100);
            document.getElementById('sidebar-gpu-vram').textContent = vramPct + '% used';
        } else {
            dot.className = 'status-dot healthy';
            document.getElementById('sidebar-gpu-temp').textContent = 'N/A';
            document.getElementById('sidebar-gpu-vram').textContent = 'N/A';
        }

        document.getElementById('sidebar-cpu').textContent = d.cpu_percent + '%';
        const ramPct = Math.round((d.ram_used_gb / d.ram_total_gb) * 100);
        document.getElementById('sidebar-ram').textContent = ramPct + '% used';
    },

    createCharts() {
        // GPU Temperature
        App.charts.gpuTemp = new Chart(
            document.getElementById('chart-gpu-temp').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'GPU Temp (°C)',
                        data: [],
                        borderColor: CHART_COLORS.amber,
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 0,
                    }],
                },
                options: {
                    ...CHART_DEFAULTS,
                    plugins: {
                        ...CHART_DEFAULTS.plugins,
                        legend: { display: false },
                    },
                    scales: {
                        ...CHART_DEFAULTS.scales,
                        y: { ...CHART_DEFAULTS.scales.y, suggestedMin: 30, suggestedMax: 100 },
                    },
                },
            }
        );

        // GPU Utilization
        App.charts.gpuUtil = new Chart(
            document.getElementById('chart-gpu-util').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'GPU Util (%)',
                        data: [],
                        borderColor: CHART_COLORS.accent,
                        backgroundColor: 'rgba(129, 140, 248, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 0,
                    }],
                },
                options: {
                    ...CHART_DEFAULTS,
                    plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
                    scales: {
                        ...CHART_DEFAULTS.scales,
                        y: { ...CHART_DEFAULTS.scales.y, min: 0, max: 100 },
                    },
                },
            }
        );

        // RAM
        App.charts.ram = new Chart(
            document.getElementById('chart-ram').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'RAM (GB)',
                        data: [],
                        borderColor: CHART_COLORS.blue,
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.3,
                        pointRadius: 0,
                    }],
                },
                options: {
                    ...CHART_DEFAULTS,
                    plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
                    scales: {
                        ...CHART_DEFAULTS.scales,
                        y: { ...CHART_DEFAULTS.scales.y, suggestedMin: 0 },
                    },
                },
            }
        );
    },

    updateCharts(history) {
        if (!history || history.length === 0) return;

        const labels = history.map(h => {
            const d = new Date(h.timestamp);
            return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        });

        // GPU Temp
        const gpuTemps = history.map(h => h.gpu_temp);
        App.charts.gpuTemp.data.labels = labels;
        App.charts.gpuTemp.data.datasets[0].data = gpuTemps;
        App.charts.gpuTemp.update('none');

        // GPU Util
        const gpuUtils = history.map(h => h.gpu_utilization);
        App.charts.gpuUtil.data.labels = labels;
        App.charts.gpuUtil.data.datasets[0].data = gpuUtils;
        App.charts.gpuUtil.update('none');

        // RAM
        const rams = history.map(h => h.ram_used_gb);
        App.charts.ram.data.labels = labels;
        App.charts.ram.data.datasets[0].data = rams;
        App.charts.ram.update('none');
    },

    async refreshNvidiaSmi() {
        try {
            const res = await fetch('/api/health');
            if (!res.ok) throw new Error();
            const data = await res.json();
            document.getElementById('nvidia-smi-output').textContent =
                data.nvidia_smi_raw || 'nvidia-smi not available.';
        } catch {
            document.getElementById('nvidia-smi-output').textContent = 'Failed to refresh.';
        }
    },
};


// ══════════════════════════════════════════════════════════════
// RUNS MODULE
// ══════════════════════════════════════════════════════════════

App.runs = {
    loaded: false,
    list: [],
    detailData: null,
    detailCharts: {},

    async loadList() {
        this.loaded = true;
        try {
            const res = await fetch('/api/runs');
            if (!res.ok) throw new Error();
            this.list = await res.json();
        } catch {
            this.list = [];
        }

        // Update badge
        document.getElementById('runs-count-badge').textContent = this.list.length;

        // Update comparison selects
        this.updateCompareSelects();

        if (this.list.length === 0) {
            document.getElementById('runs-empty-state').style.display = '';
            return;
        }

        document.getElementById('runs-empty-state').style.display = 'none';
        this.renderList();
    },

    renderList() {
        const container = document.getElementById('runs-list-container');
        // Remove old list if any (keep empty state)
        const existing = container.querySelector('.run-list');
        if (existing) existing.remove();

        const listEl = document.createElement('div');
        listEl.className = 'run-list';

        this.list.forEach(run => {
            const item = document.createElement('div');
            item.className = 'run-item';
            item.id = `run-item-${run.id}`;
            item.onclick = () => this.openDetail(run.id);

            const cfg = run.config || {};
            const metaParts = [];
            if (cfg.target_n) metaParts.push(`N=${cfg.target_n.toLocaleString()}`);
            if (cfg.mutation_rate) metaParts.push(`μ=${cfg.mutation_rate}`);
            if (cfg.keep_fraction) metaParts.push(`k=${cfg.keep_fraction}`);
            if (run.n_snapshots) metaParts.push(`${run.n_snapshots} snapshots`);

            item.innerHTML = `
                <div class="run-icon"><i data-lucide="dna" class="lucide-icon"></i></div>
                <div class="run-info">
                    <div class="run-name">${run.filename}</div>
                    <div class="run-meta">${metaParts.join(' · ') || 'No metadata'}</div>
                </div>
                <span class="run-status ${run.status}">${run.status}</span>
            `;
            listEl.appendChild(item);
        });

        container.appendChild(listEl);
        lucide.createIcons();
    },

    updateCompareSelects() {
        ['compare-select-a', 'compare-select-b'].forEach(id => {
            const sel = document.getElementById(id);
            sel.innerHTML = `<option value="">Select run…</option>`;
            this.list.forEach(run => {
                const opt = document.createElement('option');
                opt.value = run.id;
                opt.textContent = run.filename;
                sel.appendChild(opt);
            });
        });
    },

    async openDetail(runId) {
        try {
            const res = await fetch(`/api/runs/${runId}`);
            if (!res.ok) throw new Error();
            this.detailData = await res.json();
        } catch {
            return;
        }

        const run = this.list.find(r => r.id === runId);
        document.getElementById('run-detail-title').textContent = run ? run.filename : runId;

        // Show detail, hide list
        document.getElementById('runs-list-container').style.display = 'none';
        document.getElementById('comparison-bar').style.display = 'none';
        document.getElementById('run-detail').style.display = 'block';

        this.renderConfig(this.detailData.config || {});
        this.renderDetailCharts(this.detailData.metrics || []);
    },

    closeDetail() {
        document.getElementById('run-detail').style.display = 'none';
        document.getElementById('runs-list-container').style.display = '';
        document.getElementById('comparison-bar').style.display = '';
        this.destroyDetailCharts();
    },

    renderConfig(cfg) {
        const grid = document.getElementById('run-config-grid');
        grid.innerHTML = '';
        Object.entries(cfg).forEach(([key, val]) => {
            if (val === null || val === undefined) return;
            const item = document.createElement('div');
            item.className = 'config-item';
            item.innerHTML = `
                <span class="config-key">${key}</span>
                <span class="config-val">${typeof val === 'number' ? val.toLocaleString() : val}</span>
            `;
            grid.appendChild(item);
        });
    },

    renderDetailCharts(metrics) {
        if (!metrics || metrics.length === 0) return;
        this.destroyDetailCharts();

        const cycles = metrics.map((_, i) => i);

        // Affinity maturation
        this.detailCharts.affinity = new Chart(
            document.getElementById('chart-affinity').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: cycles,
                    datasets: [
                        {
                            label: 'Mean Affinity',
                            data: metrics.map(m => m.mean_affinity),
                            borderColor: CHART_COLORS.accent,
                            backgroundColor: 'rgba(129, 140, 248, 0.08)',
                            fill: true,
                            borderWidth: 2,
                            tension: 0.3,
                            pointRadius: 0,
                        },
                        {
                            label: 'Max Affinity',
                            data: metrics.map(m => m.max_affinity),
                            borderColor: CHART_COLORS.green,
                            borderWidth: 1.5,
                            borderDash: [4, 2],
                            tension: 0.3,
                            pointRadius: 0,
                        },
                        {
                            label: 'Min Affinity',
                            data: metrics.map(m => m.min_affinity),
                            borderColor: CHART_COLORS.red,
                            borderWidth: 1.5,
                            borderDash: [4, 2],
                            tension: 0.3,
                            pointRadius: 0,
                        },
                    ],
                },
                options: {
                    ...CHART_DEFAULTS,
                    scales: {
                        ...CHART_DEFAULTS.scales,
                        x: { ...CHART_DEFAULTS.scales.x, title: { display: true, text: 'Cycle', color: CHART_COLORS.text } },
                        y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: 'Affinity', color: CHART_COLORS.text }, suggestedMin: 0, suggestedMax: 1 },
                    },
                },
            }
        );

        // Population dynamics
        this.detailCharts.population = new Chart(
            document.getElementById('chart-population').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: cycles,
                    datasets: [
                        { label: 'Alive', data: metrics.map(m => m.n_alive), borderColor: CHART_COLORS.green, borderWidth: 2, tension: 0.3, pointRadius: 0 },
                        { label: 'DZ', data: metrics.map(m => m.n_in_dz), borderColor: CHART_COLORS.blue, borderWidth: 1.5, tension: 0.3, pointRadius: 0 },
                        { label: 'LZ', data: metrics.map(m => m.n_in_lz), borderColor: CHART_COLORS.amber, borderWidth: 1.5, tension: 0.3, pointRadius: 0 },
                        { label: 'Buffer', data: metrics.map(m => m.n_in_buffer), borderColor: CHART_COLORS.purple, borderWidth: 1.5, tension: 0.3, pointRadius: 0 },
                    ],
                },
                options: {
                    ...CHART_DEFAULTS,
                    scales: {
                        ...CHART_DEFAULTS.scales,
                        x: { ...CHART_DEFAULTS.scales.x, title: { display: true, text: 'Cycle', color: CHART_COLORS.text } },
                        y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: 'Count', color: CHART_COLORS.text } },
                    },
                },
            }
        );

        // Diversity (dual Y-axis)
        this.detailCharts.diversity = new Chart(
            document.getElementById('chart-diversity').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: cycles,
                    datasets: [
                        {
                            label: 'Shannon Entropy',
                            data: metrics.map(m => m.shannon_entropy),
                            borderColor: CHART_COLORS.accent,
                            borderWidth: 2,
                            tension: 0.3,
                            pointRadius: 0,
                            yAxisID: 'y',
                        },
                        {
                            label: 'Simpson Index',
                            data: metrics.map(m => m.simpson_index),
                            borderColor: CHART_COLORS.amber,
                            borderWidth: 2,
                            tension: 0.3,
                            pointRadius: 0,
                            yAxisID: 'y1',
                        },
                    ],
                },
                options: {
                    ...CHART_DEFAULTS,
                    scales: {
                        x: CHART_DEFAULTS.scales.x,
                        y: { ...CHART_DEFAULTS.scales.y, position: 'left', title: { display: true, text: 'Shannon H', color: CHART_COLORS.text } },
                        y1: { ...CHART_DEFAULTS.scales.y, position: 'right', title: { display: true, text: 'Simpson D', color: CHART_COLORS.text }, grid: { drawOnChartArea: false } },
                    },
                },
            }
        );

        // Unique clones
        this.detailCharts.clones = new Chart(
            document.getElementById('chart-clones').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: cycles,
                    datasets: [{
                        label: 'Unique Clones',
                        data: metrics.map(m => m.n_unique_clones),
                        borderColor: CHART_COLORS.purple,
                        backgroundColor: 'rgba(167, 139, 250, 0.08)',
                        fill: true,
                        borderWidth: 2,
                        tension: 0.3,
                        pointRadius: 0,
                    }],
                },
                options: {
                    ...CHART_DEFAULTS,
                    plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
                },
            }
        );

        // Clone frequency bar chart (final timepoint)
        const lastMetric = metrics[metrics.length - 1];
        if (lastMetric.clone_size_distribution) {
            const cloneDist = lastMetric.clone_size_distribution.slice(0, 20);
            this.detailCharts.cloneFreq = new Chart(
                document.getElementById('chart-clone-freq').getContext('2d'),
                {
                    type: 'bar',
                    data: {
                        labels: cloneDist.map((_, i) => `Clone ${i + 1}`),
                        datasets: [{
                            label: 'Frequency',
                            data: cloneDist,
                            backgroundColor: cloneDist.map((_, i) =>
                                `hsla(${240 + i * 6}, 70%, 65%, 0.7)`
                            ),
                            borderRadius: 4,
                        }],
                    },
                    options: {
                        ...CHART_DEFAULTS,
                        plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
                    },
                }
            );
        }

        // Hamming distribution with slider
        if (lastMetric.hamming_histogram) {
            const slider = document.getElementById('hamming-slider');
            slider.max = metrics.length - 1;
            slider.value = metrics.length - 1;
            document.getElementById('hamming-slider-value').textContent = `Cycle ${metrics.length - 1}`;

            this.renderHammingChart(metrics, parseInt(slider.value));
            slider.oninput = () => {
                const idx = parseInt(slider.value);
                document.getElementById('hamming-slider-value').textContent = `Cycle ${idx}`;
                this.renderHammingChart(metrics, idx);
            };
        }
    },

    renderHammingChart(metrics, idx) {
        const m = metrics[idx];
        if (!m || !m.hamming_histogram) return;

        if (this.detailCharts.hamming) {
            this.detailCharts.hamming.destroy();
        }

        const hist = m.hamming_histogram;
        this.detailCharts.hamming = new Chart(
            document.getElementById('chart-hamming').getContext('2d'),
            {
                type: 'bar',
                data: {
                    labels: hist.map((_, i) => i),
                    datasets: [{
                        label: 'Count',
                        data: hist,
                        backgroundColor: 'rgba(129, 140, 248, 0.5)',
                        borderColor: CHART_COLORS.accent,
                        borderWidth: 1,
                        borderRadius: 2,
                    }],
                },
                options: {
                    ...CHART_DEFAULTS,
                    plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
                    scales: {
                        ...CHART_DEFAULTS.scales,
                        x: { ...CHART_DEFAULTS.scales.x, title: { display: true, text: 'Hamming Distance', color: CHART_COLORS.text } },
                        y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: 'Count', color: CHART_COLORS.text } },
                    },
                },
            }
        );
    },

    destroyDetailCharts() {
        Object.values(this.detailCharts).forEach(c => { if (c) c.destroy(); });
        this.detailCharts = {};
    },

    async compare() {
        const idA = document.getElementById('compare-select-a').value;
        const idB = document.getElementById('compare-select-b').value;
        if (!idA || !idB || idA === idB) return;

        try {
            const [resA, resB] = await Promise.all([
                fetch(`/api/runs/${idA}`).then(r => r.json()),
                fetch(`/api/runs/${idB}`).then(r => r.json()),
            ]);

            const metricsA = resA.metrics || [];
            const metricsB = resB.metrics || [];
            if (metricsA.length === 0 && metricsB.length === 0) return;

            // Show detail with comparison
            document.getElementById('runs-list-container').style.display = 'none';
            document.getElementById('comparison-bar').style.display = 'none';
            document.getElementById('run-detail').style.display = 'block';
            document.getElementById('run-detail-title').textContent = `Comparing: ${idA} vs ${idB}`;

            this.destroyDetailCharts();
            this.renderComparisonCharts(metricsA, metricsB, idA, idB);
        } catch { /* graceful */ }
    },

    renderComparisonCharts(mA, mB, nameA, nameB) {
        const maxLen = Math.max(mA.length, mB.length);
        const cycles = Array.from({ length: maxLen }, (_, i) => i);

        // Affinity comparison
        this.detailCharts.affinity = new Chart(
            document.getElementById('chart-affinity').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: cycles,
                    datasets: [
                        { label: `${nameA} Mean`, data: mA.map(m => m.mean_affinity), borderColor: CHART_COLORS.accent, borderWidth: 2, tension: 0.3, pointRadius: 0 },
                        { label: `${nameB} Mean`, data: mB.map(m => m.mean_affinity), borderColor: CHART_COLORS.green, borderWidth: 2, tension: 0.3, pointRadius: 0 },
                    ],
                },
                options: { ...CHART_DEFAULTS },
            }
        );

        // Population comparison
        this.detailCharts.population = new Chart(
            document.getElementById('chart-population').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: cycles,
                    datasets: [
                        { label: `${nameA} Alive`, data: mA.map(m => m.n_alive), borderColor: CHART_COLORS.accent, borderWidth: 2, tension: 0.3, pointRadius: 0 },
                        { label: `${nameB} Alive`, data: mB.map(m => m.n_alive), borderColor: CHART_COLORS.green, borderWidth: 2, tension: 0.3, pointRadius: 0 },
                    ],
                },
                options: { ...CHART_DEFAULTS },
            }
        );
    },

    clearComparison() {
        this.closeDetail();
    },
};


// ══════════════════════════════════════════════════════════════
// DOCS MODULE
// ══════════════════════════════════════════════════════════════

App.docs = {
    loaded: false,

    async load() {
        try {
            const res = await fetch('/api/docs/flow');
            if (!res.ok) throw new Error(`Failed to load docs: ${res.status}`);
            const data = await res.json();
            this.loaded = true;
            this.render(data.content);
        } catch (e) {
            document.getElementById('docs-content').innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon"><i data-lucide="drafting-compass" class="lucide-icon empty-lucide"></i></div>
                    <h3>Could not load documentation</h3>
                    <p>${e.message}. Make sure the flow diagram exists at <code>~/gc_simulation/EXP_003/docs/flow_diagram_v2_pipeline.md</code></p>
                </div>
            `;
        }
    },

    render(markdown) {
        // Configure marked
        marked.setOptions({
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    return hljs.highlight(code, { language: lang }).value;
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: false,
            gfm: true,
        });

        const html = marked.parse(markdown);
        document.getElementById('docs-content').innerHTML = html;

        // Generate TOC
        this.generateTOC();

        // Initialize mermaid
        try {
            mermaid.initialize({
                startOnLoad: false,
                theme: 'dark',
                themeVariables: {
                    primaryColor: '#818cf8',
                    primaryTextColor: '#e4e5ea',
                    primaryBorderColor: '#2f3344',
                    lineColor: '#5c5f72',
                    sectionBkgColor: '#13141b',
                    altSectionBkgColor: '#1a1c25',
                    gridColor: '#252833',
                    background: '#0c0d12',
                },
            });
            mermaid.run({ nodes: document.querySelectorAll('.mermaid') });
        } catch { /* mermaid might not find diagrams */ }
    },

    generateTOC() {
        const content = document.getElementById('docs-content');
        const headings = content.querySelectorAll('h1, h2, h3');
        const tocContainer = document.getElementById('toc-links');
        tocContainer.innerHTML = '';

        headings.forEach((heading, i) => {
            const id = `doc-heading-${i}`;
            heading.id = id;

            const depth = parseInt(heading.tagName[1]);
            const link = document.createElement('a');
            link.className = `toc-link depth-${depth}`;
            link.textContent = heading.textContent;
            link.onclick = (e) => {
                e.preventDefault();
                heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
                // Update active
                document.querySelectorAll('.toc-link').forEach(l => l.classList.remove('active'));
                link.classList.add('active');
            };

            tocContainer.appendChild(link);
        });

        // Intersection observer for active TOC highlighting
        const observer = new IntersectionObserver(
            entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const id = entry.target.id;
                        document.querySelectorAll('.toc-link').forEach((link, i) => {
                            link.classList.toggle('active', `doc-heading-${i}` === id);
                        });
                    }
                });
            },
            { rootMargin: '-80px 0px -80% 0px' }
        );

        headings.forEach(h => observer.observe(h));
    },
};


// ══════════════════════════════════════════════════════════════
// SWEEP EXPLORER MODULE
// ══════════════════════════════════════════════════════════════

const MUT_LABELS = {
    '3.31e-8': 'Δ28',
    '4.26e-6': 'Double',
    '1.04e-5': 'Triple',
    '1.73e-5': 'Quintuple',
};

const MUT_COLORS = {
    '3.31e-8': '#6366f1',
    '4.26e-6': '#3b82f6',
    '1.04e-5': '#10b981',
    '1.73e-5': '#f59e0b',
};

function mutLabel(rate) {
    // Find closest matching key
    const r = parseFloat(rate);
    for (const [k, v] of Object.entries(MUT_LABELS)) {
        if (Math.abs(r - parseFloat(k)) / parseFloat(k) < 0.1) return v;
    }
    return r.toExponential(1);
}

function mutColor(rate) {
    const r = parseFloat(rate);
    for (const [k, v] of Object.entries(MUT_COLORS)) {
        if (Math.abs(r - parseFloat(k)) / parseFloat(k) < 0.1) return v;
    }
    return CHART_COLORS.accent;
}

App.sweep = {
    loaded: false,
    sweeps: [],
    currentSweepId: null,
    allRuns: [],
    filteredRuns: [],

    // ── Mutation rate helpers ──
    MUT_LABELS: {
        3.31e-8:  '3.3×10⁻⁸ spb/gen — wild-type T7 replisome (Δ28 variant)',
        4.26e-6:  '4.3×10⁻⁶ spb/gen — 2-mutation variant',
        1.04e-5:  '1.0×10⁻⁵ spb/gen — 3-mutation variant',
        1.73e-5:  '1.7×10⁻⁵ spb/gen — 5-mutation variant (max rate)',
    },
    MUT_SHORT: {
        3.31e-8:  '3.3e-8',
        4.26e-6:  '4.3e-6',
        1.04e-5:  '1.0e-5',
        1.73e-5:  '1.7e-5',
    },
    MUT_COLORS_HEX: {
        3.31e-8:  '#6366f1',
        4.26e-6:  '#34d399',
        1.04e-5:  '#fbbf24',
        1.73e-5:  '#ef4444',
    },

    _mutLabel(rate) {
        for (const [k, v] of Object.entries(this.MUT_LABELS)) {
            if (Math.abs(rate - parseFloat(k)) / parseFloat(k) < 0.15) return v;
        }
        return rate.toExponential(2);
    },
    _mutShort(rate) {
        for (const [k, v] of Object.entries(this.MUT_SHORT)) {
            if (Math.abs(rate - parseFloat(k)) / parseFloat(k) < 0.15) return v;
        }
        return rate.toExponential(2);
    },
    _mutIndex(rate) {
        const keys = Object.keys(this.MUT_SHORT).map(Number).sort((a,b)=>a-b);
        for (let i = 0; i < keys.length; i++) {
            if (Math.abs(rate - keys[i]) / keys[i] < 0.15) return i;
        }
        return keys.length;
    },

    // ── Plotly dark theme layout ──
    _plotlyLayout(extra) {
        return Object.assign({
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor:  'rgba(0,0,0,0)',
            font: { family: 'Inter, sans-serif', color: '#e2e8f0', size: 12 },
            margin: { t: 30, b: 60, l: 60, r: 40 },
        }, extra);
    },
    _plotlyAxisStyle() {
        return {
            gridcolor: 'rgba(255,255,255,0.07)',
            zerolinecolor: 'rgba(255,255,255,0.1)',
            tickfont: { color: '#94a3b8', size: 11 },
            titlefont: { color: '#cbd5e1', size: 12 },
        };
    },
    _hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r},${g},${b},${alpha})`;
    },

    // ═══════════════════════════════════════════
    //  LOAD SWEEPS
    // ═══════════════════════════════════════════
    async loadSweeps() {
        try {
            const res = await fetch('/api/sweeps');
            this.sweeps = await res.json();
            console.log('[sweep] Loaded', this.sweeps.length, 'sweeps:', this.sweeps.map(s => s.id));
        } catch (err) {
            console.error('[sweep] Failed to fetch /api/sweeps:', err);
            this.sweeps = [];
        }

        const sel = document.getElementById('sweep-select');
        sel.innerHTML = '';
        if (!this.sweeps.length) {
            sel.innerHTML = '<option value="">No sweeps</option>';
            document.getElementById('sweep-empty-state').style.display = '';
            document.getElementById('sweep-context-content').textContent = 'No sweeps available.';
            return;
        }
        this.sweeps.forEach(s => {
            const o = document.createElement('option');
            o.value = s.id;
            o.textContent = `${s.id} (${s.n_runs} runs)`;
            sel.appendChild(o);
        });
        sel.onchange = () => { this.currentSweepId = sel.value; this.loadSweepData(); };
        this.currentSweepId = this.sweeps[0].id;
        this.loadSweepData();
    },

    // ═══════════════════════════════════════════
    //  LOAD SWEEP DATA  (summary + context)
    // ═══════════════════════════════════════════
    async loadSweepData() {
        if (!this.currentSweepId) return;
        try {
            const res = await fetch(`/api/sweeps/${this.currentSweepId}/summary`);
            this.allRuns = await res.json();
            console.log('[sweep] Loaded', this.allRuns.length, 'runs for', this.currentSweepId);
        } catch (err) {
            console.error('[sweep] Failed to fetch summary:', err);
            this.allRuns = [];
        }

        this.loadSweepContext();
        this.buildFilters();
        this.applyFilters();
        this.loadNotes();
        this.loaded = true;
    },

    // ═══════════════════════════════════════════
    //  SWEEP CONTEXT (fixed / swept params)
    // ═══════════════════════════════════════════
    loadSweepContext() {
        const sw = this.sweeps.find(s => s.id === this.currentSweepId);
        const el = document.getElementById('sweep-context-content');
        if (!sw || !sw.manifest) {
            console.warn('[sweep] No manifest found for', this.currentSweepId, '— sweep obj:', sw);
            el.textContent = 'No manifest found for this sweep.';
            return;
        }
        const m = sw.manifest;

        // Fixed params
        const fixed = m.fixed_parameters || {};
        const fixedStr = Object.entries(fixed).map(([k,v]) => `${k} = ${v}`).join(' · ');

        // Swept params
        const swept = m.swept_parameters || {};
        let sweptHTML = '<table class="param-table" style="margin-top:8px;"><thead><tr><th>Parameter</th><th>Values</th><th>Count</th></tr></thead><tbody>';
        for (const [p, vals] of Object.entries(swept)) {
            // vals could be an array [0.05, 0.1] or an object {delta28: 3.31e-8, ...}
            const isArr = Array.isArray(vals);
            const valsList = isArr ? vals : Object.values(vals);
            const labelsList = isArr ? vals : Object.keys(vals);
            let displayVals;
            if (p === 'paper_mutation_rate') {
                displayVals = isArr
                    ? valsList.map(v => { const n = parseFloat(v); return isNaN(n) ? v : n.toExponential(2); })
                    : Object.entries(vals).map(([name, v]) => `${name}: ${parseFloat(v).toExponential(2)}`);
            } else {
                displayVals = valsList;
            }
            const count = valsList.length;
            sweptHTML += `<tr><td><code>${p}</code></td><td>${Array.isArray(displayVals) ? displayVals.join(', ') : displayVals}</td><td>${count}</td></tr>`;
        }
        sweptHTML += '</tbody></table>';

        // Stats
        const stats = m.total_runs
            ? `Total: <strong>${m.total_runs}</strong> runs · Failed: ${m.failed || 0} · Runtime: <strong>${(m.runtime_minutes || 0).toFixed(1)}</strong> min · Seed: ${m.seed || '—'}`
            : '';

        el.innerHTML = `<p><strong>Fixed Parameters</strong><br/>${fixedStr}</p>
            <p style="margin-top:8px;"><strong>Swept Parameters</strong></p>${sweptHTML}
            ${stats ? `<p style="margin-top:8px;">${stats}</p>` : ''}`;

        // ── Populate experiment intent from manifest ──
        const intentEl = document.getElementById('sweep-intent');
        if (intentEl) {
            const intent = m.intent || '';
            const hypothesis = m.hypothesis || '';
            if (intent || hypothesis) {
                intentEl.innerHTML =
                    `<strong style="color:var(--text);font-size:14px;">Experiment intent — ${m.sweep_id || this.currentSweepId}</strong><br>` +
                    (intent ? `${intent}<br>` : '') +
                    (hypothesis ? `<br><strong>Hypothesis:</strong> ${hypothesis}` : '');
            } else {
                intentEl.innerHTML = '<em>No intent specified in manifest.</em>';
            }
        }
    },

    // ═══════════════════════════════════════════
    //  FILTER BAR
    // ═══════════════════════════════════════════
    buildFilters() {
        const uniq = (arr, key) => [...new Set(arr.map(r => r[key]).filter(v => v != null))].sort((a,b)=>a-b);
        const fill = (id, key, labelFn) => {
            const sel = document.getElementById(id);
            const vals = uniq(this.allRuns, key);
            sel.innerHTML = '<option value="all">All</option>';
            vals.forEach(v => {
                const o = document.createElement('option');
                o.value = v;
                o.textContent = labelFn ? labelFn(v) : v;
                sel.appendChild(o);
            });
            sel.onchange = () => this.applyFilters();
        };
        fill('filter-mutation', 'paper_mutation_rate', v => this._mutLabel(v));
        fill('filter-keep',     'keep_fraction');
        fill('filter-sample',   'sample_fraction');
        fill('filter-leak',     'leak_fraction');
        fill('filter-incubation','incubation_time', v => `${v} min`);
        fill('filter-target-n', 'target_n',         v => v >= 1e6 ? `${(v/1e6).toFixed(0)}M` : `${(v/1e3).toFixed(0)}K`);
    },

    applyFilters() {
        const getV = id => document.getElementById(id).value;
        let runs = this.allRuns;
        const fv = getV('filter-mutation');   if (fv !== 'all') runs = runs.filter(r => String(r.paper_mutation_rate) === fv);
        const kv = getV('filter-keep');       if (kv !== 'all') runs = runs.filter(r => String(r.keep_fraction) === kv);
        const sv = getV('filter-sample');     if (sv !== 'all') runs = runs.filter(r => String(r.sample_fraction) === sv);
        const lv = getV('filter-leak');       if (lv !== 'all') runs = runs.filter(r => String(r.leak_fraction) === lv);
        const iv = getV('filter-incubation'); if (iv !== 'all') runs = runs.filter(r => String(r.incubation_time) === iv);
        const tv = getV('filter-target-n');   if (tv !== 'all') runs = runs.filter(r => String(r.target_n) === tv);
        this.filteredRuns = runs;

        document.getElementById('filter-count').textContent = `${runs.length} runs`;

        // ── Auto-detect sweep layout ──
        const uniqueNs = [...new Set(this.allRuns.map(r => r.target_n))].sort((a,b) => a-b);
        const is2N = uniqueNs.length === 2;

        // Show/hide sections based on N count
        const show = (id, visible) => {
            const el = document.getElementById(id);
            if (el) el.style.display = visible ? '' : 'none';
        };
        show('section-parcoords', is2N);
        show('section-heatmaps', is2N);
        show('section-3d', is2N);
        show('section-paired', is2N);
        show('section-timecourses', is2N);
        show('section-n-scaling', !is2N && uniqueNs.length > 1);
        show('section-n-relchange', !is2N && uniqueNs.length > 1);
        show('section-n-selection-diversity', !is2N && uniqueNs.length > 1);
        show('section-n-boxplots', !is2N && uniqueNs.length > 1);
        show('section-n-r2', !is2N && uniqueNs.length > 1);
        show('section-n-verdict', !is2N && uniqueNs.length > 1);

        if (is2N) {
            this.renderParallelCoords();
            this.renderFacetedHeatmaps();
            this.render3DPlots();
            this.renderPairedComparison();
        }
        if (!is2N && uniqueNs.length > 1) {
            this.renderNScaling();
            this.renderRelativeChange();
            this.renderSelectionDiversity();
            this.renderBoxPlotsByN();
            this.renderR2Heatmap();
            this.renderNVerdict();
        }
    },

    // ═══════════════════════════════════════════
    //  PARALLEL COORDINATES (only for multi-param sweeps)
    // ═══════════════════════════════════════════
    renderParallelCoords() {
        const runs = this.filteredRuns;
        if (!runs.length) {
            Plotly.purge('parcoords-affinity');
            Plotly.purge('parcoords-diversity');
            return;
        }

        const mutKeys  = Object.keys(this.MUT_SHORT).map(Number).sort((a,b)=>a-b);
        const mutIdxs  = runs.map(r => this._mutIndex(r.paper_mutation_rate));
        const mutTickVals = mutKeys.map((_, i) => i);
        const mutTickText = mutKeys.map(k => this._mutShort(k));

        const testedVals = (key) => [...new Set(this.allRuns.map(r => r[key]))].sort((a,b)=>a-b);
        const keepTested  = testedVals('keep_fraction');
        const sampleTested = testedVals('sample_fraction');
        const leakTested  = testedVals('leak_fraction');
        const incTested   = testedVals('incubation_time');

        const dims = [
            {
                label: 'Mutation Rate',
                values: mutIdxs,
                tickvals: mutTickVals,
                ticktext: mutTickText,
                range: [-0.3, mutKeys.length - 0.7],
            },
            {
                label: 'Keep Fraction',
                values: runs.map(r => r.keep_fraction),
                tickvals: keepTested,
                ticktext: keepTested.map(String),
                range: [Math.min(...keepTested) - 0.01, Math.max(...keepTested) + 0.01],
            },
            {
                label: 'Sample Fraction',
                values: runs.map(r => r.sample_fraction),
                tickvals: sampleTested,
                ticktext: sampleTested.map(String),
                range: [Math.min(...sampleTested) - 0.02, Math.max(...sampleTested) + 0.02],
            },
            {
                label: 'Leak Fraction',
                values: runs.map(r => r.leak_fraction),
                tickvals: leakTested,
                ticktext: leakTested.map(String),
                range: [Math.min(...leakTested) - 0.005, Math.max(...leakTested) + 0.005],
            },
            {
                label: 'Incubation (min)',
                values: runs.map(r => r.incubation_time),
                tickvals: incTested,
                ticktext: incTested.map(v => `${v}`),
                range: [Math.min(...incTested) - 5, Math.max(...incTested) + 5],
            },
            {
                label: 'Target N',
                values: runs.map(r => r.target_n),
                tickvals: [100000, 1000000],
                ticktext: ['100K', '1M'],
                range: [0, 1100000],
            },
        ];

        // Affinity plot
        const affVals = runs.map(r => r.final_mean_affinity);
        const affDims = [...dims, { label: 'Final Affinity', values: affVals }];
        Plotly.react('parcoords-affinity', [{
            type: 'parcoords',
            line: {
                color: affVals,
                colorscale: [[0, '#312e81'], [0.25, '#4338ca'], [0.5, '#6366f1'], [0.75, '#f59e0b'], [1, '#ef4444']],
                showscale: true,
                colorbar: { title: 'Affinity', titleside: 'right', tickfont: { color: '#94a3b8' }, titlefont: { color: '#cbd5e1' } },
            },
            dimensions: affDims,
        }], this._plotlyLayout({ height: 460, margin: { t: 60, b: 30, l: 80, r: 80 } }), { responsive: true });

        // Diversity plot
        const divVals = runs.map(r => r.final_shannon || 0);
        const divDims = [...dims, { label: 'Final Shannon H', values: divVals }];
        Plotly.react('parcoords-diversity', [{
            type: 'parcoords',
            line: {
                color: divVals,
                colorscale: [[0, '#064e3b'], [0.3, '#059669'], [0.6, '#34d399'], [1, '#fbbf24']],
                showscale: true,
                colorbar: { title: 'Shannon H', titleside: 'right', tickfont: { color: '#94a3b8' }, titlefont: { color: '#cbd5e1' } },
            },
            dimensions: divDims,
        }], this._plotlyLayout({ height: 460, margin: { t: 60, b: 30, l: 80, r: 80 } }), { responsive: true });
    },

    // ═══════════════════════════════════════════
    //  FACETED HEATMAPS (mutation × keep → metric, split by N)
    // ═══════════════════════════════════════════
    renderFacetedHeatmaps() {
        const runs = this.allRuns;
        if (!runs.length) return;

        const mutKeys = Object.keys(this.MUT_SHORT).map(Number).sort((a,b)=>a-b);
        const keepVals = [...new Set(runs.map(r => r.keep_fraction))].sort((a,b)=>a-b);
        const yLabels = mutKeys.map(k => this._mutShort(k));
        const xLabels = keepVals.map(v => String(v));

        // Pre-compute ALL cell means for shared color scale
        const computeGrid = (metric, targetN) => {
            return mutKeys.map(mut =>
                keepVals.map(kp => {
                    const matching = runs.filter(r =>
                        Math.abs(r.paper_mutation_rate - mut) / mut < 0.15 &&
                        r.keep_fraction === kp &&
                        r.target_n === targetN
                    );
                    return matching.length
                        ? matching.reduce((s, r) => s + r[metric], 0) / matching.length
                        : null;
                })
            );
        };

        // Compute grids for both N values
        const affGrid100k = computeGrid('final_mean_affinity', 100000);
        const affGrid1m   = computeGrid('final_mean_affinity', 1000000);
        const shaGrid100k = computeGrid('final_shannon', 100000);
        const shaGrid1m   = computeGrid('final_shannon', 1000000);

        // Derive shared zmin/zmax from CELL MEANS (not individual runs)
        const rangeFromGrids = (...grids) => {
            const all = grids.flatMap(g => g.flat()).filter(v => v !== null);
            return [Math.min(...all), Math.max(...all)];
        };
        const [affMin, affMax] = rangeFromGrids(affGrid100k, affGrid1m);
        const [shaMin, shaMax] = rangeFromGrids(shaGrid100k, shaGrid1m);

        const renderHeatmap = (z, containerId, colorscale, zmin, zmax, isShannonMetric) => {
            const annotations = [];
            z.forEach((row, yi) => {
                row.forEach((val, xi) => {
                    if (val !== null) {
                        annotations.push({
                            x: xi, y: yi,
                            text: isShannonMetric ? val.toFixed(2) : val.toFixed(3),
                            font: { color: '#fff', size: 12, family: 'Inter' },
                            showarrow: false,
                        });
                    }
                });
            });

            Plotly.react(containerId, [{
                type: 'heatmap',
                z: z,
                x: xLabels,
                y: yLabels,
                colorscale: colorscale,
                showscale: true,
                zmin: zmin,
                zmax: zmax,
                colorbar: { tickfont: { color: '#94a3b8' } },
                hoverongaps: false,
                xgap: 2,
                ygap: 2,
            }], this._plotlyLayout({
                height: 340,
                xaxis: { title: 'Keep Fraction', type: 'category', ...this._plotlyAxisStyle() },
                yaxis: { title: 'Mutation Rate', type: 'category', ...this._plotlyAxisStyle(), autorange: true },
                annotations: annotations,
                margin: { t: 20, b: 60, l: 100, r: 60 },
            }), { responsive: true });
        };

        // Affinity heatmaps — same color scale across N
        const affScale = [[0, '#1e1b4b'], [0.25, '#3730a3'], [0.5, '#6366f1'], [0.75, '#f59e0b'], [1, '#ef4444']];
        renderHeatmap(affGrid100k, 'heatmap-aff-100k', affScale, affMin, affMax, false);
        renderHeatmap(affGrid1m,   'heatmap-aff-1m',   affScale, affMin, affMax, false);

        // Shannon heatmaps — same color scale across N
        const shaScale = [[0, '#064e3b'], [0.3, '#059669'], [0.6, '#34d399'], [1, '#fef3c7']];
        renderHeatmap(shaGrid100k, 'heatmap-div-100k', shaScale, shaMin, shaMax, true);
        renderHeatmap(shaGrid1m,   'heatmap-div-1m',   shaScale, shaMin, shaMax, true);
    },

    // ═══════════════════════════════════════════
    //  3D PARAMETER LANDSCAPE (scatter + surface)
    // ═══════════════════════════════════════════
    render3DPlots() {
        const runs = this.allRuns;
        if (!runs.length) return;

        const mutKeys = Object.keys(this.MUT_SHORT).map(Number).sort((a,b)=>a-b);
        const keepVals = [...new Set(runs.map(r => r.keep_fraction))].sort((a,b)=>a-b);
        const nColors = { 100000: '#6366f1', 1000000: '#f59e0b' };
        const nLabels = { 100000: 'N=100K', 1000000: 'N=1M' };

        const build3D = (metric, containerId, metricLabel) => {
            const traces = [];
            const showScatter = document.getElementById('toggle-3d-scatter').checked;
            const showSurface = document.getElementById('toggle-3d-surface').checked;

            for (const targetN of [100000, 1000000]) {
                const nRuns = runs.filter(r => r.target_n === targetN);
                const color = nColors[targetN];
                const label = nLabels[targetN];

                // ── Scatter: individual runs ──
                if (showScatter) {
                    traces.push({
                        type: 'scatter3d',
                        mode: 'markers',
                        x: nRuns.map(r => r.keep_fraction),
                        y: nRuns.map(r => this._mutIndex(r.paper_mutation_rate)),
                        z: nRuns.map(r => r[metric]),
                        name: `${label} (runs)`,
                        marker: {
                            size: 3,
                            color: color,
                            opacity: 0.35,
                        },
                        hovertemplate:
                            'Keep: %{x}<br>' +
                            'Mutation: %{text}<br>' +
                            metricLabel + ': %{z:.4f}<extra>' + label + '</extra>',
                        text: nRuns.map(r => this._mutShort(r.paper_mutation_rate)),
                    });
                }

                // ── Surface: grouped means ──
                if (showSurface) {
                    const zGrid = mutKeys.map(mut =>
                        keepVals.map(kp => {
                            const matching = nRuns.filter(r =>
                                Math.abs(r.paper_mutation_rate - mut) / mut < 0.15 &&
                                r.keep_fraction === kp
                            );
                            return matching.length
                                ? matching.reduce((s, r) => s + r[metric], 0) / matching.length
                                : null;
                        })
                    );

                    traces.push({
                        type: 'surface',
                        x: keepVals,
                        y: mutKeys.map((_, i) => i),
                        z: zGrid,
                        name: `${label} (mean)`,
                        colorscale: targetN === 100000
                            ? [[0, '#312e81'], [0.5, '#6366f1'], [1, '#a5b4fc']]
                            : [[0, '#78350f'], [0.5, '#f59e0b'], [1, '#fde68a']],
                        opacity: 0.7,
                        showscale: false,
                        contours: {
                            x: { show: true, color: 'rgba(255,255,255,0.15)', width: 1 },
                            y: { show: true, color: 'rgba(255,255,255,0.15)', width: 1 },
                        },
                    });
                }
            }

            if (!traces.length) {
                Plotly.purge(containerId);
                return;
            }

            const mutTickVals = mutKeys.map((_, i) => i);
            const mutTickText = mutKeys.map(k => this._mutShort(k));

            Plotly.react(containerId, traces, {
                scene: {
                    xaxis: { title: 'Keep Fraction', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.06)', backgroundcolor: '#0f172a' },
                    yaxis: { title: 'Mutation Rate', color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.06)', backgroundcolor: '#0f172a',
                             tickvals: mutTickVals, ticktext: mutTickText },
                    zaxis: { title: metricLabel, color: '#94a3b8', gridcolor: 'rgba(255,255,255,0.06)', backgroundcolor: '#0f172a' },
                    bgcolor: '#0f172a',
                    camera: { eye: { x: 1.8, y: -1.8, z: 1.2 } },
                },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { color: '#94a3b8', family: 'Inter, sans-serif' },
                margin: { t: 10, b: 10, l: 10, r: 10 },
                legend: {
                    font: { color: '#cbd5e1', size: 11 },
                    bgcolor: 'rgba(0,0,0,0.3)',
                    x: 0.01, y: 0.99,
                },
                height: 520,
            }, { responsive: true });
        };

        build3D('final_mean_affinity', 'plot3d-affinity', 'Affinity');
        build3D('final_shannon', 'plot3d-shannon', 'Shannon H');
    },

    update3DVisibility() {
        this.render3DPlots();
    },

    // ═══════════════════════════════════════════
    //  PAIRED COMPARISON (N=100K vs N=1M)
    // ═══════════════════════════════════════════
    renderPairedComparison() {
        const runs = this.allRuns;
        if (!runs.length) return;

        // Build matched pairs: group by everything except target_n
        const condKey = r => `${r.paper_mutation_rate}|${r.keep_fraction}|${r.sample_fraction}|${r.leak_fraction}|${r.incubation_time}`;

        // Group runs by condition + target_n
        const groups = {};
        for (const r of runs) {
            const k = condKey(r);
            if (!groups[k]) groups[k] = {};
            const n = r.target_n;
            if (!groups[k][n]) groups[k][n] = [];
            groups[k][n].push(r);
        }

        const buildPaired = (metric, containerId, metricLabel) => {
            const traces = [];
            const mutKeys = Object.keys(this.MUT_SHORT).map(Number).sort((a,b)=>a-b);

            for (const mut of mutKeys) {
                const x100k = [], y1m = [], hoverTexts = [];
                for (const [cond, byN] of Object.entries(groups)) {
                    if (!byN[100000] || !byN[1000000]) continue;
                    // Check this condition matches mutation rate
                    const sample100k = byN[100000];
                    if (Math.abs(sample100k[0].paper_mutation_rate - mut) / mut >= 0.15) continue;

                    const mean100k = sample100k.reduce((s,r) => s + r[metric], 0) / sample100k.length;
                    const mean1m = byN[1000000].reduce((s,r) => s + r[metric], 0) / byN[1000000].length;
                    x100k.push(mean100k);
                    y1m.push(mean1m);
                    hoverTexts.push(`keep=${sample100k[0].keep_fraction}, samp=${sample100k[0].sample_fraction}, leak=${sample100k[0].leak_fraction}`);
                }

                traces.push({
                    type: 'scatter',
                    mode: 'markers',
                    x: x100k,
                    y: y1m,
                    name: this._mutShort(mut),
                    marker: { size: 8, opacity: 0.8, color: this.MUT_COLORS_HEX[mut] || '#6366f1' },
                    text: hoverTexts,
                    hovertemplate: '%{text}<br>N=100K: %{x:.4f}<br>N=1M: %{y:.4f}<extra>%{fullData.name}</extra>',
                });
            }

            // Diagonal reference line (y = x)
            const allX = traces.flatMap(t => t.x);
            const allY = traces.flatMap(t => t.y);
            const lo = Math.min(...allX, ...allY) * 0.9;
            const hi = Math.max(...allX, ...allY) * 1.1;

            traces.push({
                type: 'scatter',
                mode: 'lines',
                x: [lo, hi],
                y: [lo, hi],
                line: { color: 'rgba(255,255,255,0.3)', width: 1, dash: 'dash' },
                showlegend: false,
                hoverinfo: 'skip',
            });

            // Compute R² and mean difference for annotation
            const diffs = allX.map((x, i) => allY[i] - x);
            const meanDiff = diffs.reduce((s,d) => s+d, 0) / diffs.length;
            const meanX = allX.reduce((s,v) => s+v, 0) / allX.length;
            const meanY = allY.reduce((s,v) => s+v, 0) / allY.length;
            const ssRes = allX.reduce((s, x, i) => s + (allY[i] - x) ** 2, 0);
            const ssTot = allY.reduce((s, y) => s + (y - meanY) ** 2, 0);
            const r2 = ssTot > 0 ? (1 - ssRes / ssTot).toFixed(3) : 'N/A';

            Plotly.react(containerId, traces, this._plotlyLayout({
                height: 420,
                xaxis: { title: `${metricLabel} — N=100K`, ...this._plotlyAxisStyle(), scaleanchor: 'y' },
                yaxis: { title: `${metricLabel} — N=1M`, ...this._plotlyAxisStyle() },
                margin: { t: 30, b: 60, l: 70, r: 30 },
                annotations: [{
                    text: `R² = ${r2} · Mean Δ = ${meanDiff >= 0 ? '+' : ''}${meanDiff.toFixed(4)}`,
                    x: 0.02, y: 0.98,
                    xref: 'paper', yref: 'paper',
                    showarrow: false,
                    font: { color: '#94a3b8', size: 11, family: 'JetBrains Mono' },
                    bgcolor: 'rgba(0,0,0,0.4)',
                    borderpad: 4,
                }],
            }), { responsive: true });
        };

        buildPaired('final_mean_affinity', 'paired-affinity', 'Affinity');
        buildPaired('final_shannon', 'paired-shannon', 'Shannon H');
    },

    // ═══════════════════════════════════════════
    //  N-SCALING PLOTS (multi-N sweeps)
    // ═══════════════════════════════════════════
    renderNScaling() {
        const runs = this.allRuns;
        if (!runs.length) return;

        const uniqueNs = [...new Set(runs.map(r => r.target_n))].sort((a, b) => a - b);
        const mutKeys = [...new Set(runs.map(r => r.paper_mutation_rate))].sort((a, b) => a - b);
        const keepVals = [...new Set(runs.map(r => r.keep_fraction))].sort((a, b) => a - b);

        // Line styles for keep_fraction
        const keepDash = { 0.05: 'solid', 0.1: 'dash', 0.3: 'dot' };
        const keepWidth = { 0.05: 2.5, 0.1: 2, 0.3: 1.5 };

        const buildNScale = (metric, containerId, metricLabel) => {
            const traces = [];

            for (const mut of mutKeys) {
                const color = this.MUT_COLORS_HEX[mut] || '#6366f1';
                for (const kf of keepVals) {
                    const xVals = [], yVals = [], errVals = [], hoverTexts = [];

                    for (const n of uniqueNs) {
                        const matching = runs.filter(r =>
                            Math.abs(r.paper_mutation_rate - mut) / mut < 0.15 &&
                            r.keep_fraction === kf &&
                            r.target_n === n
                        );
                        if (!matching.length) continue;

                        const vals = matching.map(r => r[metric]);
                        const mean = vals.reduce((s, v) => s + v, 0) / vals.length;
                        const std = Math.sqrt(vals.reduce((s, v) => s + (v - mean) ** 2, 0) / vals.length);
                        const sem = std / Math.sqrt(vals.length);

                        xVals.push(n);
                        yVals.push(mean);
                        errVals.push(sem);
                        hoverTexts.push(`N=${n >= 1e6 ? (n/1e6)+'M' : (n/1e3)+'K'}, n=${vals.length}`);
                    }

                    if (xVals.length < 2) continue;

                    traces.push({
                        type: 'scatter',
                        mode: 'lines+markers',
                        x: xVals,
                        y: yVals,
                        name: `μ=${this._mutShort(mut)}, k=${kf}`,
                        line: { color, dash: keepDash[kf] || 'solid', width: keepWidth[kf] || 2 },
                        marker: { size: 6, color },
                        error_y: { type: 'data', array: errVals, visible: true, thickness: 2, width: 6, color },
                        text: hoverTexts,
                        hovertemplate: `%{text}<br>${metricLabel}: %{y:.4f} ± %{error_y.array:.4f}<extra>%{fullData.name}</extra>`,
                    });
                }
            }

            Plotly.react(containerId, traces, this._plotlyLayout({
                height: 480,
                xaxis: {
                    title: 'Population Size (target_n)',
                    type: 'log',
                    ...this._plotlyAxisStyle(),
                    tickvals: uniqueNs,
                    ticktext: uniqueNs.map(n => n >= 1e6 ? `${(n/1e6)}M` : `${(n/1e3)}K`),
                },
                yaxis: { title: metricLabel, ...this._plotlyAxisStyle() },
                margin: { t: 30, b: 70, l: 70, r: 30 },
                legend: { font: { size: 10 } },
            }), { responsive: true });
        };

        buildNScale('final_mean_affinity', 'nscale-affinity', 'Mean Affinity');
        buildNScale('final_shannon', 'nscale-shannon', 'Mean Shannon H');
    },

    // ═══════════════════════════════════════════
    //  RELATIVE CHANGE FROM BASELINE N
    // ═══════════════════════════════════════════
    renderRelativeChange() {
        const runs = this.allRuns;
        if (!runs.length) return;

        const uniqueNs = [...new Set(runs.map(r => r.target_n))].sort((a, b) => a - b);
        const baselineN = uniqueNs[0];
        const mutKeys = [...new Set(runs.map(r => r.paper_mutation_rate))].sort((a, b) => a - b);
        const keepVals = [...new Set(runs.map(r => r.keep_fraction))].sort((a, b) => a - b);

        const keepDash = { 0.05: 'solid', 0.1: 'dash', 0.3: 'dot' };

        const getMean = (metric, mut, kf, n) => {
            const matching = runs.filter(r =>
                Math.abs(r.paper_mutation_rate - mut) / mut < 0.15 &&
                r.keep_fraction === kf && r.target_n === n
            );
            if (!matching.length) return null;
            return matching.reduce((s, r) => s + r[metric], 0) / matching.length;
        };

        const buildRelChange = (metric, containerId, metricLabel, yRange) => {
            const traces = [];

            for (const mut of mutKeys) {
                const color = this.MUT_COLORS_HEX[mut] || '#6366f1';
                for (const kf of keepVals) {
                    const baseline = getMean(metric, mut, kf, baselineN);
                    if (!baseline || baseline === 0) continue;

                    const xVals = [], yVals = [];
                    for (const n of uniqueNs) {
                        const val = getMean(metric, mut, kf, n);
                        if (val === null) continue;
                        xVals.push(n);
                        yVals.push(((val - baseline) / Math.abs(baseline)) * 100);
                    }
                    if (xVals.length < 2) continue;

                    traces.push({
                        type: 'scatter', mode: 'lines+markers',
                        x: xVals, y: yVals,
                        name: `μ=${this._mutShort(mut)}, k=${kf}`,
                        line: { color, dash: keepDash[kf] || 'solid', width: 2 },
                        marker: { size: 5, color },
                        hovertemplate: `%{x} → %{y:.1f}%<extra>%{fullData.name}</extra>`,
                    });
                }
            }

            // Zero reference line
            traces.push({
                type: 'scatter', mode: 'lines', x: [uniqueNs[0], uniqueNs[uniqueNs.length-1]], y: [0, 0],
                line: { color: 'rgba(255,255,255,0.2)', dash: 'dash', width: 1 },
                showlegend: false, hoverinfo: 'skip',
            });

            Plotly.react(containerId, traces, this._plotlyLayout({
                height: 420,
                xaxis: { title: 'Population Size', type: 'log', ...this._plotlyAxisStyle(),
                    tickvals: uniqueNs, ticktext: uniqueNs.map(n => n >= 1e6 ? `${(n/1e6)}M` : `${(n/1e3)}K`) },
                yaxis: { title: `% Change from N=${baselineN >= 1e6 ? (baselineN/1e6)+'M' : (baselineN/1e3)+'K'}`, ...this._plotlyAxisStyle(), range: yRange },
                margin: { t: 20, b: 60, l: 70, r: 30 }, legend: { font: { size: 10 } },
            }), { responsive: true });
        };

        // Compute global y-range across both metrics for matched axes
        const allYVals = [];
        const collectY = (metric) => {
            for (const mut of mutKeys) {
                for (const kf of keepVals) {
                    const baseline = getMean(metric, mut, kf, baselineN);
                    if (!baseline || baseline === 0) continue;
                    for (const n of uniqueNs) {
                        const val = getMean(metric, mut, kf, n);
                        if (val !== null) allYVals.push(((val - baseline) / Math.abs(baseline)) * 100);
                    }
                }
            }
        };
        collectY('final_mean_affinity');
        collectY('final_shannon');
        const yPad = 10;
        const sharedRange = [Math.min(...allYVals) - yPad, Math.max(...allYVals) + yPad];

        buildRelChange('final_mean_affinity', 'relchange-affinity', 'Affinity', sharedRange);
        buildRelChange('final_shannon', 'relchange-shannon', 'Shannon H', sharedRange);
    },

    // ═══════════════════════════════════════════
    //  BOX PLOTS BY N
    // ═══════════════════════════════════════════
    renderBoxPlotsByN() {
        const runs = this.allRuns;
        if (!runs.length) return;

        const uniqueNs = [...new Set(runs.map(r => r.target_n))].sort((a, b) => a - b);
        const nLabel = n => n >= 1e6 ? `${(n/1e6)}M` : `${(n/1e3)}K`;

        const buildBox = (metric, containerId, metricLabel) => {
            const traces = uniqueNs.map((n, i) => ({
                type: 'box',
                y: runs.filter(r => r.target_n === n).map(r => r[metric]),
                name: nLabel(n),
                marker: { color: `hsl(${230 + i * 25}, 70%, 65%)`, outliercolor: `hsl(${230 + i * 25}, 70%, 45%)` },
                boxmean: 'sd',
                jitter: 0.3,
                pointpos: -1.5,
                boxpoints: 'all',
            }));

            Plotly.react(containerId, traces, this._plotlyLayout({
                height: 420,
                xaxis: { title: 'Population Size (target_n)', ...this._plotlyAxisStyle() },
                yaxis: { title: metricLabel, ...this._plotlyAxisStyle() },
                margin: { t: 20, b: 60, l: 70, r: 30 },
                showlegend: false,
            }), { responsive: true });
        };

        buildBox('final_mean_affinity', 'boxplot-affinity', 'Mean Affinity');
        buildBox('final_shannon', 'boxplot-shannon', 'Mean Shannon H');
    },

    // ═══════════════════════════════════════════
    //  SHANNON H CHANGE BY SELECTION PRESSURE
    // ═══════════════════════════════════════════
    renderSelectionDiversity() {
        const runs = this.allRuns;
        if (!runs.length) return;

        const uniqueNs = [...new Set(runs.map(r => r.target_n))].sort((a, b) => a - b);
        const baselineN = uniqueNs[0];
        const nLabel = n => n >= 1e6 ? `${(n/1e6)}M` : `${(n/1e3)}K`;
        const mutKeys = [...new Set(runs.map(r => r.paper_mutation_rate))].sort((a, b) => a - b);
        const keepVals = [...new Set(runs.map(r => r.keep_fraction))].sort((a, b) => a - b);

        const getMean = (metric, mut, kf, n) => {
            const m = runs.filter(r =>
                Math.abs(r.paper_mutation_rate - mut) / mut < 0.15 &&
                r.keep_fraction === kf && r.target_n === n
            );
            return m.length ? m.reduce((s, r) => s + r[metric], 0) / m.length : null;
        };

        const keepColors = { 0.05: '#ef4444', 0.1: '#f59e0b', 0.3: '#10b981' };
        const keepNames = { 0.05: 'k=0.05 (strict)', 0.1: 'k=0.1 (moderate)', 0.3: 'k=0.3 (lenient)' };

        // ── Welch's t-test (two-tailed) ──
        const welchT = (a, b) => {
            if (a.length < 2 || b.length < 2) return 1;
            const mA = a.reduce((s,v)=>s+v,0)/a.length, mB = b.reduce((s,v)=>s+v,0)/b.length;
            const vA = a.reduce((s,v)=>s+(v-mA)**2,0)/(a.length-1), vB = b.reduce((s,v)=>s+(v-mB)**2,0)/(b.length-1);
            const se = Math.sqrt(vA/a.length + vB/b.length);
            if (se === 0) return 1;
            const t = Math.abs(mA - mB) / se;
            const dfNum = (vA/a.length + vB/b.length)**2;
            const dfDen = (vA/a.length)**2/(a.length-1) + (vB/b.length)**2/(b.length-1);
            const df = dfNum / dfDen;
            // Normal approx for p (works well enough for df > 2)
            const z = t * (1 - 1/(4*df)) / Math.sqrt(1 + t*t/(2*df));
            const nc = (z2) => { // normal CDF
                const p2 = 0.3275911, a1=0.254829592, a2=-0.284496736, a3=1.421413741, a4=-1.453152027, a5=1.061405429;
                const x2 = Math.abs(z2)/Math.SQRT2, tt=1/(1+p2*x2);
                const y2 = 1-(((((a5*tt+a4)*tt)+a3)*tt+a2)*tt+a1)*tt*Math.exp(-x2*x2);
                return z2 < 0 ? (1-y2)/2 : (1+y2)/2;
            };
            return Math.max(2*(1-nc(Math.abs(z))), 1e-10);
        };

        // Collect data per (N, keep)
        const dataMap = {};
        const traces = [];

        for (const kf of keepVals) {
            const xLabels = [], yValues = [];
            for (const n of uniqueNs) {
                if (n === baselineN) continue;
                const vals = [];
                for (const mut of mutKeys) {
                    const base = getMean('final_shannon', mut, kf, baselineN);
                    const val = getMean('final_shannon', mut, kf, n);
                    if (base && val && base !== 0) {
                        const pct = ((val - base) / Math.abs(base)) * 100;
                        xLabels.push(nLabel(n));
                        yValues.push(pct);
                        vals.push(pct);
                    }
                }
                dataMap[`${nLabel(n)}_${kf}`] = vals;
            }
            traces.push({
                type: 'box', y: yValues, x: xLabels,
                name: keepNames[kf] || `k=${kf}`,
                marker: { color: keepColors[kf] || '#6366f1' },
                boxmean: true, jitter: 0.3, pointpos: 0, boxpoints: 'all',
            });
        }

        // Zero reference line
        traces.push({
            type: 'scatter', mode: 'lines',
            x: [nLabel(uniqueNs[1]), nLabel(uniqueNs[uniqueNs.length-1])], y: [0, 0],
            line: { color: 'rgba(255,255,255,0.2)', dash: 'dash', width: 1 },
            showlegend: false, hoverinfo: 'skip',
        });

        // ── Significance annotations ──
        const pToStars = p => p <= 0.001 ? '***' : p <= 0.01 ? '**' : p <= 0.05 ? '*' : 'ns';
        const starColor = s => s === 'ns' ? 'rgba(255,255,255,0.25)' : '#fbbf24';
        let allVals = [];
        for (const k in dataMap) allVals = allVals.concat(dataMap[k]);
        const gMax = allVals.length ? Math.max(...allVals) : 100;

        const annotations = [];
        for (const n of uniqueNs.filter(n => n !== baselineN)) {
            const nl = nLabel(n);
            const strict = dataMap[`${nl}_0.05`] || [];
            const lenient = dataMap[`${nl}_0.3`] || [];
            if (strict.length >= 2 && lenient.length >= 2) {
                const p = welchT(strict, lenient);
                const stars = pToStars(p);
                annotations.push({
                    x: nl, y: gMax + 30, text: `<b>${stars}</b>`, showarrow: false,
                    font: { size: stars === 'ns' ? 10 : 14, color: starColor(stars), family: 'JetBrains Mono, monospace' },
                });
                annotations.push({
                    x: nl, y: gMax + 18, text: `p=${p < 0.001 ? p.toExponential(1) : p.toFixed(3)}`, showarrow: false,
                    font: { size: 9, color: 'rgba(255,255,255,0.35)', family: 'JetBrains Mono, monospace' },
                });
            }
        }
        annotations.push({
            x: 1, y: 1.02, xref: 'paper', yref: 'paper', xanchor: 'right', showarrow: false,
            text: "Welch's t-test: strict (k=0.05) vs lenient (k=0.3) · * p<0.05 · ** p<0.01 · *** p<0.001",
            font: { size: 10, color: 'rgba(255,255,255,0.35)' },
        });

        Plotly.react('boxplot-selection-shannon', traces, this._plotlyLayout({
            height: 520,
            boxmode: 'group',
            xaxis: { title: 'Population Size', ...this._plotlyAxisStyle() },
            yaxis: { title: 'Shannon H — % Change from N=10K', ...this._plotlyAxisStyle() },
            margin: { t: 30, b: 60, l: 70, r: 30 },
            legend: { font: { size: 11 } },
            annotations,
        }), { responsive: true });
    },

    // ═══════════════════════════════════════════
    //  R² HEATMAP
    // ═══════════════════════════════════════════
    renderR2Heatmap() {
        const runs = this.allRuns;
        if (!runs.length) return;

        const uniqueNs = [...new Set(runs.map(r => r.target_n))].sort((a, b) => a - b);
        const nLabel = n => n >= 1e6 ? `${(n/1e6)}M` : `${(n/1e3)}K`;
        const mutKeys = [...new Set(runs.map(r => r.paper_mutation_rate))].sort((a, b) => a - b);
        const keepVals = [...new Set(runs.map(r => r.keep_fraction))].sort((a, b) => a - b);

        // Build condition keys
        const conditions = [];
        for (const mut of mutKeys) for (const kf of keepVals) conditions.push({ mut, kf });

        const getMean = (metric, mut, kf, n) => {
            const m = runs.filter(r =>
                Math.abs(r.paper_mutation_rate - mut) / mut < 0.15 &&
                r.keep_fraction === kf && r.target_n === n
            );
            return m.length ? m.reduce((s, r) => s + r[metric], 0) / m.length : null;
        };

        const computeR2 = (metric, nA, nB) => {
            const xs = [], ys = [];
            for (const c of conditions) {
                const a = getMean(metric, c.mut, c.kf, nA);
                const b = getMean(metric, c.mut, c.kf, nB);
                if (a !== null && b !== null) { xs.push(a); ys.push(b); }
            }
            if (xs.length < 3) return null;
            const mx = xs.reduce((s,v) => s+v, 0) / xs.length;
            const my = ys.reduce((s,v) => s+v, 0) / ys.length;
            let ssRes = 0, ssTot = 0;
            for (let i = 0; i < xs.length; i++) {
                // R² using identity line (y=x), not best-fit
                ssRes += (ys[i] - xs[i]) ** 2;
                ssTot += (ys[i] - my) ** 2;
            }
            // Pearson R² (correlation)
            let num = 0, dx2 = 0, dy2 = 0;
            for (let i = 0; i < xs.length; i++) {
                num += (xs[i] - mx) * (ys[i] - my);
                dx2 += (xs[i] - mx) ** 2;
                dy2 += (ys[i] - my) ** 2;
            }
            const r = num / Math.sqrt(dx2 * dy2);
            return r * r;
        };

        const buildR2 = (metric, containerId, metricLabel) => {
            const labels = uniqueNs.map(nLabel);
            const z = uniqueNs.map(nA => uniqueNs.map(nB => {
                if (nA === nB) return 1.0;
                return computeR2(metric, nA, nB);
            }));

            // Annotations
            const annotations = [];
            for (let i = 0; i < labels.length; i++) {
                for (let j = 0; j < labels.length; j++) {
                    const val = z[i][j];
                    annotations.push({
                        x: labels[j], y: labels[i],
                        text: val !== null ? val.toFixed(3) : '—',
                        showarrow: false,
                        font: { size: 11, color: val > 0.95 ? '#fff' : '#cbd5e1', family: 'JetBrains Mono, monospace' },
                    });
                }
            }

            Plotly.react(containerId, [{
                type: 'heatmap',
                z, x: labels, y: labels,
                colorscale: [[0, '#7f1d1d'], [0.5, '#78350f'], [0.8, '#14532d'], [0.95, '#065f46'], [1, '#10b981']],
                zmin: 0.5, zmax: 1.0,
                showscale: true,
                colorbar: { title: 'R²', titleside: 'right', tickfont: { color: '#94a3b8' }, titlefont: { color: '#cbd5e1' } },
            }], this._plotlyLayout({
                height: 420,
                xaxis: { title: '', ...this._plotlyAxisStyle(), side: 'bottom' },
                yaxis: { title: '', ...this._plotlyAxisStyle(), autorange: 'reversed' },
                margin: { t: 20, b: 60, l: 60, r: 80 },
                annotations,
            }), { responsive: true });
        };

        buildR2('final_mean_affinity', 'r2-affinity', 'Affinity');
        buildR2('final_shannon', 'r2-shannon', 'Shannon H');
    },

    // ═══════════════════════════════════════════
    //  N VERDICT
    // ═══════════════════════════════════════════
    renderNVerdict() {
        const runs = this.allRuns;
        if (!runs.length) return;

        const uniqueNs = [...new Set(runs.map(r => r.target_n))].sort((a, b) => a - b);
        const baselineN = uniqueNs[0];
        const nLabel = n => n >= 1e6 ? `${(n/1e6)}M` : `${(n/1e3)}K`;
        const mutKeys = [...new Set(runs.map(r => r.paper_mutation_rate))].sort((a, b) => a - b);
        const keepVals = [...new Set(runs.map(r => r.keep_fraction))].sort((a, b) => a - b);

        const conditions = [];
        for (const mut of mutKeys) for (const kf of keepVals) conditions.push({ mut, kf });

        const getMean = (metric, mut, kf, n) => {
            const m = runs.filter(r =>
                Math.abs(r.paper_mutation_rate - mut) / mut < 0.15 &&
                r.keep_fraction === kf && r.target_n === n
            );
            return m.length ? m.reduce((s, r) => s + r[metric], 0) / m.length : null;
        };

        // Compute mean relative change for each metric at largest N
        const largestN = uniqueNs[uniqueNs.length - 1];
        const relChanges = (metric) => {
            const changes = [];
            for (const c of conditions) {
                const base = getMean(metric, c.mut, c.kf, baselineN);
                const val = getMean(metric, c.mut, c.kf, largestN);
                if (base && val && base !== 0) changes.push(((val - base) / Math.abs(base)) * 100);
            }
            if (!changes.length) return { mean: 0, max: 0 };
            return {
                mean: changes.reduce((s, v) => s + v, 0) / changes.length,
                max: Math.max(...changes.map(Math.abs)),
            };
        };

        // Mean R² across all pairs for each metric
        const meanR2 = (metric) => {
            const r2s = [];
            for (let i = 0; i < uniqueNs.length; i++) {
                for (let j = i+1; j < uniqueNs.length; j++) {
                    const xs = [], ys = [];
                    for (const c of conditions) {
                        const a = getMean(metric, c.mut, c.kf, uniqueNs[i]);
                        const b = getMean(metric, c.mut, c.kf, uniqueNs[j]);
                        if (a !== null && b !== null) { xs.push(a); ys.push(b); }
                    }
                    if (xs.length < 3) continue;
                    const mx = xs.reduce((s,v) => s+v, 0) / xs.length;
                    const my = ys.reduce((s,v) => s+v, 0) / ys.length;
                    let num = 0, dx2 = 0, dy2 = 0;
                    for (let k = 0; k < xs.length; k++) {
                        num += (xs[k]-mx)*(ys[k]-my); dx2 += (xs[k]-mx)**2; dy2 += (ys[k]-my)**2;
                    }
                    const r = num / Math.sqrt(dx2 * dy2);
                    r2s.push(r * r);
                }
            }
            return r2s.length ? r2s.reduce((s,v)=>s+v,0)/r2s.length : 0;
        };

        const affRC = relChanges('final_mean_affinity');
        const shaRC = relChanges('final_shannon');
        const affR2 = meanR2('final_mean_affinity');
        const shaR2 = meanR2('final_shannon');

        const affPass = affR2 > 0.95 && affRC.max < 20;
        const shaPass = shaR2 > 0.90;

        const card = document.getElementById('verdict-card');
        card.style.borderLeftColor = (affPass && shaPass) ? 'var(--green)' : 'var(--amber)';

        document.getElementById('verdict-content').innerHTML = `
            <strong style="color:var(--text);font-size:15px;">
                ${affPass && shaPass ? '✅ Population size can be fixed at N=' + nLabel(uniqueNs[1]) + ' for future sweeps'
                    : '⚠️ Population size has some effect — review the plots above'}
            </strong>
            <table style="margin-top:12px;font-size:13px;width:100%;border-collapse:collapse;">
                <thead><tr style="border-bottom:1px solid var(--border);">
                    <th style="text-align:left;padding:6px;">Metric</th>
                    <th style="text-align:right;padding:6px;">Mean R² (all pairs)</th>
                    <th style="text-align:right;padding:6px;">Mean Δ% (${nLabel(baselineN)}→${nLabel(largestN)})</th>
                    <th style="text-align:right;padding:6px;">Max |Δ%|</th>
                    <th style="text-align:center;padding:6px;">Verdict</th>
                </tr></thead>
                <tbody>
                    <tr style="border-bottom:1px solid rgba(255,255,255,0.04);">
                        <td style="padding:6px;">Affinity</td>
                        <td style="text-align:right;padding:6px;font-family:'JetBrains Mono',monospace;">${affR2.toFixed(3)}</td>
                        <td style="text-align:right;padding:6px;font-family:'JetBrains Mono',monospace;">${affRC.mean > 0 ? '+' : ''}${affRC.mean.toFixed(1)}%</td>
                        <td style="text-align:right;padding:6px;font-family:'JetBrains Mono',monospace;">${affRC.max.toFixed(1)}%</td>
                        <td style="text-align:center;padding:6px;">${affPass ? '<span style="color:var(--green);">✓ No effect</span>' : '<span style="color:var(--amber);">⚠ Small effect</span>'}</td>
                    </tr>
                    <tr>
                        <td style="padding:6px;">Shannon H</td>
                        <td style="text-align:right;padding:6px;font-family:'JetBrains Mono',monospace;">${shaR2.toFixed(3)}</td>
                        <td style="text-align:right;padding:6px;font-family:'JetBrains Mono',monospace;">${shaRC.mean > 0 ? '+' : ''}${shaRC.mean.toFixed(1)}%</td>
                        <td style="text-align:right;padding:6px;font-family:'JetBrains Mono',monospace;">${shaRC.max.toFixed(1)}%</td>
                        <td style="text-align:center;padding:6px;">${shaPass ? '<span style="color:var(--green);">✓ No effect</span>' : '<span style="color:var(--amber);">⚠ Some effect</span>'}</td>
                    </tr>
                </tbody>
            </table>
            <p style="margin-top:12px;font-size:12px;">
                <strong>Interpretation:</strong> R² measures whether changing N changes the <em>ranking</em> of conditions.
                R² > 0.95 means the same parameter combinations are best regardless of N.
                Δ% measures the absolute shift in metric value between the smallest and largest N tested.
            </p>
        `;
    },

    // ═══════════════════════════════════════════
    //  DUAL-AXIS TIME COURSES
    // ═══════════════════════════════════════════
    async loadTimeCourses() {
        const btn = document.getElementById('btn-load-timecourses');
        btn.textContent = 'Loading…';
        btn.disabled = true;

        try {
            const runs = this.filteredRuns;
            if (!runs.length) {
                document.getElementById('timecourse-plot').innerHTML = '<p style="color:var(--text-muted);padding:20px;text-align:center;">No runs match current filters.</p>';
                return;
            }

            // Group runs by mutation variant
            const mutKeys = Object.keys(this.MUT_SHORT).map(Number).sort((a,b)=>a-b);
            const groups = {};
            mutKeys.forEach(mk => { groups[mk] = []; });

            runs.forEach(r => {
                const idx = mutKeys.find(mk => Math.abs(r.paper_mutation_rate - mk) / mk < 0.15);
                if (idx !== undefined) groups[idx].push(r);
            });

            // Fetch grouped time-series (returns an array of group objects)
            const res = await fetch(`/api/sweeps/${this.currentSweepId}/grouped-timeseries`);
            const tsData = await res.json(); // array of {rate, rate_key, cycles, mean_affinity, mean_affinity_sem, ...}

            const traces = [];
            const activeGroups = tsData.filter(d => d.cycles && d.cycles.length > 0);

            if (!activeGroups.length) {
                document.getElementById('timecourse-plot').innerHTML = '<p style="color:var(--text-muted);padding:20px;text-align:center;">No time-series data available.</p>';
                return;
            }

            // Build traces for each mutation variant
            activeGroups.forEach(d => {
                const cycles = d.cycles;
                const affMean = d.mean_affinity;
                const affSEM  = d.mean_affinity_sem || affMean.map(() => 0);
                const entMean = d.shannon_entropy;
                const entSEM  = d.shannon_entropy_sem || entMean.map(() => 0);

                // Find label and color from rate_key string (more robust than float comparison)
                const RATE_KEY_MAP = {
                    '3.31e-08': { label: 'Δ28',       color: '#6366f1' },
                    '4.26e-06': { label: 'Double',    color: '#34d399' },
                    '1.04e-05': { label: 'Triple',    color: '#fbbf24' },
                    '1.73e-05': { label: 'Quintuple', color: '#ef4444' },
                };
                const info = RATE_KEY_MAP[d.rate_key] || { label: d.rate_key, color: '#6366f1' };
                const label = info.label;
                const color = info.color;

                // Affinity mean line with data point markers
                traces.push({
                    x: cycles,
                    y: affMean,
                    name: `${label} — Affinity`,
                    line: { color: color, width: 2 },
                    marker: { size: 6, color: color },
                    mode: 'lines+markers',
                    yaxis: 'y',
                    legendgroup: label,
                });
                // Affinity SEM band
                const affUpper = affMean.map((v, i) => v + affSEM[i]);
                const affLower = affMean.map((v, i) => v - affSEM[i]);
                traces.push({
                    x: [...cycles, ...cycles.slice().reverse()],
                    y: [...affUpper, ...affLower.slice().reverse()],
                    fill: 'toself',
                    fillcolor: this._hexToRgba(color, 0.15),
                    line: { color: 'transparent' },
                    showlegend: false,
                    yaxis: 'y',
                    legendgroup: label,
                    hoverinfo: 'skip',
                });

                // Shannon entropy mean line (right y-axis)
                traces.push({
                    x: cycles,
                    y: entMean,
                    name: `${label} — Shannon H`,
                    line: { color: color, width: 2, dash: 'dot' },
                    marker: { size: 6, color: color, symbol: 'diamond' },
                    mode: 'lines+markers',
                    yaxis: 'y2',
                    legendgroup: label,
                });
                // Entropy SEM band
                const entUpper = entMean.map((v, i) => v + entSEM[i]);
                const entLower = entMean.map((v, i) => v - entSEM[i]);
                traces.push({
                    x: [...cycles, ...cycles.slice().reverse()],
                    y: [...entUpper, ...entLower.slice().reverse()],
                    fill: 'toself',
                    fillcolor: this._hexToRgba(color, 0.08),
                    line: { color: 'transparent' },
                    showlegend: false,
                    yaxis: 'y2',
                    legendgroup: label,
                    hoverinfo: 'skip',
                });
            });

            // SEM bands now use proper rgba from _hexToRgba, no post-processing needed

            const axStyle = this._plotlyAxisStyle();
            Plotly.react('timecourse-plot', traces, this._plotlyLayout({
                height: 480,
                xaxis: { title: 'Cycle', ...axStyle },
                yaxis: {
                    title: 'Mean Affinity (solid line, ● markers)',
                    titlefont: { color: '#818cf8' },
                    tickfont: { color: '#818cf8' },
                    ...axStyle,
                    side: 'left',
                },
                yaxis2: {
                    title: 'Shannon H — diversity (dotted, ◆)',
                    titlefont: { color: '#fb923c' },
                    tickfont: { color: '#fb923c' },
                    ...axStyle,
                    overlaying: 'y',
                    side: 'right',
                },
                legend: {
                    font: { color: '#94a3b8', size: 11 },
                    bgcolor: 'rgba(0,0,0,0.3)',
                    x: 0.01, y: 0.99,
                },
                margin: { t: 20, b: 80, l: 70, r: 70 },
                annotations: [{
                    text: 'Shaded bands = mean ± SEM across runs. Grouped by mutation variant using current filters.',
                    xref: 'paper', yref: 'paper', x: 0.5, y: -0.12,
                    showarrow: false, font: { size: 10, color: '#64748b' },
                }],
            }), { responsive: true });

        } catch (err) {
            console.error('Time course load error:', err);
            document.getElementById('timecourse-plot').innerHTML = `<p style="color:#ef4444;padding:20px;">Error: ${err.message}</p>`;
        } finally {
            btn.innerHTML = '<i data-lucide="play" class="lucide-icon btn-icon"></i> Reload time courses';
            btn.disabled = false;
            if (typeof lucide !== 'undefined') lucide.createIcons();
        }
    },

    // ═══════════════════════════════════════════
    //  NOTES
    // ═══════════════════════════════════════════
    async loadNotes() {
        if (!this.currentSweepId) return;
        try {
            const res = await fetch(`/api/sweeps/${this.currentSweepId}/notes`);
            const data = await res.json();
            this._notesContent = data.content || '';
        } catch { this._notesContent = ''; }
        this._renderNotesPreview();
    },

    _renderNotesPreview() {
        const el = document.getElementById('sweep-notes-rendered');
        if (!this._notesContent) {
            el.innerHTML = '<p style="color:var(--text-muted);font-style:italic;">No notes yet. Click Edit to add observations.</p>';
        } else {
            el.innerHTML = typeof marked !== 'undefined' ? marked.parse(this._notesContent) : this._notesContent;
        }
    },

    toggleNotesEditor() {
        const editor = document.getElementById('sweep-notes-editor');
        const rendered = document.getElementById('sweep-notes-rendered');
        const btnEdit = document.getElementById('btn-edit-notes');
        const btnSave = document.getElementById('btn-save-notes');
        const showing = editor.style.display !== 'none';
        if (showing) {
            editor.style.display = 'none';
            rendered.style.display = '';
            btnEdit.innerHTML = '<i data-lucide="edit" class="lucide-icon btn-icon"></i> Edit';
            btnSave.style.display = 'none';
            this._renderNotesPreview();
        } else {
            editor.value = this._notesContent || '';
            editor.style.display = '';
            rendered.style.display = 'none';
            btnEdit.innerHTML = '<i data-lucide="x" class="lucide-icon btn-icon"></i> Cancel';
            btnSave.style.display = '';
        }
        if (typeof lucide !== 'undefined') lucide.createIcons();
    },

    async saveNotes() {
        const editor = document.getElementById('sweep-notes-editor');
        this._notesContent = editor.value;
        try {
            await fetch(`/api/sweeps/${this.currentSweepId}/notes`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content: this._notesContent }),
            });
        } catch (e) { console.error('Save notes failed:', e); }
        this.toggleNotesEditor();
    },
};



// ══════════════════════════════════════════════════════════════
// SWEEP PROGRESS MODULE
// ══════════════════════════════════════════════════════════════
//
// Polls GET /api/sweeps/active every 5 seconds and renders a live
// progress card in the Server Health tab (panel-health).
//
// Architecture:
//   poll() → fetch /api/sweeps/active → render(data) → setTimeout(poll, 5000)
//
// States handled:
//   - idle:      No active or completed sweep. Shows muted "No active sweep".
//   - running:   Animated progress bar, ETA, current run, timing, mini table,
//                live Plotly scatter. Sidebar sim-indicator changes to running.
//   - completed: Green badge, total stats. Polling stops.
//
// Uses setTimeout (not setInterval) to prevent request stacking if the
// server is slow, as specified in the handoff document.

App.sweepProgress = {
    _timer: null,
    _lastStatus: null,

    /**
     * Start the polling loop. Called once from DOMContentLoaded.
     */
    init() {
        this.poll();
    },

    /**
     * Fetch /api/sweeps/active and schedule next poll.
     * Uses setTimeout to avoid stacking requests.
     */
    async poll() {
        try {
            const res = await fetch('/api/sweeps/active');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            this.render(data);
        } catch (e) {
            // Silently ignore — health module already handles connectivity
        }

        // Schedule next poll unless sweep is completed (stop polling)
        if (this._lastStatus !== 'completed') {
            this._timer = setTimeout(() => this.poll(), 5000);
        }
    },

    /**
     * Update the entire sweep progress card DOM based on the API response.
     *
     * @param {Object} data - Response from /api/sweeps/active
     *   data.status can be "idle", "running", or "completed"
     */
    render(data) {
        const status = data.status || 'idle';
        this._lastStatus = status;

        const card = document.getElementById('sweep-progress-card');
        const badge = document.getElementById('sweep-status-badge');
        const idleEl = document.getElementById('sweep-idle-state');
        const activeEl = document.getElementById('sweep-active-state');

        // ── Card styling ──
        card.className = 'card fade-in sweep-progress-card ' + status;
        badge.className = 'card-badge ' + status;

        if (status === 'idle') {
            badge.textContent = 'Idle';
            idleEl.style.display = '';
            activeEl.style.display = 'none';
            this._updateSidebar(false);
            return;
        }

        // Show active state for both running and completed
        idleEl.style.display = 'none';
        activeEl.style.display = '';

        // ── Badge ──
        if (status === 'running') {
            badge.textContent = '● Running';
        } else if (status === 'completed') {
            badge.textContent = '✓ Complete';
        }

        // ── Sweep ID & start time ──
        document.getElementById('sweep-progress-id').textContent = data.sweep_id || '—';
        const startedAt = data.started_at ? new Date(data.started_at).toLocaleString() : '—';
        document.getElementById('sweep-progress-started').textContent = `Started: ${startedAt}`;

        // ── Progress bar ──
        const completed = data.completed || 0;
        const failed = data.failed || 0;
        const total = data.total_runs || 1;
        const done = completed + failed;
        const pct = Math.round((done / total) * 100);

        const barFill = document.getElementById('sweep-bar-fill');
        barFill.style.width = pct + '%';
        barFill.className = 'sweep-bar-fill' +
            (status === 'running' ? ' animated' : '') +
            (status === 'completed' ? ' completed-bar' : '');

        document.getElementById('sweep-bar-text').textContent =
            `${done}/${total} runs (${pct}%)`;

        // ── ETA ──
        if (status === 'running' && data.eta_minutes != null && data.eta_minutes > 0) {
            document.getElementById('sweep-eta-text').textContent =
                `~${Math.round(data.eta_minutes)} min remaining`;
        } else if (status === 'completed') {
            // Show total runtime
            const started = data.started_at ? new Date(data.started_at) : null;
            const finished = data.finished_at ? new Date(data.finished_at) : null;
            if (started && finished) {
                const totalMin = Math.round((finished - started) / 60000);
                document.getElementById('sweep-eta-text').textContent =
                    `Total: ${totalMin} min`;
            } else {
                document.getElementById('sweep-eta-text').textContent = 'Completed';
            }
        } else {
            document.getElementById('sweep-eta-text').textContent = '—';
        }

        // ── Current run ──
        const currentBox = document.getElementById('sweep-current-run-box');
        if (status === 'running' && data.current_run) {
            currentBox.style.display = '';
            document.getElementById('sweep-current-run-id').textContent =
                `Running: ${data.current_run.id || '—'}`;
        } else {
            currentBox.style.display = 'none';
        }

        // ── Timing stats ──
        const timing = data.timing || {};
        if (timing.mean_per_run) {
            document.getElementById('sweep-timing-stats').textContent =
                `Mean: ${timing.mean_per_run}s/run  |  Fastest: ${timing.fastest}s  |  Slowest: ${timing.slowest}s`;
        } else {
            document.getElementById('sweep-timing-stats').textContent = '—';
        }

        // ── Failed runs ──
        const failedEl = document.getElementById('sweep-failed-text');
        if (failed > 0) {
            failedEl.style.display = '';
            failedEl.textContent = `⚠ ${failed} run${failed > 1 ? 's' : ''} failed`;
        } else {
            failedEl.style.display = 'none';
        }

        // ── Mini table (last 5 completed runs) ──
        this._renderMiniTable(data.runs_completed || []);

        // ── Mini Plotly scatter ──
        this._renderMiniChart(data.runs_completed || []);

        // ── Sidebar indicator ──
        this._updateSidebar(status === 'running');
    },

    /**
     * Render the last 5 completed runs into the mini table.
     * @param {Array} runs - Array of completed run objects from progress.json
     */
    _renderMiniTable(runs) {
        const tbody = document.getElementById('sweep-mini-table-body');
        const last5 = runs.slice(-5).reverse();  // most recent first

        if (!last5.length) {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:var(--text-dim);">—</td></tr>';
            return;
        }

        tbody.innerHTML = last5.map(r => `
            <tr>
                <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
                    title="${r.id || '—'}">${r.id || '—'}</td>
                <td>${r.duration_seconds != null ? r.duration_seconds.toFixed(1) + 's' : '—'}</td>
                <td>${r.final_affinity != null ? r.final_affinity.toFixed(4) : '—'}</td>
                <td>${r.final_shannon != null ? r.final_shannon.toFixed(2) : '—'}</td>
            </tr>
        `).join('');
    },

    /**
     * Render a small Plotly scatter showing affinity vs run index
     * for completed runs. Updates as new data arrives.
     *
     * @param {Array} runs - Array of completed run objects
     */
    _renderMiniChart(runs) {
        const container = document.getElementById('sweep-mini-scatter');
        if (!runs.length) {
            Plotly.purge(container);
            return;
        }

        // Filter to runs that have affinity data
        const validRuns = runs.filter(r => r.final_affinity != null);
        if (!validRuns.length) {
            Plotly.purge(container);
            return;
        }

        const x = validRuns.map((_, i) => i + 1);
        const y = validRuns.map(r => r.final_affinity);
        const text = validRuns.map(r => r.id || '');

        Plotly.react(container, [{
            type: 'scatter',
            mode: 'markers',
            x: x,
            y: y,
            text: text,
            hovertemplate: '%{text}<br>Affinity: %{y:.4f}<extra></extra>',
            marker: {
                size: 6,
                color: y,
                colorscale: [[0, '#312e81'], [0.5, '#6366f1'], [1, '#f59e0b']],
                showscale: false,
            },
        }], {
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: '#8b8e9e', family: 'Inter, sans-serif', size: 10 },
            margin: { t: 5, b: 30, l: 45, r: 10 },
            xaxis: {
                title: 'Run #',
                gridcolor: 'rgba(255,255,255,0.05)',
                tickfont: { size: 9, color: '#5c5f72' },
                titlefont: { size: 10, color: '#5c5f72' },
            },
            yaxis: {
                title: 'Affinity',
                gridcolor: 'rgba(255,255,255,0.05)',
                tickfont: { size: 9, color: '#5c5f72' },
                titlefont: { size: 10, color: '#5c5f72' },
            },
            height: 170,
        }, { responsive: true, displayModeBar: false });
    },

    /**
     * Update the sidebar sim-indicator to show running/idle state.
     * @param {boolean} isRunning - Whether a sweep is currently running
     */
    _updateSidebar(isRunning) {
        const indicator = document.getElementById('sim-indicator');
        const text = document.getElementById('sim-indicator-text');
        if (isRunning) {
            indicator.className = 'sim-indicator';
            text.textContent = 'Sweep running…';
        } else {
            indicator.className = 'sim-indicator idle';
            text.textContent = 'No active simulation';
        }
    },
};



// ══════════════════════════════════════════════════════════════
// UTILITIES
// ══════════════════════════════════════════════════════════════

function formatUptime(seconds) {
    if (!seconds || seconds <= 0) return '—';
    const d = Math.floor(seconds / 86400);
    const h = Math.floor((seconds % 86400) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const parts = [];
    if (d > 0) parts.push(`${d}d`);
    parts.push(`${h}h`);
    parts.push(`${m}m`);
    return parts.join(' ');
}


// ══════════════════════════════════════════════════════════════
// INIT
// ══════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
    App.health.init();
    App.sweepProgress.init();
});
