let emotionDetector = null;

document.addEventListener('DOMContentLoaded', async () => {
    await initializeDashboard();
    setupEventListeners();
    initializeChart();
});
async function initializeDashboard() {
    try {
        emotionDetector = new EmotionDetector();
    } catch (error) {
        showMessage('Error initializing dashboard components', 'error');
    }
}
function setupEventListeners() {
    setupPasswordChangeForm();
    setupPasswordStrengthChecker();
    setupPasswordVisibilityToggles();
    setupEmotionDetectionControls();
    setupChatControls();
}
function showDashboard() {
    document.querySelector('.emotion-detection-section').style.display = 'block';
    document.querySelector('.dashboard-section').style.display = 'block';
    document.getElementById('settingsSection').style.display = 'none';

    document.getElementById('dashboardNav').classList.add('active');
    document.getElementById('settingsNav').classList.remove('active');
}

function showSettings() {
    document.querySelector('.emotion-detection-section').style.display = 'none';
    document.querySelector('.dashboard-section').style.display = 'none';
    document.getElementById('settingsSection').style.display = 'block';

    // Update nav active state
    document.getElementById('dashboardNav').classList.remove('active');
    document.getElementById('settingsNav').classList.add('active');
}

// Logout function
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
        console.error('Logout error:', error);
        alert('Logout failed. Please try again.');
    }
}

// Password change functionality
function setupPasswordChangeForm() {
    const form = document.getElementById('changePasswordForm');
    if (form) {
        form.addEventListener('submit', handlePasswordChange);
    }
}

