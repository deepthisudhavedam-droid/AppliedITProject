document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = 'http://127.0.0.1:8000';

    // Redirect authenticated users back to the main page.
    const token = localStorage.getItem('authToken');
    if (token) {
        window.location.href = 'index.html';
        return;
    }

    const registerForm = document.getElementById('registerForm');
    const errorContainer = document.getElementById('formError');

    registerForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        errorContainer.classList.add('hidden');

        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;

        if (!username || !email || !password) {
            showError('All fields are required.');
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password }),
            });

            const payload = await parseResponsePayload(response);
            if (!response.ok) {
                throw new Error(payload.detail || payload.message || 'Registration failed.');
            }

            window.location.href = 'login.html';
        } catch (error) {
            showError(error.message || `Unable to register. Check backend at ${API_BASE}.`);
        }
    });

    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
    }

    async function parseResponsePayload(response) {
        const text = await response.text();
        let payload = {};
        try {
            payload = text ? JSON.parse(text) : {};
        } catch {
            payload = { message: text };
        }
        return payload;
    }
});