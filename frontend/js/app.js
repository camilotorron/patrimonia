/* ============================================
 * Patrimonia — Lógica de la aplicación
 * ============================================ */

/* —— UI helpers —— */

function showNotification(message, type = 'info') {
    const notif = document.createElement('div');
    notif.className = `notification ${type}`;
    notif.textContent = message;
    document.body.appendChild(notif);
    setTimeout(() => notif.remove(), 4000);
}

function formatCurrency(value, currency = 'EUR') {
    const symbols = { EUR: '€', USD: '$', GBP: '£' };
    const symbol = symbols[currency] || currency;
    const num = parseFloat(value) || 0;
    return `${symbol} ${num.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatPercentage(value) {
    const num = parseFloat(value) || 0;
    const sign = num >= 0 ? '+' : '';
    const cls = num >= 0 ? 'positive' : 'negative';
    return `<span class="${cls}">${sign}${num.toFixed(2)}%</span>`;
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('es-ES');
}

/* —— Dashboard —— */

async function loadDashboard() {
    if (!document.getElementById('totalWealth')) return;

    try {
        const summary = await reportsAPI.getSummary();

        document.getElementById('totalWealth').textContent = formatCurrency(summary.total_wealth);
        document.getElementById('totalGain').textContent = formatCurrency(summary.total_gain);
        document.getElementById('totalGainPct').innerHTML = formatPercentage(summary.total_gain_percentage);
        document.getElementById('portfolioValue').textContent = formatCurrency(summary.portfolio_value);
        document.getElementById('cashValue').textContent = formatCurrency(summary.cash);

        // Patrimonio Total: Efectivo vs Inversiones
        renderWealthChart('wealthChart', summary.cash, summary.portfolio_value);

        // Composición por tipo con % y valor en euros
        const comp = await reportsAPI.getComposition();
        if (comp.by_type && comp.by_type.length > 0) {
            renderPieChart('compositionChart',
                comp.by_type.map(c => c.type),
                comp.by_type.map(c => parseFloat(c.value))
            );
        }

    } catch (error) {
        showNotification('Error cargando dashboard: ' + error.message, 'error');
    }
}

/* —— Evolución del Patrimonio Total —— */

let wealthEvolutionChart = null;

const WEALTH_SCALE_OPTIONS = [
    { value: '-1', label: '1 semana', ms: 7 * 86400000 },
    { value: '0', label: '1 mes', ms: 30 * 86400000 },
    { value: '1', label: '6 meses', ms: 180 * 86400000 },
    { value: '2', label: '1 año', ms: 365 * 86400000 },
    { value: '3', label: '2 años', ms: 2 * 365 * 86400000 },
    { value: '4', label: '5 años', ms: 5 * 365 * 86400000 },
    { value: '5', label: 'Total', ms: null },
];

/* Lee la escala activa del primer selector y sincroniza los demás */
function getActiveScaleVal() {
    const selects = document.querySelectorAll('.scale-select, #wealthScaleSelect');
    // Usar el valor del selector que disparó el cambio (el que tiene focus)
    // o el primero si ninguno tiene focus
    let val = '5';
    for (const sel of selects) {
        if (document.activeElement === sel) {
            val = sel.value;
            break;
        }
    }
    if (val === '5') {
        val = selects[0]?.value || '5';
    }
    // Sincronizar todos los selectores al mismo valor
    selects.forEach(sel => { sel.value = val; });
    return val;
}

async function loadWealthEvolution() {
    const canvas = document.getElementById('wealthEvolutionChart');
    if (!canvas) return;

    try {
        const data = await reportsAPI.getWealthEvolution();
        if (!data.points || data.points.length === 0) {
            canvas.parentElement.innerHTML += '<p style="color:var(--text-muted);text-align:center;padding:2rem;">No hay datos de evolución.</p>';
            return;
        }

        // Determinar el rango de fechas según la escala seleccionada
        const scaleVal = getActiveScaleVal();
        const scale = WEALTH_SCALE_OPTIONS.find(s => s.value === scaleVal) || WEALTH_SCALE_OPTIONS[6];

        let points = data.points;
        const now = Date.now();
        if (scale.ms !== null) {
            const minDate = now - scale.ms;
            points = points.filter(p => new Date(p.date).getTime() >= minDate);
            // Asegurar que el primero sea el del inicio del rango
            if (points.length === 0 || new Date(points[0].date).getTime() > minDate) {
                const before = data.points.filter(p => new Date(p.date).getTime() < minDate);
                if (before.length > 0) {
                    points.unshift(before[before.length - 1]);
                }
            }
        }

        if (points.length === 0) {
            canvas.parentElement.innerHTML += '<p style="color:var(--text-muted);text-align:center;padding:2rem;">Sin datos en este rango.</p>';
            return;
        }

        const labels = points.map(p => new Date(p.date));

        if (wealthEvolutionChart) wealthEvolutionChart.destroy();

        wealthEvolutionChart = new Chart(canvas, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Patrimonio Total',
                        data: points.map(p => p.total),
                        borderColor: '#18181b',
                        backgroundColor: 'rgba(24, 24, 27, 0.08)',
                        borderWidth: 3,
                        tension: 0.3,
                        fill: true,
                        pointRadius: 2,
                        pointHoverRadius: 5,
                        spanGaps: true,
                    },
                    {
                        label: 'Inversiones',
                        data: points.map(p => p.investments),
                        borderColor: '#6366f1',
                        backgroundColor: 'rgba(99, 102, 241, 0.05)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false,
                        pointRadius: 2,
                        pointHoverRadius: 5,
                        spanGaps: true,
                    },
                    {
                        label: 'Efectivo',
                        data: points.map(p => p.cash),
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.05)',
                        borderWidth: 2,
                        tension: 0.3,
                        fill: false,
                        pointRadius: 2,
                        pointHoverRadius: 5,
                        spanGaps: true,
                    },
                ]
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { font: { size: 12 }, padding: 12 },
                    },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                return formatCurrency(ctx.parsed.y);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            displayFormats: { day: 'dd/MM/yyyy', month: 'MM/yyyy' },
                            tooltipFormat: 'dd/MM/yyyy',
                        },
                        grid: { display: false },
                        ticks: { maxTicksLimit: 8, font: { size: 11 } },
                    },
                    y: {
                        beginAtZero: false,
                        ticks: {
                            font: { size: 11 },
                            callback: function(value) {
                                if (value >= 1000000) return `€${(value/1000000).toFixed(1)}M`;
                                if (value >= 1000) return `€${(value/1000).toFixed(0)}k`;
                                return `€${value}`;
                            }
                        },
                    },
                },
            },
        });
    } catch (error) {
        showNotification('Error cargando evolución: ' + error.message, 'error');
    }
}

/* —— Evolución de Inversiones por Tipo —— */

let investmentsByTypeChart = null;

const TYPE_COLORS = {
    ETF: '#6366f1',
    Stock: '#10b981',
    Fund: '#f59e0b',
    Crypto: '#ef4444',
    Other: '#8b5cf6',
};

async function loadInvestmentsByType() {
    const canvas = document.getElementById('investmentsByTypeChart');
    if (!canvas) return;

    try {
        const data = await reportsAPI.getWealthEvolution();
        if (!data.points || data.points.length === 0) return;

        // Filtro de escala (compartido con los otros gráficos)
        const scaleVal = getActiveScaleVal();
        const scale = WEALTH_SCALE_OPTIONS.find(s => s.value === scaleVal) || WEALTH_SCALE_OPTIONS[6];
        let points = data.points;
        const now = Date.now();
        if (scale.ms !== null) {
            const minDate = now - scale.ms;
            points = points.filter(p => new Date(p.date).getTime() >= minDate);
            if (points.length === 0 || new Date(points[0].date).getTime() > minDate) {
                const before = data.points.filter(p => new Date(p.date).getTime() < minDate);
                if (before.length > 0) points.unshift(before[before.length - 1]);
            }
        }
        if (points.length === 0) return;

        const labels = points.map(p => new Date(p.date));

        // Descubrir todos los tipos presentes en los datos
        const allTypes = new Set();
        points.forEach(p => Object.keys(p.by_type || {}).forEach(t => allTypes.add(t)));

        const datasets = [...allTypes].map(type => ({
            label: type,
            data: points.map(p => p.by_type?.[type] || 0),
            borderColor: TYPE_COLORS[type] || '#a1a1aa',
            backgroundColor: (TYPE_COLORS[type] || '#a1a1aa') + '15',
            borderWidth: 2,
            tension: 0.3,
            fill: false,
            pointRadius: 2,
            pointHoverRadius: 5,
            spanGaps: true,
        }));

        if (investmentsByTypeChart) investmentsByTypeChart.destroy();

        investmentsByTypeChart = new Chart(canvas, {
            type: 'line',
            data: { labels, datasets },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'bottom', labels: { font: { size: 12 }, padding: 12 } },
                    tooltip: { callbacks: { label: ctx => formatCurrency(ctx.parsed.y) } },
                },
                scales: {
                    x: {
                        type: 'time',
                        time: { displayFormats: { day: 'dd/MM/yyyy', month: 'MM/yyyy' }, tooltipFormat: 'dd/MM/yyyy' },
                        grid: { display: false },
                        ticks: { maxTicksLimit: 8, font: { size: 11 } },
                    },
                    y: {
                        beginAtZero: true,
                        ticks: {
                            font: { size: 11 },
                            callback: function(value) {
                                if (value >= 1000000) return `€${(value/1000000).toFixed(1)}M`;
                                if (value >= 1000) return `€${(value/1000).toFixed(0)}k`;
                                return `€${value}`;
                            }
                        },
                    },
                },
            },
        });
    } catch (error) {
        showNotification('Error cargando evolución por tipo: ' + error.message, 'error');
    }
}

/* —— Evolución del Patrimonio por Banco —— */

let wealthByBankChart = null;

const BANK_COLORS = [
    '#6366f1', '#10b981', '#f59e0b', '#ef4444',
    '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16',
];

async function loadWealthByBank() {
    const canvas = document.getElementById('wealthByBankChart');
    if (!canvas) return;

    try {
        const data = await reportsAPI.getWealthEvolution();
        if (!data.points || data.points.length === 0) return;

        // Filtro de escala (compartido)
        const scaleVal = getActiveScaleVal();
        const scale = WEALTH_SCALE_OPTIONS.find(s => s.value === scaleVal) || WEALTH_SCALE_OPTIONS[6];
        let points = data.points;
        const now = Date.now();
        if (scale.ms !== null) {
            const minDate = now - scale.ms;
            points = points.filter(p => new Date(p.date).getTime() >= minDate);
            if (points.length === 0 || new Date(points[0].date).getTime() > minDate) {
                const before = data.points.filter(p => new Date(p.date).getTime() < minDate);
                if (before.length > 0) points.unshift(before[before.length - 1]);
            }
        }
        if (points.length === 0) return;

        const labels = points.map(p => new Date(p.date));

        // Descubrir todos los bancos presentes
        const allBanks = new Set();
        points.forEach(p => Object.keys(p.by_bank || {}).forEach(b => allBanks.add(b)));

        const bankList = [...allBanks];
        const datasets = bankList.map((bank, i) => ({
            label: bank,
            data: points.map(p => p.by_bank?.[bank] || 0),
            borderColor: BANK_COLORS[i % BANK_COLORS.length],
            backgroundColor: BANK_COLORS[i % BANK_COLORS.length] + '15',
            borderWidth: 2,
            tension: 0.3,
            fill: false,
            pointRadius: 2,
            pointHoverRadius: 5,
            spanGaps: true,
        }));

        if (wealthByBankChart) wealthByBankChart.destroy();

        wealthByBankChart = new Chart(canvas, {
            type: 'line',
            data: { labels, datasets },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'bottom', labels: { font: { size: 12 }, padding: 12 } },
                    tooltip: { callbacks: { label: ctx => formatCurrency(ctx.parsed.y) } },
                },
                scales: {
                    x: {
                        type: 'time',
                        time: { displayFormats: { day: 'dd/MM/yyyy', month: 'MM/yyyy' }, tooltipFormat: 'dd/MM/yyyy' },
                        grid: { display: false },
                        ticks: { maxTicksLimit: 8, font: { size: 11 } },
                    },
                    y: {
                        beginAtZero: false,
                        ticks: {
                            font: { size: 11 },
                            callback: function(value) {
                                if (value >= 1000000) return `€${(value/1000000).toFixed(1)}M`;
                                if (value >= 1000) return `€${(value/1000).toFixed(0)}k`;
                                return `€${value}`;
                            }
                        },
                    },
                },
            },
        });
    } catch (error) {
        showNotification('Error cargando evolución por banco: ' + error.message, 'error');
    }
}

/* —— Cargar los 3 gráficos de evolución a la vez —— */
async function loadAllEvolutionCharts() {
    await Promise.all([
        loadWealthEvolution(),
        loadInvestmentsByType(),
        loadWealthByBank(),
    ]);
}

/* —— Evolution —— */

let evolutionChartInstance = null;

const SCALE_OPTIONS = [
    { value: '0', label: '1 mes', ms: 30 * 86400000 },
    { value: '1', label: '6 meses', ms: 180 * 86400000 },
    { value: '2', label: '1 año', ms: 365 * 86400000 },
    { value: '3', label: '2 años', ms: 2 * 365 * 86400000 },
    { value: '4', label: '5 años', ms: 5 * 365 * 86400000 },
    { value: '5', label: 'Total', ms: null },
];

async function loadEvolution() {
    const canvas = document.getElementById('evolutionChart');
    if (!canvas) return;

    try {
        const data = await accountsAPI.getBalanceEvolution();
        if (!data.accounts || data.accounts.length === 0) {
            canvas.parentElement.innerHTML = '<p style="color:var(--text-muted);text-align:center;padding:2rem;">No hay datos de cuentas.</p>';
            return;
        }

        // Determinar el rango de fechas según la escala seleccionada
        const scaleVal = document.getElementById('scaleSelect')?.value || '3';
        const scale = SCALE_OPTIONS.find(s => s.value === scaleVal) || SCALE_OPTIONS[3];

        let points = data.points;
        const now = Date.now();
        if (scale.ms !== null) {
            const minDate = now - scale.ms;
            points = points.filter(p => new Date(p.date).getTime() >= minDate);
            // Asegurar que el primero sea el del inicio del rango
            if (points.length === 0 || new Date(points[0].date).getTime() > minDate) {
                // Buscar el último punto antes del rango
                const before = data.points.filter(p => new Date(p.date).getTime() < minDate);
                if (before.length > 0) {
                    points.unshift(before[before.length - 1]);
                }
            }
        }

        // Preparar datasets: una línea por cuenta + línea total
        const labels = points.map(p => new Date(p.date));
        const datasets = data.accounts.map(acc => ({
            label: acc.name,
            data: points.map(p => p.balances[String(acc.id)] || null),
            borderColor: acc.color,
            backgroundColor: acc.color + '15',
            borderWidth: 2,
            tension: 0.3,
            fill: false,
            pointRadius: 3,
            pointHoverRadius: 5,
            spanGaps: true,
        }));

        // Línea total (negro)
        datasets.push({
            label: 'Total',
            data: points.map(p => p.balances['total'] || null),
            borderColor: '#18181b',
            backgroundColor: '#18181b15',
            borderWidth: 3,
            tension: 0.3,
            fill: false,
            pointRadius: 3,
            pointHoverRadius: 5,
            spanGaps: true,
        });

        // Eje Y: de 0 a la siguiente centena de millar del máximo
        const maxVal = Math.max(...points.map(p => p.balances['total'] || 0));
        const yMax = Math.ceil(maxVal / 100000) * 100000;

        if (evolutionChartInstance) evolutionChartInstance.destroy();

        evolutionChartInstance = new Chart(canvas, {
            type: 'line',
            data: { labels: labels, datasets: datasets },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { font: { size: 12 }, padding: 12 },
                    },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                const val = ctx.parsed.y;
                                if (val === null) return null;
                                return ` ${ctx.dataset.label}: ${formatCurrency(val)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: scale.value === '0' ? 'day' : scale.value === '1' ? 'week' : 'month',
                        },
                        title: { display: true, text: 'Fecha' },
                    },
                    y: {
                        beginAtZero: true,
                        max: yMax,
                        title: { display: true, text: 'Euros (€)' },
                        ticks: {
                            callback: function(v) { return '€ ' + v.toLocaleString('es-ES'); }
                        }
                    }
                }
            }
        });
    } catch (error) {
        showNotification('Error cargando evolución: ' + error.message, 'error');
    }
}

