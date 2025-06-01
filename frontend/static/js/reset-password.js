document.addEventListener('DOMContentLoaded', function() {
    initializeResetPassword();
    initializePasswordToggle();
});

function initializeResetPassword() {
    const resetForm = document.getElementById('resetPasswordForm');
    if (!resetForm) return;

    resetForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const token = document.getElementById('resetToken').value;
        const newPassword = document.getElementById('newPassword').value;
        const confirmPassword = document.getElementById('confirmNewPassword').value;

        if (newPassword !== confirmPassword) {
            showMessage('Passwords do not match!', 'error');
            return;
        }

        if (newPassword.length < 8) {
            showMessage('Password must be at least 8 characters long!', 'error');
            return;
        }

        try {
            const response = await fetch(`/auth/reset-password/${token}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    password: newPassword
                })
            });

            const data = await response.json();

            if (data.success) {
                showMessage(data.message, 'success');
                setTimeout(() => {
                    window.location.href = '/';
                }, 2000);
            } else {
                showMessage(data.message, 'error');
            }
        } catch (error) {
            showMessage('An error occurred. Please try again.', 'error');
        }
    });
}

function initializePasswordToggle() {
    document.querySelectorAll('.toggle-password').forEach(icon => {
        icon.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    this.textContent = '🙈';
                } else {
                    input.type = 'password';
                    this.textContent = '👁️';
                }
            }
        });
    });
}

function showMessage(message, type) {
    const messageContainer = document.getElementById('messageContainer');
    if (!messageContainer) return;
    
    messageContainer.textContent = message;
    messageContainer.className = `message-container ${type}`;
    messageContainer.style.display = 'block';

    if (type === 'success') {
        setTimeout(() => {
            messageContainer.style.display = 'none';
        }, 5000);
    }
}
function checkPasswordStrength(password) {
    let strength = 0;
    let feedback = [];

    if (password.length >= 8) strength++;
    else feedback.push('At least 8 characters');

    if (/[A-Z]/.test(password)) strength++;
    else feedback.push('One uppercase letter');

    if (/[a-z]/.test(password)) strength++;
    else feedback.push('One lowercase letter');

    if (/\d/.test(password)) strength++;
    else feedback.push('One number');

    if (/[^A-Za-z0-9]/.test(password)) strength++;
    else feedback.push('One special character');

    return {
        strength: strength,
        feedback: feedback,
        isStrong: strength >= 4
    };
}
