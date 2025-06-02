let emotionDetector = null;
let dashboardChart = null;
let refreshInterval = null;
let isRealTimeEnabled = true;

document.addEventListener('DOMContentLoaded', async () => {
    await initializeDashboard();
    setupEventListeners();
    await loadRealTimeDashboard();
    startRealTimeUpdates();
});

async function initializeDashboard() {
    try {
        emotionDetector = new EmotionDetector();
        console.log('✅ Dashboard initialized successfully');
    } catch (error) {
        console.error('❌ Error initializing dashboard:', error);
        showMessage('Error initializing dashboard components', 'error');
    }
}

async function loadRealTimeDashboard() {
    console.log('🔄 Loading real-time dashboard data...');

    // Add visual feedback
    addUpdateAnimation();

    try {
        await Promise.all([
            updateRecentEmotions(),
            updateEmotionTrends(),
            updateDashboardStats()
        ]);
        console.log('✅ Dashboard data loaded successfully');
    } catch (error) {
        console.error('❌ Error loading dashboard data:', error);
        showMessage('Error loading dashboard data', 'error');
    }
}

function startRealTimeUpdates() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }

    // Update dashboard every 30 seconds
    refreshInterval = setInterval(async () => {
        if (isRealTimeEnabled) {
            console.log('🔄 Auto-refreshing dashboard...');
            await loadRealTimeDashboard();
        }
    }, 30000);

    console.log('✅ Real-time updates started (30s interval)');
}

function stopRealTimeUpdates() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
        console.log('⏹️ Real-time updates stopped');
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

// Real-time data fetching functions
async function updateRecentEmotions() {
    try {
        const response = await fetch('/api/emotion-history?limit=5');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.records) {
                displayRecentEmotions(data.records);
            } else {
                console.warn('No recent emotions data available');
                displayDefaultRecentEmotions();
            }
        } else {
            throw new Error('Failed to fetch recent emotions');
        }
    } catch (error) {
        console.error('Error fetching recent emotions:', error);
        displayDefaultRecentEmotions();
    }
}

async function updateEmotionTrends() {
    try {
        const response = await fetch('/api/emotion-analytics?days=7');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.analytics) {
                updateTrendsChart(data.analytics);
            } else {
                console.warn('No analytics data available');
                initializeDefaultChart();
            }
        } else {
            throw new Error('Failed to fetch emotion analytics');
        }
    } catch (error) {
        console.error('Error fetching emotion trends:', error);
        initializeDefaultChart();
    }
}

async function updateDashboardStats() {
    try {
        const response = await fetch('/api/emotion-analytics?days=30');
        if (response.ok) {
            const data = await response.json();
            if (data.success && data.analytics) {
                displayDashboardStats(data.analytics);
            }
        }
    } catch (error) {
        console.error('Error fetching dashboard stats:', error);
    }
}

function displayRecentEmotions(records) {
    const recentEmotionsElement = document.getElementById('recentEmotions');
    if (!recentEmotionsElement) return;

    const emotionEmojis = {
        happy: '😊',
        sad: '😢',
        angry: '😠',
        stressed: '😰',
        anxious: '😟',
        peaceful: '😌',
        depressed: '😔',
        neutral: '😐'
    };

    if (records.length === 0) {
        recentEmotionsElement.innerHTML = '<li>No emotions detected yet</li>';
        return;
    }

    const emotionItems = records.map(record => {
        const emoji = emotionEmojis[record.emotion] || '😐';
        const timeAgo = getTimeAgo(new Date(record.timestamp));
        return `<li>${emoji} ${record.emotion.charAt(0).toUpperCase() + record.emotion.slice(1)} - ${timeAgo}</li>`;
    }).join('');

    recentEmotionsElement.innerHTML = emotionItems;
}

function displayDefaultRecentEmotions() {
    const recentEmotionsElement = document.getElementById('recentEmotions');
    if (recentEmotionsElement) {
        recentEmotionsElement.innerHTML = `
            <li>😊 Happy - Today</li>
            <li>😐 Neutral - Yesterday</li>
            <li>😢 Sad - 2 days ago</li>
        `;
    }
}

function getTimeAgo(date) {
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;
    return date.toLocaleDateString();
}