/* —— Accounts —— */

async function loadAccounts() {
    const tbody = document.getElementById('accountsBody');
    if (!tbody) return;

    try {
        const accounts = await accountsAPI.getAll();
        tbody.innerHTML = accounts.map(a => `
            <tr>
                <td>${a.name}</td>
                <td>${a.bank}</td>
                <td>${a.account_type}</td>
                <td>${formatCurrency(a.current_balance, a.currency)}</td>
                <td>${a.currency}</td>
                <td>${a.is_active ? '✅ Activa' : '❌ Inactiva'}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="openBalanceModal(${a.id}, '${a.name}')">Actualizar Saldo</button>
                    <button class="btn btn-secondary btn-sm" onclick="editAccount(${a.id})">Editar</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteAccount(${a.id})">Eliminar</button>
                </td>
            </tr>
        `).join('') || '<tr><td colspan="7">Sin cuentas</td></tr>';
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="7">Error: ${error.message}</td></tr>`;
    }
}

function openAccountModal() {
    document.getElementById('accountForm').reset();
    document.getElementById('accountId').value = '';
    document.getElementById('accountModalTitle').textContent = 'Nueva Cuenta';
    document.getElementById('accountModal').style.display = 'flex';
}

function closeAccountModal() {
    document.getElementById('accountModal').style.display = 'none';
}

async function editAccount(id) {
    try {
        const account = await accountsAPI.getOne(id);
        document.getElementById('accountId').value = account.id;
        document.getElementById('accName').value = account.name;
        document.getElementById('accType').value = account.account_type;
        document.getElementById('accBank').value = account.bank;
        document.getElementById('accIban').value = account.iban || '';
        document.getElementById('accCurrency').value = account.currency;
        document.getElementById('accBalance').value = account.current_balance;
        document.getElementById('accountModalTitle').textContent = 'Editar Cuenta';
        document.getElementById('accountModal').style.display = 'flex';
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

async function deleteAccount(id) {
    if (!confirm('¿Eliminar esta cuenta?')) return;
    try {
        await accountsAPI.delete(id);
        showNotification('Cuenta eliminada', 'success');
        loadAccounts();
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

/* —— Balance update —— */

let balanceAccountId = null;

function openBalanceModal(id, name) {
    balanceAccountId = id;
    document.getElementById('balanceAccountName').textContent = name;
    document.getElementById('balanceForm').reset();
    // Cargar el saldo actual como valor por defecto
    accountsAPI.getBalance(id).then(data => {
        document.getElementById('newBalance').value = data.balance;
    }).catch(() => {});
    document.getElementById('balanceModal').style.display = 'flex';
}

function closeBalanceModal() {
    document.getElementById('balanceModal').style.display = 'none';
    balanceAccountId = null;
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('balanceForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const balance = parseFloat(document.getElementById('newBalance').value);
            try {
                await accountsAPI.updateBalance(balanceAccountId, balance);
                showNotification('Saldo actualizado', 'success');
                closeBalanceModal();
                loadAccounts();
            } catch (error) {
                showNotification('Error: ' + error.message, 'error');
            }
        });
    }
});

// Account form submit
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('accountForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('accountId').value;
            const data = {
                name: document.getElementById('accName').value,
                account_type: document.getElementById('accType').value,
                bank: document.getElementById('accBank').value,
                iban: document.getElementById('accIban').value || null,
                currency: document.getElementById('accCurrency').value,
                current_balance: parseFloat(document.getElementById('accBalance').value) || 0,
            };
            try {
                if (id) {
                    await accountsAPI.update(id, data);
                    showNotification('Cuenta actualizada', 'success');
                } else {
                    await accountsAPI.create(data);
                    showNotification('Cuenta creada', 'success');
                }
                closeAccountModal();
                loadAccounts();
            } catch (error) {
                showNotification('Error: ' + error.message, 'error');
            }
        });
    }
});

/* —— Assets —— */

async function loadAssets() {
    const tbody = document.getElementById('assetsBody');
    if (!tbody) return;

    try {
        let assets = await assetsAPI.getSnapshot();
        const search = document.getElementById('assetSearch')?.value;
        const typeFilter = document.getElementById('assetTypeFilter')?.value;

        if (search) {
            const q = search.toLowerCase();
            assets = assets.filter(a =>
                a.ticker.toLowerCase().includes(q) ||
                a.name.toLowerCase().includes(q)
            );
        }
        if (typeFilter) {
            assets = assets.filter(a => a.asset_type === typeFilter);
        }

        // —— Filtrar activos sin posición (cantidad 0 o sin valor) ——
        // Se guardan aparte para mostrarlos atenuados al final.
        const activeAssets = assets.filter(a => (parseFloat(a.quantity) || 0) > 0);
        const zeroAssets = assets.filter(a => (parseFloat(a.quantity) || 0) <= 0);

        // —— Agrupar por banco ——
        // Cada activo puede estar en uno o varios bancos; usamos el nombre
        // concatenado como clave de grupo. Los sin banco van a "Sin banco".
        const groups = {};
        for (const a of activeAssets) {
            const bankKey = (a.banks && a.banks.length > 0)
                ? a.banks.join(', ')
                : 'Sin banco';
            if (!groups[bankKey]) groups[bankKey] = [];
            groups[bankKey].push(a);
        }

        // —— Ordenar grupos por valor total descendente ——
        const sortedGroups = Object.entries(groups).map(([bank, items]) => {
            const groupTotal = items.reduce(
                (sum, a) => sum + (parseFloat(a.current_value) || 0), 0
            );
            // Dentro de cada grupo, ordenar de mayor a menor valor
            items.sort((a, b) =>
                (parseFloat(b.current_value) || 0) - (parseFloat(a.current_value) || 0)
            );
            return { bank, items, groupTotal };
        }).sort((a, b) => b.groupTotal - a.groupTotal);

        if (sortedGroups.length === 0 && zeroAssets.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9">Sin activos</td></tr>';
            return;
        }

        // —— Construir filas con cabeceras de grupo ——
        const rows = [];
        for (const { bank, items, groupTotal } of sortedGroups) {
            // Fila cabecera del banco
            rows.push(`
                <tr class="bank-group-header">
                    <td colspan="9">
                        <span class="bank-name">🏦 ${bank}</span>
                        <span class="bank-total">${formatCurrency(groupTotal)}</span>
                    </td>
                </tr>
            `);
            // Filas de activos
            for (const a of items) {
                const qty = parseFloat(a.quantity) || 0;
                const value = parseFloat(a.current_value) || 0;
                const gain = parseFloat(a.gain) || 0;
                const gainPct = parseFloat(a.gain_percentage) || 0;
                const gainCls = gain >= 0 ? 'positive' : 'negative';
                const gainSign = gain >= 0 ? '+' : '';

                // Resaltar fila según rentabilidad
                let rowCls = '';
                if (gainPct >= 5) rowCls = 'row-gain-strong';
                else if (gainPct <= -5) rowCls = 'row-loss-strong';

                rows.push(`
                <tr class="${rowCls}">
                    <td><strong>${a.ticker}</strong></td>
                    <td>${a.name}</td>
                    <td>${a.asset_type}</td>
                    <td>${bank}</td>
                    <td>${a.current_price ? formatCurrency(a.current_price, a.currency) : '—'}</td>
                    <td>${qty.toFixed(4)}</td>
                    <td>${formatCurrency(value, a.currency)}</td>
                    <td class="${gainCls}">${gainSign}${formatCurrency(Math.abs(gain), a.currency)} (${gainSign}${gainPct.toFixed(2)}%)</td>
                    <td>
                        <button class="btn btn-secondary" onclick="editAsset(${a.id})">Editar</button>
                        <button class="btn btn-danger" onclick="deleteAsset(${a.id})">Eliminar</button>
                    </td>
                </tr>
            `);
            }
        }

        // —— Activos sin posición (cantidad 0) al final, atenuados ——
        if (zeroAssets.length > 0) {
            rows.push(`
                <tr class="bank-group-header">
                    <td colspan="9">
                        <span class="bank-name">📪 Sin posición</span>
                        <span class="bank-total">${zeroAssets.length} activo(s)</span>
                    </td>
                </tr>
            `);
            for (const a of zeroAssets) {
                const gain = parseFloat(a.gain) || 0;
                const gainPct = parseFloat(a.gain_percentage) || 0;
                const gainsCls = gain >= 0 ? 'positive' : 'negative';
                const gainSign = gain >= 0 ? '+' : '';
                rows.push(`
                <tr class="row-zero-position">
                    <td><strong>${a.ticker}</strong></td>
                    <td>${a.name}</td>
                    <td>${a.asset_type}</td>
                    <td>—</td>
                    <td>${a.current_price ? formatCurrency(a.current_price, a.currency) : '—'}</td>
                    <td>0.0000</td>
                    <td>—</td>
                    <td class="${gainsCls}">${gainSign}${formatCurrency(Math.abs(gain), a.currency)} (${gainSign}${gainPct.toFixed(2)}%)</td>
                    <td>
                        <button class="btn btn-secondary" onclick="editAsset(${a.id})">Editar</button>
                        <button class="btn btn-danger" onclick="deleteAsset(${a.id})">Eliminar</button>
                    </td>
                </tr>
            `);
            }
        }

        tbody.innerHTML = rows.join('');
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="9">Error: ${error.message}</td></tr>`;
    }
}

