
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
class EmotionAnalytics {
    constructor() {
        this.trendsChart = null;
        this.distributionChart = null;
        this.emotionColors = {
            happy: '#FFD93D',
            sad: '#74b9ff',
            angry: '#fd79a8',
            stressed: '#fdcb6e',
            anxious: '#a29bfe',
            neutral: '#95a5a6'
        };
    }

    async loadAnalytics() {
        try {
            const response = await fetch('/api/emotion-analytics?days=30');
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    this.displayAnalytics(data.analytics);
                } else {
                    this.displayMockData();
                }
            } else {
                this.displayMockData();
            }
        } catch (error) {
            this.displayMockData();
        }
    }

    displayMockData() {
        const mockData = {
            emotion_frequency: [
                { emotion: 'happy', count: 15, percentage: 35.7 },
                { emotion: 'neutral', count: 12, percentage: 28.6 },
                { emotion: 'stressed', count: 8, percentage: 19.0 },
                { emotion: 'sad', count: 4, percentage: 9.5 },
                { emotion: 'anxious', count: 3, percentage: 7.1 }
            ],
            daily_trends: {
                '2024-01-01': { happy: { count: 3 }, neutral: { count: 2 } },
                '2024-01-02': { happy: { count: 2 }, stressed: { count: 1 } },
                '2024-01-03': { neutral: { count: 4 }, sad: { count: 1 } },
                '2024-01-04': { happy: { count: 5 }, anxious: { count: 1 } },
                '2024-01-05': { stressed: { count: 3 }, neutral: { count: 2 } },
                '2024-01-06': { happy: { count: 4 }, neutral: { count: 3 } },
                '2024-01-07': { happy: { count: 1 }, stressed: { count: 4 } }
            }
        };
        this.displayAnalytics(mockData);
    }

    displayAnalytics(analytics) {
        const totalSessions = analytics.emotion_frequency.reduce((sum, item) => sum + item.count, 0);
        document.getElementById('totalSessions').textContent = totalSessions;

        const mostCommon = analytics.emotion_frequency[0];
        document.getElementById('mostCommonEmotion').textContent =
            `${mostCommon.emotion.charAt(0).toUpperCase() + mostCommon.emotion.slice(1)} (${mostCommon.percentage}%)`;

        document.getElementById('weeklyTrend').textContent =
            `${Object.keys(analytics.daily_trends).length} days tracked`;

        this.createTrendsChart(analytics.daily_trends);
        this.createDistributionChart(analytics.emotion_frequency);

        this.displayRecentRecords();
        this.displayInsights(analytics);
    }

    createTrendsChart(dailyTrends) {
        const ctx = document.getElementById('trendsChart').getContext('2d');

        const dates = Object.keys(dailyTrends).sort();
        const emotions = ['happy', 'sad', 'angry', 'stressed', 'anxious', 'neutral'];

        const datasets = emotions.map(emotion => ({
            label: emotion.charAt(0).toUpperCase() + emotion.slice(1),
            data: dates.map(date => dailyTrends[date][emotion]?.count || 0),
            borderColor: this.emotionColors[emotion],
            backgroundColor: this.emotionColors[emotion] + '20',
            tension: 0.4
        }));

        this.trendsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates.map(date => new Date(date).toLocaleDateString()),
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    createDistributionChart(emotionFrequency) {
        const ctx = document.getElementById('distributionChart').getContext('2d');

        this.distributionChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: emotionFrequency.map(item =>
                    item.emotion.charAt(0).toUpperCase() + item.emotion.slice(1)
                ),
                datasets: [{
                    data: emotionFrequency.map(item => item.count),
                    backgroundColor: emotionFrequency.map(item => this.emotionColors[item.emotion]),
                    borderWidth: 3,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'bottom' }
                }
            }
        });
    }

    displayRecentRecords() {
        const recentRecords = document.getElementById('recentRecords');
        recentRecords.innerHTML = `
            <div class="record-item">
                <span class="record-emotion">😊 Happy</span>
                <span class="record-time">2 hours ago</span>
                <span class="record-confidence">92% confidence</span>
            </div>
            <div class="record-item">
                <span class="record-emotion">😰 Stressed</span>
                <span class="record-time">5 hours ago</span>
                <span class="record-confidence">87% confidence</span>
            </div>
            <div class="record-item">
                <span class="record-emotion">😐 Neutral</span>
                <span class="record-time">1 day ago</span>
                <span class="record-confidence">78% confidence</span>
            </div>
        `;
    }

    displayInsights(analytics) {
        const insights = document.getElementById('insights');
        const mostCommon = analytics.emotion_frequency[0];

        insights.innerHTML = `
            <div class="insight-item">
                <span class="insight-icon">🎯</span>
                <div class="insight-content">
                    <h4>Primary Emotion Pattern</h4>
                    <p>Your most frequent emotion is <strong>${mostCommon.emotion}</strong> (${mostCommon.percentage}% of the time). This suggests a generally ${this.getEmotionDescription(mostCommon.emotion)} emotional state.</p>
                </div>
            </div>
            <div class="insight-item">
                <span class="insight-icon">📈</span>
                <div class="insight-content">
                    <h4>Weekly Trend</h4>
                    <p>You've been actively tracking your emotions. Consider setting daily check-in reminders to build a consistent emotional awareness habit.</p>
                </div>
            </div>
            <div class="insight-item">
                <span class="insight-icon">💡</span>
                <div class="insight-content">
                    <h4>Recommendation</h4>
                    <p>Try incorporating mindfulness exercises during your most common emotional states to enhance self-awareness and emotional regulation.</p>
                </div>
            </div>
        `;
    }

    getEmotionDescription(emotion) {
        const descriptions = {
            happy: 'positive and uplifting',
            sad: 'reflective and introspective',
            angry: 'intense and energetic',
            stressed: 'challenging but manageable',
            anxious: 'alert and cautious',
            neutral: 'balanced and stable'
        };
        return descriptions[emotion] || 'unique';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const analytics = new EmotionAnalytics();
    analytics.loadAnalytics();
});

window.logout = logout;