async function handlePasswordChange(event) {
    event.preventDefault();

    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmNewPassword = document.getElementById('confirmNewPassword').value;
    const messageDiv = document.getElementById('passwordChangeMessage');
    const submitBtn = document.getElementById('changePasswordBtn');

    // Validate passwords match
    if (newPassword !== confirmNewPassword) {
        showPasswordMessage('New passwords do not match!', 'error');
        return;
    }

    // Validate password strength
    if (newPassword.length < 8) {
        showPasswordMessage('Password must be at least 8 characters long!', 'error');
        return;
    }

    // Set loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Updating...';

    try {
        const response = await fetch('/auth/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                current_password: currentPassword,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (data.success) {
            showPasswordMessage(data.message, 'success');
            document.getElementById('changePasswordForm').reset();
            document.getElementById('newPasswordStrength').innerHTML = '';
        } else {
            showPasswordMessage(data.message, 'error');
        }
    } catch (error) {
        showPasswordMessage('An error occurred. Please try again.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="button-emoji">🔐</span> Update Password';
    }
}

function showPasswordMessage(message, type) {
    const messageDiv = document.getElementById('passwordChangeMessage');
    if (messageDiv) {
        messageDiv.style.display = 'block';
        messageDiv.className = `message ${type}`;
        messageDiv.textContent = message;
    }
}

// Password strength checker
function setupPasswordStrengthChecker() {
    const passwordInput = document.getElementById('newPassword');
    if (passwordInput) {
        passwordInput.addEventListener('input', (e) => {
            checkPasswordStrength(e.target.value);
        });
    }
}

function checkPasswordStrength(password) {
    const strengthDiv = document.getElementById('newPasswordStrength');
    if (!strengthDiv) return;

    let strength = 0;
    let feedback = [];

    if (password.length >= 8) strength++;
    else feedback.push('At least 8 characters');

    if (/[a-z]/.test(password)) strength++;
    else feedback.push('Lowercase letter');

    if (/[A-Z]/.test(password)) strength++;
    else feedback.push('Uppercase letter');

    if (/[0-9]/.test(password)) strength++;
    else feedback.push('Number');

    if (/[^A-Za-z0-9]/.test(password)) strength++;
    else feedback.push('Special character');

    const strengthLevels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
    const strengthColors = ['#e74c3c', '#e67e22', '#f39c12', '#27ae60', '#2ecc71'];

    strengthDiv.innerHTML = `
        <div class="strength-bar">
            <div class="strength-fill" style="width: ${(strength / 5) * 100}%; background: ${strengthColors[strength - 1] || '#e74c3c'}"></div>
        </div>
        <div class="strength-text" style="color: ${strengthColors[strength - 1] || '#e74c3c'}">
            ${strengthLevels[strength - 1] || 'Very Weak'}
            ${feedback.length > 0 ? ' - Missing: ' + feedback.join(', ') : ''}
        </div>
    `;
}

// Password visibility toggle
function setupPasswordVisibilityToggles() {
    document.querySelectorAll('.toggle-password').forEach(toggle => {
        toggle.addEventListener('click', () => {
            const targetId = toggle.getAttribute('data-target');
            togglePasswordVisibility(targetId);
        });
    });
}

function togglePasswordVisibility(targetId) {
    const input = document.getElementById(targetId);
    const toggle = document.querySelector(`[data-target="${targetId}"]`);

    if (input && toggle) {
        if (input.type === 'password') {
            input.type = 'text';
            toggle.textContent = '🙈';
        } else {
            input.type = 'password';
            toggle.textContent = '👁️';
        }
    }
}

// Emotion detection controls
function setupEmotionDetectionControls() {
    const startBtn = document.getElementById('startDetection');
    const stopBtn = document.getElementById('stopDetection');

    if (startBtn) {
        startBtn.addEventListener('click', handleStartDetection);
    }

    if (stopBtn) {
        stopBtn.addEventListener('click', handleStopDetection);
    }
}

async function handleStartDetection() {
    const startBtn = document.getElementById('startDetection');
    const stopBtn = document.getElementById('stopDetection');

    try {
        startBtn.disabled = true;
        startBtn.innerHTML = '<span class="loading"></span> Starting camera...';

        // Reset detector state for fresh start
        if (emotionDetector) {
            emotionDetector.reset();
        }

        const initialized = await emotionDetector.initialize();
        if (initialized) {
            document.getElementById('cameraPlaceholder').style.display = 'none';
            document.getElementById('video').style.display = 'block';

            emotionDetector.startDetection();

            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';

            // Show input area when detection starts
            document.getElementById('inputArea').style.display = 'block';

            showMessage('Camera started! Analyzing emotions...', 'success');
        } else {
            showMessage('Failed to start camera. Please check permissions.', 'error');
            startBtn.disabled = false;
            startBtn.innerHTML = '<span class="button-emoji">📸</span> Start Emotion Detection';
        }
    } catch (error) {
        console.error('Error starting detection:', error);
        showMessage('Error starting camera: ' + error.message, 'error');
        startBtn.disabled = false;
        startBtn.innerHTML = '<span class="button-emoji">📸</span> Start Emotion Detection';
    }
}

function handleStopDetection() {
    const startBtn = document.getElementById('startDetection');
    const stopBtn = document.getElementById('stopDetection');

    emotionDetector.stopDetection();

    document.getElementById('video').style.display = 'none';
    document.getElementById('cameraPlaceholder').style.display = 'block';

    // Keep input area visible if there's an ongoing conversation
    const conversationArea = document.getElementById('conversationArea');
    if (conversationArea.children.length === 0) {
        document.getElementById('inputArea').style.display = 'none';
    } else {
        // Keep input area visible for continued chat
        document.getElementById('inputArea').style.display = 'block';
    }

    startBtn.style.display = 'inline-block';
    startBtn.disabled = false;
    startBtn.innerHTML = '<span class="button-emoji">📸</span> Start Emotion Detection';
    stopBtn.style.display = 'none';

    // Only reset emotion display if no conversation exists
    if (conversationArea.children.length === 0) {
        document.getElementById('emotionDisplay').innerHTML = `
            <div class="welcome-message">
                <h3>👋 Welcome to EmotiCare!</h3>
                <p>Start emotion detection to begin our conversation.</p>
            </div>
        `;
    } else {
        // Update emotion display to show chat continues
        document.getElementById('emotionDisplay').innerHTML = `
            <div class="welcome-message">
                <h3>💬 Chat Continues</h3>
                <p>Emotion detection stopped, but I'm still here to chat!</p>
            </div>
        `;
    }

    showMessage('Emotion detection stopped. Chat remains active!', 'info');
}

// Chat controls
function setupChatControls() {
    const sendBtn = document.getElementById('sendResponse');
    const userResponseInput = document.getElementById('userResponse');

    if (sendBtn) {
        sendBtn.addEventListener('click', handleSendMessage);
    }

    if (userResponseInput) {
        userResponseInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });
    }
}

function handleSendMessage() {
    const userResponseInput = document.getElementById('userResponse');
    const userInput = userResponseInput.value.trim();
    
    if (userInput && emotionDetector) {
        const conversationArea = document.getElementById('conversationArea');
        emotionDetector.handleUserResponse(userInput, conversationArea);
        userResponseInput.value = '';
    }
}

// Utility function for showing messages
function showMessage(message, type) {
    // Create a temporary message element
    const messageEl = document.createElement('div');
    messageEl.className = `message-toast ${type}`;
    messageEl.textContent = message;
    messageEl.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 10px;
        color: white;
        font-weight: bold;
        z-index: 1000;
        animation: slideIn 0.3s ease;
        background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
    `;

    document.body.appendChild(messageEl);

    setTimeout(() => {
        messageEl.remove();
    }, 3000);
}

// Initialize chart
function initializeChart() {
    const chartCanvas = document.getElementById('emotionTrendsChart');
    if (chartCanvas) {
        const ctx = chartCanvas.getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Happiness',
                    data: [3, 4, 2, 5, 4, 3, 5],
                    borderColor: '#ffb347',
                    backgroundColor: 'rgba(255, 179, 71, 0.2)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: { beginAtZero: true, max: 5 }
                }
            }
        });
    }
}

// Make functions available globally for HTML onclick handlers
window.showDashboard = showDashboard;
window.showSettings = showSettings;
window.logout = logout;