function openAssetModal() {
    document.getElementById('assetForm').reset();
    document.getElementById('assetId').value = '';
    document.getElementById('assetModalTitle').textContent = 'Nuevo Activo';
    document.getElementById('assetModal').style.display = 'flex';
}

function closeAssetModal() {
    document.getElementById('assetModal').style.display = 'none';
}

function toggleManualPrice() {
    const checked = document.getElementById('astManualPrice').checked;
    document.getElementById('manualPriceGroup').style.display = checked ? 'block' : 'none';
}

async function editAsset(id) {
    try {
        const asset = await assetsAPI.getOne(id);
        document.getElementById('assetId').value = asset.id;
        document.getElementById('astTicker').value = asset.ticker;
        document.getElementById('astName').value = asset.name;
        document.getElementById('astType').value = asset.asset_type;
        document.getElementById('astCurrency').value = asset.currency;
        document.getElementById('astManualPrice').checked = asset.manual_price;
        if (asset.manual_price) {
            document.getElementById('manualPriceGroup').style.display = 'block';
            document.getElementById('astPrice').value = asset.current_price || '';
        }
        document.getElementById('assetModalTitle').textContent = 'Editar Activo';
        document.getElementById('assetModal').style.display = 'flex';
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

async function deleteAsset(id) {
    if (!confirm('¿Eliminar este activo?')) return;
    try {
        await assetsAPI.delete(id);
        showNotification('Activo eliminado', 'success');
        loadAssets();
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

async function refreshAllPrices() {
    showNotification('Actualizando precios...', 'info');
    try {
        const result = await pricesAPI.refreshAll();
        showNotification(`${result.updated_count} precios actualizados, ${result.failed_count} fallidos`, 'success');
        loadAssets();
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

// Asset form submit
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('assetForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const id = document.getElementById('assetId').value;
            const data = {
                ticker: document.getElementById('astTicker').value,
                name: document.getElementById('astName').value,
                asset_type: document.getElementById('astType').value,
                currency: document.getElementById('astCurrency').value,
                manual_price: document.getElementById('astManualPrice').checked,
            };
            if (data.manual_price) {
                data.current_price = parseFloat(document.getElementById('astPrice').value);
            }
            try {
                if (id) {
                    await assetsAPI.update(id, data);
                    showNotification('Activo actualizado', 'success');
                } else {
                    await assetsAPI.create(data);
                    showNotification('Activo creado', 'success');
                }
                closeAssetModal();
                loadAssets();
            } catch (error) {
                showNotification('Error: ' + error.message, 'error');
            }
        });
    }
});

/* —— Operations —— */

async function loadOperations() {
    const tbody = document.getElementById('operationsBody');
    if (!tbody) return;

    try {
        // Cargar operaciones, assets y cuentas en paralelo para resolver nombres
        const [ops, assets, accounts] = await Promise.all([
            operationsAPI.getAll(),
            assetsAPI.getAll(),
            accountsAPI.getAll(),
        ]);

        const assetMap = new Map(assets.map(a => [a.id, a]));
        const accountMap = new Map(accounts.map(a => [a.id, a]));

        tbody.innerHTML = ops.map(op => {
            const asset = assetMap.get(op.asset_id);
            const account = accountMap.get(op.account_id);
            const assetLabel = asset ? `${asset.ticker}` : `#${op.asset_id}`;
            const accountLabel = account ? `${account.name}` : `#${op.account_id}`;
            return `
            <tr>
                <td>${formatDate(op.operation_date)}</td>
                <td>${op.operation_type === 'Buy' ? '📈 Compra' : '📉 Venta'}</td>
                <td>${assetLabel}</td>
                <td>${accountLabel}</td>
                <td>${op.quantity}</td>
                <td>${formatCurrency(op.unit_price)}</td>
                <td>${formatCurrency(op.total_amount)}</td>
                <td>${formatCurrency(op.commission)}</td>
                <td>
                    <button class="btn btn-danger" onclick="deleteOperation(${op.id})">Eliminar</button>
                </td>
            </tr>
        `;
        }).join('') || '<tr><td colspan="9">Sin operaciones</td></tr>';
    } catch (error) {
        tbody.innerHTML = `<tr><td colspan="9">Error: ${error.message}</td></tr>`;
    }
}

// Cache de assets para autofill de precio
let _modalAssets = [];
let _modalAssetMap = {};

function getOpType() {
    return document.querySelector('input[name="opType"]:checked')?.value || 'Buy';
}

function getOpAssetMode() {
    const el = document.querySelector('input[name="opAssetMode"]:checked');
    return el ? el.value : 'existing';
}

function getOpQtyMode() {
    const el = document.querySelector('input[name="opQtyMode"]:checked');
    return el ? el.value : 'units';
}

/* Toggle Buy/Sell: venta siempre usa activo existente */
function onOpTypeChange() {
    const opType = getOpType();
    const modeGroup = document.getElementById('opAssetModeGroup');

    if (opType === 'Sell') {
        // Venta: forzar activo existente, ocultar opción "nuevo"
        modeGroup.style.display = 'none';
        const existingRadio = document.querySelector('input[name="opAssetMode"][value="existing"]');
        if (existingRadio) existingRadio.checked = true;
        onOpAssetModeChange();
    } else {
        // Compra: mostrar ambas opciones
        modeGroup.style.display = 'block';
        onOpAssetModeChange();
    }
}

/* Toggle activo existente / nuevo */
function onOpAssetModeChange() {
    const mode = getOpAssetMode();
    const existingGroup = document.getElementById('opExistingAssetGroup');
    const newFields = document.getElementById('opNewAssetFields');
    const priceInput = document.getElementById('opPrice');

    if (mode === 'new') {
        existingGroup.style.display = 'none';
        newFields.style.display = 'block';
        priceInput.value = '';
    } else {
        existingGroup.style.display = 'block';
        newFields.style.display = 'none';
        onAssetSelected();
    }
}

/* Toggle cantidad por unidades / por importe */
function onOpQtyModeChange() {
    const mode = getOpQtyMode();
    const unitsGroup = document.getElementById('opQtyUnitsGroup');
    const amountGroup = document.getElementById('opQtyAmountGroup');

    if (mode === 'amount') {
        unitsGroup.style.display = 'none';
        amountGroup.style.display = 'block';
        calcFromAmount();
    } else {
        unitsGroup.style.display = 'block';
        amountGroup.style.display = 'none';
        calcTotal();
    }
}

/* Autocompletar precio al seleccionar un activo existente */
function onAssetSelected() {
    const select = document.getElementById('opAsset');
    const assetId = parseInt(select.value);
    const asset = _modalAssetMap[assetId];
    if (asset && asset.current_price) {
        document.getElementById('opPrice').value = asset.current_price;
    }
    // Recalcular
    if (getOpQtyMode() === 'amount') calcFromAmount();
    else calcTotal();
}

/* Calcular total cuando se introduce cantidad en unidades */
function calcTotal() {
    const qty = parseFloat(document.getElementById('opQuantity').value) || 0;
    const price = parseFloat(document.getElementById('opPrice').value) || 0;
    const commission = parseFloat(document.getElementById('opCommission').value) || 0;
    const total = qty * price + commission;
    document.getElementById('opTotal').value = total.toFixed(2);
}

/* Calcular cantidad cuando se introduce importe total */
function calcFromAmount() {
    const amount = parseFloat(document.getElementById('opAmount').value) || 0;
    const price = parseFloat(document.getElementById('opPrice').value) || 0;
    const commission = parseFloat(document.getElementById('opCommission').value) || 0;
    document.getElementById('opTotal').value = amount.toFixed(2);
    if (price > 0) {
        const qty = (amount - commission) / price;
        document.getElementById('opQuantity').value = qty.toFixed(8);
    }
}

/* Recalcular al cambiar el precio */
function onPriceInput() {
    if (getOpQtyMode() === 'amount') calcFromAmount();
    else calcTotal();
}

/* Recalcular al cambiar la comisión */
function onCommissionInput() {
    if (getOpQtyMode() === 'amount') calcFromAmount();
    else calcTotal();
}

async function openOperationModal() {
    const form = document.getElementById('operationForm');
    if (form) form.reset();
    document.getElementById('opDate').value = new Date().toISOString().split('T')[0];

    // Cargar selects de assets y accounts
    try {
        const [assets, accounts] = await Promise.all([
            assetsAPI.getAll(),
            accountsAPI.getAll(),
        ]);
        _modalAssets = assets;
        _modalAssetMap = {};
        assets.forEach(a => { _modalAssetMap[a.id] = a; });

        document.getElementById('opAsset').innerHTML = assets.map(a =>
            `<option value="${a.id}">${a.ticker} — ${a.name}</option>`).join('');
        document.getElementById('opAccount').innerHTML = accounts.map(a =>
            `<option value="${a.id}">${a.name} (${a.bank})</option>`).join('');

        // Estado inicial: Compra + existente + unidades
        onOpTypeChange();
        onAssetSelected();
    } catch (error) {
        showNotification('Error cargando datos: ' + error.message, 'error');
    }

    document.getElementById('operationModal').style.display = 'flex';
}

function closeOperationModal() {
    document.getElementById('operationModal').style.display = 'none';
}

async function deleteOperation(id) {
    if (!confirm('¿Eliminar esta operación? Se revertirán los cambios.')) return;
    try {
        await operationsAPI.delete(id);
        showNotification('Operación eliminada', 'success');
        loadOperations();
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

async function importCSV(event) {
    const file = event.target.files[0];
    if (!file) return;
    try {
        const result = await operationsAPI.importCSV(file);
        showNotification(`Importadas: ${result.imported}, Errores: ${result.errors.length}`, 'success');
        loadOperations();
    } catch (error) {
        showNotification('Error: ' + error.message, 'error');
    }
}

// Operation form submit
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('operationForm');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const opType = getOpType();
            const assetMode = getOpAssetMode();
            const qtyMode = getOpQtyMode();

            const accountId = parseInt(document.getElementById('opAccount').value);
            const commission = parseFloat(document.getElementById('opCommission').value) || 0;
            const price = parseFloat(document.getElementById('opPrice').value);
            const opDate = new Date(document.getElementById('opDate').value).toISOString();
            const notes = document.getElementById('opNotes').value || null;

            if (!price || price <= 0) {
                showNotification('El precio unitario es obligatorio', 'error');
                return;
            }

            try {
                // —— 1. Resolver o crear el activo ——
                let assetId;
                if (assetMode === 'new') {
                    // Crear el activo nuevo
                    const ticker = document.getElementById('opNewTicker').value.trim();
                    const name = document.getElementById('opNewName').value.trim();
                    if (!ticker || !name) {
                        showNotification('Ticker y nombre del activo son obligatorios', 'error');
                        return;
                    }
                    const newAsset = await assetsAPI.create({
                        ticker,
                        name,
                        asset_type: document.getElementById('opNewType').value,
                        currency: document.getElementById('opNewCurrency').value,
                        manual_price: true,
                        current_price: price,
                    });
                    assetId = newAsset.id;
                } else {
                    assetId = parseInt(document.getElementById('opAsset').value);
                }

                // —— 2. Calcular cantidad y total ——
                let quantity, totalAmount;
                if (qtyMode === 'amount') {
                    totalAmount = parseFloat(document.getElementById('opAmount').value) || 0;
                    if (totalAmount <= 0) {
                        showNotification('El importe debe ser mayor que 0', 'error');
                        return;
                    }
                    quantity = (totalAmount - commission) / price;
                } else {
                    quantity = parseFloat(document.getElementById('opQuantity').value);
                    if (!quantity || quantity <= 0) {
                        showNotification('La cantidad debe ser mayor que 0', 'error');
                        return;
                    }
                    totalAmount = quantity * price + commission;
                }

                // —— 3. Crear la operación ——
                const data = {
                    asset_id: assetId,
                    account_id: accountId,
                    operation_type: opType,
                    quantity,
                    unit_price: price,
                    commission,
                    operation_date: opDate,
                    notes,
                };
                await operationsAPI.create(data);
                showNotification('Operación creada', 'success');
                closeOperationModal();
                loadOperations();
            } catch (error) {
                showNotification('Error: ' + error.message, 'error');
            }
        });
    }
});

