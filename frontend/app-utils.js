(function () {
    const defaultApiBase = 'http://127.0.0.1:8000';
    const configuredApiBase = (window.API_BASE || defaultApiBase).replace(/\/+$/, '');
    const API_BASE = configuredApiBase;

    function buildApiUrl(path) {
        if (!path) {
            return API_BASE;
        }

        if (/^https?:\/\//i.test(path)) {
            return path;
        }

        const normalizedPath = path.startsWith('/') ? path : `/${path}`;
        return `${API_BASE}${normalizedPath}`;
    }

    function getAuthToken() {
        return localStorage.getItem('authToken') || '';
    }

    function clearSession() {
        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
    }

    function redirectToLogin() {
        if (window.location.pathname.endsWith('login.html')) {
            return;
        }
        window.location.href = 'login.html';
    }

    async function parseResponsePayload(response, responseType) {
        if (responseType === 'blob') {
            return response.blob();
        }

        if (responseType === 'text') {
            return response.text();
        }

        const text = await response.text();
        if (!text) {
            return null;
        }

        try {
            return JSON.parse(text);
        } catch {
            return { message: text };
        }
    }

    async function authenticatedFetch(path, options = {}) {
        const token = getAuthToken();
        const headers = new Headers(options.headers || {});

        if (token) {
            headers.set('Authorization', `Bearer ${token}`);
        }

        const hasBody = options.body !== undefined && options.body !== null;
        if (hasBody && !(options.body instanceof FormData) && !headers.has('Content-Type') && !headers.has('content-type')) {
            headers.set('Content-Type', 'application/json');
        }

        const response = await fetch(buildApiUrl(path), {
            ...options,
            headers,
        });

        if (response.status === 401) {
            clearSession();
            redirectToLogin();
            throw new Error('Session expired. Please log in again.');
        }

        const responseType = options.responseType || 'json';
        const data = await parseResponsePayload(response, responseType);
        return { response, data };
    }

    window.API_BASE = API_BASE;
    window.apiUrl = buildApiUrl;
    window.authenticatedFetch = authenticatedFetch;
    window.clearSession = clearSession;
    window.redirectToLogin = redirectToLogin;
})();
