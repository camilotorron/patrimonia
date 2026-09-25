/* ============================================
 * Patrimonia — Cliente API
 * ============================================ */

const API_BASE = '/api/v1';
const DEFAULT_HEADERS = { 'Content-Type': 'application/json' };

/**
 * Llamada genérica al API con manejo de errores.
 * @param {string} method - HTTP method
 * @param {string} endpoint - Ruta relativa al API base
 * @param {object|null} data - Body para POST/PUT
 * @returns {Promise<any>}
 */
async function apiCall(method, endpoint, data = null) {
    const options = {
        method,
        headers: DEFAULT_HEADERS,
    };
    if (data) {
        options.body = JSON.stringify(data);
    }
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        if (response.status === 204) return null;
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.detail || `HTTP ${response.status}`);
        }
        return result;
    } catch (error) {
        console.error(`API ${method} ${endpoint}:`, error);
        throw error;
    }
}

/* —— Accounts —— */
const accountsAPI = {
    getAll: (params = '') => apiCall('GET', `/accounts${params}`),
    getBalanceEvolution: () => apiCall('GET', '/accounts/balance-evolution'),
    getOne: (id) => apiCall('GET', `/accounts/${id}`),
    create: (data) => apiCall('POST', '/accounts', data),
    update: (id, data) => apiCall('PUT', `/accounts/${id}`, data),
    delete: (id) => apiCall('DELETE', `/accounts/${id}`),
    getBalance: (id) => apiCall('GET', `/accounts/${id}/balance`),
    updateBalance: (id, balance) => apiCall('POST', `/accounts/${id}/balance`, { balance }),
    getBalanceHistory: (id) => apiCall('GET', `/accounts/${id}/balance/history`),
    getSummary: (id) => apiCall('GET', `/accounts/${id}/summary`),
};

/* —— Assets —— */
const assetsAPI = {
    getAll: (params = '') => apiCall('GET', `/assets${params}`),
    getSnapshot: () => apiCall('GET', '/assets/overview/snapshot'),
    getOne: (id) => apiCall('GET', `/assets/${id}`),
    getByTicker: (ticker) => apiCall('GET', `/assets/ticker/${ticker}`),
    search: (query) => apiCall('GET', `/assets/search?query=${encodeURIComponent(query)}`),
    create: (data) => apiCall('POST', '/assets', data),
    update: (id, data) => apiCall('PUT', `/assets/${id}`, data),
    delete: (id) => apiCall('DELETE', `/assets/${id}`),
    getHoldings: (id) => apiCall('GET', `/assets/${id}/holdings`),
};

/* —— Operations —— */
const operationsAPI = {
    getAll: (params = '') => apiCall('GET', `/operations${params}`),
    getOne: (id) => apiCall('GET', `/operations/${id}`),
    create: (data) => apiCall('POST', '/operations', data),
    update: (id, data) => apiCall('PUT', `/operations/${id}`, data),
    delete: (id) => apiCall('DELETE', `/operations/${id}`),
    importCSV: (file) => {
        const formData = new FormData();
        formData.append('file', file);
        return fetch(`${API_BASE}/operations/import`, {
            method: 'POST',
            body: formData,
        }).then(r => r.json());
    },
};

/* —— Prices —— */
const pricesAPI = {
    getHistory: (assetId) => apiCall('GET', `/prices/asset/${assetId}`),
    getLatest: (assetId) => apiCall('GET', `/prices/asset/${assetId}/latest`),
    getCurrent: (assetId) => apiCall('GET', `/prices/asset/${assetId}/current`),
    create: (data) => apiCall('POST', '/prices', data),
    refresh: (assetId) => apiCall('POST', `/prices/refresh/${assetId}`),
    refreshAll: () => apiCall('POST', '/prices/refresh-all'),
    search: (query) => apiCall('GET', `/prices/search?query=${encodeURIComponent(query)}`),
};

/* —— Reports —— */
const reportsAPI = {
    getSummary: () => apiCall('GET', '/reports/summary'),
    getComposition: () => apiCall('GET', '/reports/composition'),
    getReturns: (period = 'all') => apiCall('GET', `/reports/returns?period=${period}`),
    getHistory: (params = '') => apiCall('GET', `/reports/history${params}`),
    getWealthEvolution: () => apiCall('GET', '/reports/wealth-evolution'),
};
