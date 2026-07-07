document.addEventListener('DOMContentLoaded', () => {
    const API_BASE = 'http://127.0.0.1:8000';
    const form = document.getElementById('forgotPasswordForm');
    const errorContainer = document.getElementById('formError');
    const successContainer = document.getElementById('formSuccess');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        errorContainer.classList.add('hidden');
        successContainer.classList.add('hidden');

        const email = document.getElementById('email').value.trim();
        const newPassword = document.getElementById('newPassword').value;

        if (!email || !newPassword) {
            showError('Please enter both email and new password.');
            return;
        }

        if (newPassword.length < 6) {
            showError('Password must be at least 6 characters long.');
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/forgot-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, new_password: newPassword }),
            });

            const payload = await parseResponsePayload(response);
            if (!response.ok) {
                throw new Error(payload.detail || payload.message || 'Failed to reset password.');
            }

            successContainer.textContent = payload.message || 'Password updated successfully. Log in with your new password.';
            successContainer.classList.remove('hidden');
            form.reset();
        } catch (error) {
            showError(error.message || `Unable to reset password. Check backend at ${API_BASE}.`);
        }
    });

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

    function showError(message) {
        errorContainer.textContent = message;
        errorContainer.classList.remove('hidden');
    }
});
