document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = window.API_BASE || 'http://127.0.0.1:8000';

    // If the user already has an active token, redirect to the main page.
    const token = localStorage.getItem('authToken');
    if (token) {
        window.location.href = 'index.html';
        return;
    }

    const loginForm = document.getElementById('loginForm');
    const errorContainer = document.getElementById('formError');

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        errorContainer.classList.add('hidden');

        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        if (!email || !password) {
            showError('Please enter both email and password.');
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });

            const text = await response.text();
            let payload = {};
            try {
                payload = text ? JSON.parse(text) : {};
            } catch {
                payload = { message: text };
            }

            if (!response.ok) {
                throw new Error(payload.detail || payload.message || 'Login failed.');
            }

            localStorage.setItem('authToken', payload.access_token);
            localStorage.setItem('authUser', JSON.stringify(payload.user));
            window.location.href = 'index.html';
        } catch (error) {
            showError(error.message || `Unable to login. Check backend at ${API_BASE}.`);
        }
    });

    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
    }
});