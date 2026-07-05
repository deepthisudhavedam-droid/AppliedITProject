document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = 'http://127.0.0.1:8000';
    const token = localStorage.getItem('authToken');
    const userStorage = localStorage.getItem('authUser');
    const emailInput = document.getElementById('email');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const profileForm = document.getElementById('profileForm');
    const profileError = document.getElementById('profileError');
    const profileSuccess = document.getElementById('profileSuccess');
    const cancelBtn = document.getElementById('cancelBtn');
    const profileBtn = document.getElementById('profileBtn');
    const profileInitial = document.getElementById('profileInitial');

    if (!token || !userStorage) {
        window.location.href = 'login.html';
        return;
    }

    const user = JSON.parse(userStorage);
    usernameInput.value = user.username;
    emailInput.value = user.email;
    if (profileInitial) {
        profileInitial.textContent = (user.username || 'U')[0].toUpperCase();
    }

    document.getElementById('logoutBtn')?.addEventListener('click', async () => {
        await fetch('http://127.0.0.1:8000/logout', {
            method: 'POST',
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }).catch(() => {});

        localStorage.removeItem('authToken');
        localStorage.removeItem('authUser');
        window.location.href = 'login.html';
    });

    profileBtn?.addEventListener('click', () => {
        window.location.href = 'profile.html';
    });

    cancelBtn.addEventListener('click', () => {
        window.location.href = 'index.html';
    });

    profileForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        profileError.classList.add('hidden');
        profileSuccess.classList.add('hidden');

        const email = emailInput.value.trim();
        const password = passwordInput.value;

        if (!email) {
            showError('Email is required.');
            return;
        }

        if (password && password.length < 6) {
            showError('Password must be at least 6 characters long.');
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/me`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ email, password: password || undefined }),
            });

            const payload = await parseResponsePayload(response);
            if (!response.ok) {
                throw new Error(payload.detail || payload.message || 'Unable to update profile.');
            }

            localStorage.setItem('authUser', JSON.stringify(payload));
            showSuccess('Profile updated successfully.');
            passwordInput.value = '';
        } catch (error) {
            showError(error.message || `Unable to update profile. Check backend at ${API_BASE}.`);
        }
    });

    function showError(message) {
        profileError.textContent = message;
        profileError.classList.remove('hidden');
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

    function showSuccess(message) {
        profileSuccess.textContent = message;
        profileSuccess.classList.remove('hidden');
    }
});