function updateTrendsChart(analytics) {
    const chartCanvas = document.getElementById('emotionTrendsChart');
    if (!chartCanvas) return;

    const ctx = chartCanvas.getContext('2d');

    // Destroy existing chart if it exists
    if (dashboardChart) {
        dashboardChart.destroy();
    }

    // Prepare data from analytics
    const dailyTrends = analytics.daily_trends || {};
    const dates = Object.keys(dailyTrends).sort().slice(-7); // Last 7 days

    const emotionColors = {
        happy: '#FFD93D',
        sad: '#74b9ff',
        angry: '#fd79a8',
        stressed: '#fdcb6e',
        anxious: '#a29bfe',
        peaceful: '#55efc4',
        depressed: '#636e72',
        neutral: '#95a5a6'
    };

    // Get the most common emotions to display
    const emotionFreq = analytics.emotion_frequency || [];
    const topEmotions = emotionFreq.slice(0, 3).map(item => item.emotion);

    if (topEmotions.length === 0) {
        initializeDefaultChart();
        return;
    }

    const datasets = topEmotions.map(emotion => ({
        label: emotion.charAt(0).toUpperCase() + emotion.slice(1),
        data: dates.map(date => {
            const dayData = dailyTrends[date] || {};
            return dayData[emotion]?.count || 0;
        }),
        borderColor: emotionColors[emotion] || '#95a5a6',
        backgroundColor: (emotionColors[emotion] || '#95a5a6') + '20',
        tension: 0.4,
        fill: false
    }));

    const labels = dates.map(date => {
        const d = new Date(date);
        return d.toLocaleDateString('en-US', { weekday: 'short' });
    });

    dashboardChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets
        },
        options: {
            responsive: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: { fontSize: 10 }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 }
                }
            }
        }
    });
}

function initializeDefaultChart() {
    const chartCanvas = document.getElementById('emotionTrendsChart');
    if (!chartCanvas) return;

    const ctx = chartCanvas.getContext('2d');

    if (dashboardChart) {
        dashboardChart.destroy();
    }

    dashboardChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Emotions',
                data: [0, 0, 0, 0, 0, 0, 0],
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

function displayDashboardStats(analytics) {
    // Update achievements based on real data
    const achievementsElement = document.querySelector('.stat-card:nth-child(3) ul');
    if (achievementsElement && analytics.emotion_frequency) {
        const totalSessions = analytics.emotion_frequency.reduce((sum, item) => sum + item.count, 0);
        const uniqueDays = Object.keys(analytics.daily_trends || {}).length;

        let achievements = [];

        if (totalSessions >= 1) achievements.push('🎯 First Emotion Detected');
        if (totalSessions >= 10) achievements.push('🌟 10 Sessions Completed');
        if (totalSessions >= 50) achievements.push('🏆 50 Sessions Milestone');
        if (uniqueDays >= 7) achievements.push('📅 7-Day Streak');
        if (uniqueDays >= 30) achievements.push('🗓️ Monthly Tracker');

        if (achievements.length === 0) {
            achievements.push('🌱 Getting Started');
        }

        achievementsElement.innerHTML = achievements.map(achievement => `<li>${achievement}</li>`).join('');
    }
}

// Enhanced emotion detection integration
function onEmotionDetected(emotion, confidence) {
    console.log(`🎯 Emotion detected: ${emotion} (${confidence})`);

    // Trigger immediate dashboard update when new emotion is detected
    setTimeout(async () => {
        console.log('🔄 Updating dashboard after emotion detection...');
        await loadRealTimeDashboard();
    }, 2000); // Small delay to ensure the emotion is saved to database
}

// Enhanced show dashboard function with real-time loading
async function showDashboard() {
    document.querySelector('.emotion-detection-section').style.display = 'block';
    document.querySelector('.dashboard-section').style.display = 'block';
    document.getElementById('settingsSection').style.display = 'none';

    document.getElementById('dashboardNav').classList.add('active');
    document.getElementById('settingsNav').classList.remove('active');

    // Refresh dashboard data when switching to dashboard view
    await loadRealTimeDashboard();
}

// Add real-time toggle control
function toggleRealTimeUpdates() {
    isRealTimeEnabled = !isRealTimeEnabled;

    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    const toggleBtn = document.getElementById('realTimeToggle');

    if (isRealTimeEnabled) {
        startRealTimeUpdates();
        showMessage('Real-time updates enabled', 'success');

        // Update UI
        if (statusDot) statusDot.classList.remove('inactive');
        if (statusText) statusText.textContent = 'Real-time updates active';
        if (toggleBtn) toggleBtn.textContent = '⏸️';
    } else {
        stopRealTimeUpdates();
        showMessage('Real-time updates disabled', 'info');

        // Update UI
        if (statusDot) statusDot.classList.add('inactive');
        if (statusText) statusText.textContent = 'Real-time updates paused';
        if (toggleBtn) toggleBtn.textContent = '▶️';
    }
}

// Add visual feedback when updating
function addUpdateAnimation() {
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.classList.add('updating');
        setTimeout(() => {
            card.classList.remove('updating');
        }, 500);
    });
}

// Cleanup function for when user leaves the page
window.addEventListener('beforeunload', () => {
    stopRealTimeUpdates();
});

// Make functions available globally for HTML onclick handlers
window.showDashboard = showDashboard;
window.showSettings = showSettings;
window.logout = logout;
window.toggleRealTimeUpdates = toggleRealTimeUpdates;
window.onEmotionDetected = onEmotionDetected;
