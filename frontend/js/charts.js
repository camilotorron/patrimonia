/* ============================================
 * Patrimonia — Gráficos con Chart.js
 * ============================================ */

let compositionChartInstance = null;
let topAssetsChartInstance = null;
let historyChartInstance = null;
let wealthChartInstance = null;

const CHART_COLORS = [
    '#6366f1', '#10b981', '#f59e0b', '#ef4444',
    '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16',
];

/**
 * Doughnut: cómo se divide el patrimonio total (Efectivo vs Inversiones).
 */
function renderWealthChart(canvasId, cash, investments) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (wealthChartInstance) wealthChartInstance.destroy();

    const labels = ['Efectivo', 'Inversiones'];
    const data = [cash, investments];
    const total = cash + investments;
    const colors = ['#10b981', '#6366f1'];

    wealthChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0,
            }],
        },
        options: {
            responsive: true,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { size: 12 },
                        padding: 12,
                        generateLabels: function(chart) {
                            const chartData = chart.data;
                            return chartData.labels.map((label, i) => {
                                const value = chartData.datasets[0].data[i];
                                const pct = total > 0 ? (value / total * 100).toFixed(1) : 0;
                                return {
                                    text: `${label} — ${pct}%`,
                                    fillStyle: chartData.datasets[0].backgroundColor[i],
                                    strokeStyle: chartData.datasets[0].backgroundColor[i],
                                    index: i,
                                };
                            });
                        },
                    },
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const pct = total > 0 ? (value / total * 100).toFixed(1) : 0;
                            return ` ${context.label}: ${formatCurrency(value)} (${pct}%)`;
                        }
                    }
                }
            },
        },
    });
}

/**
 * Crea o actualiza un gráfico de tipo doughnut con % y valor en euros.
 */
function renderPieChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (compositionChartInstance) compositionChartInstance.destroy();

    const total = data.reduce((a, b) => a + b, 0);

    compositionChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: CHART_COLORS,
                borderWidth: 0,
            }],
        },
        options: {
            responsive: true,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        font: { size: 12 },
                        padding: 12,
                        generateLabels: function(chart) {
                            const chartData = chart.data;
                            return chartData.labels.map((label, i) => {
                                const value = chartData.datasets[0].data[i];
                                const pct = total > 0 ? (value / total * 100).toFixed(1) : 0;
                                return {
                                    text: `${label} — ${pct}%`,
                                    fillStyle: chartData.datasets[0].backgroundColor[i],
                                    strokeStyle: chartData.datasets[0].backgroundColor[i],
                                    index: i,
                                };
                            });
                        },
                    },
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed;
                            const pct = total > 0 ? (value / total * 100).toFixed(1) : 0;
                            return ` ${context.label}: ${formatCurrency(value)} (${pct}%)`;
                        }
                    }
                }
            },
        },
    });
}

/**
 * Crea o actualiza un gráfico de barras horizontales.
 */
function renderBarChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (topAssetsChartInstance) topAssetsChartInstance.destroy();

    topAssetsChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Valor (€)',
                data: data,
                backgroundColor: '#2563eb',
            }],
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: { x: { beginAtZero: true } },
        },
    });
}

/**
 * Crea o actualiza un gráfico de línea.
 */
function renderLineChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (historyChartInstance) historyChartInstance.destroy();

    historyChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Patrimonio Total',
                data: data,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                fill: true,
                tension: 0.3,
            }],
        },
        options: {
            responsive: true,
            plugins: { legend: { position: 'bottom' } },
            scales: { y: { beginAtZero: true } },
        },
    });
}
