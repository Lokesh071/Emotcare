
async function logout() {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            window.location.href = '/';
        } else {
            alert('Logout failed. Please try again.');
        }
    } catch (error) {
        alert('Logout failed. Please try again.');
    }
}

window.logout = logout;

document.addEventListener('DOMContentLoaded', () => {
});