/* —— Reports —— */

async function loadReports() {
    const compBody = document.getElementById('compBody');
    if (!compBody) return;

    try {
        // Composición
        const comp = await reportsAPI.getComposition();
        compBody.innerHTML = comp.by_type.map(c => `
            <tr>
                <td>${c.type}</td>
                <td>${formatCurrency(c.value)}</td>
                <td>${parseFloat(c.percentage).toFixed(2)}%</td>
            </tr>
        `).join('');

        if (comp.by_type.length > 0) {
            renderPieChart('compPieChart',
                comp.by_type.map(c => c.type),
                comp.by_type.map(c => parseFloat(c.value))
            );
        }

        // Rentabilidad
        const returns = await reportsAPI.getReturns();
        const returnsBody = document.getElementById('returnsBody');
        if (returnsBody) {
            returnsBody.innerHTML = returns.items.map(item => `
                <tr>
                    <td>${item.ticker}</td>
                    <td>${item.name}</td>
                    <td>${formatCurrency(item.realized_gain)}</td>
                    <td>${formatCurrency(item.unrealized_gain)}</td>
                    <td>${formatCurrency(item.total_gain)}</td>
                    <td>${formatPercentage(item.return_percentage)}</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        showNotification('Error cargando reportes: ' + error.message, 'error');
    }
}

/* —— Tabs —— */

function switchTab(tabName, button) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    button.classList.add('active');
    document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');
    document.getElementById(`tab-${tabName}`).style.display = 'block';
}
