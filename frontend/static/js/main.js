// main.js
document.addEventListener('DOMContentLoaded', function() {
    const emotionDetector = new EmotionDetector();
    let isLoggedIn = false;
    
    // Check if user is logged in
    checkAuthStatus();
    
    // Initialize emotion detector when user starts detection
    document.getElementById('startDetection').addEventListener('click', async function() {
        this.disabled = true;
        this.innerHTML = '<span class="loading"></span> Initializing...';
        
        const initialized = await emotionDetector.initialize();
        
        if (initialized) {
            this.innerHTML = '<span class="button-emoji">⏹️</span> Stop Detection';
            this.disabled = false;
            this.onclick = function() {
                emotionDetector.stopDetection();
                this.innerHTML = '<span class="button-emoji">📸</span> Start Emotion Detection';
                this.onclick = startDetectionHandler;
            };
            
            emotionDetector.startDetection();
        } else {
            this.innerHTML = '<span class="button-emoji">❌</span> Failed to Initialize';
            setTimeout(() => {
                this.innerHTML = '<span class="button-emoji">📸</span> Start Emotion Detection';
                this.disabled = false;
            }, 3000);
        }
    });
    
    function startDetectionHandler() {
        document.getElementById('startDetection').click();
    }
    
    // Handle user response submission
    document.getElementById('sendResponse').addEventListener('click', function() {
        const userInput = document.getElementById('userResponse').value.trim();
        const conversationArea = document.getElementById('conversationArea');
        
        if (userInput) {
            emotionDetector.handleUserResponse(userInput, conversationArea);
            document.getElementById('userResponse').value = '';
            
            // Save the emotion record
            saveEmotionRecord(userInput);
        }
    });
    
    // Allow Enter key to send response
    document.getElementById('userResponse').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            document.getElementById('sendResponse').click();
        }
    });
    
    async function checkAuthStatus() {
        try {
            const response = await fetch('/check-auth');
            const data = await response.json();
            
            if (data.success) {
                isLoggedIn = true;
                showWelcomeMessage(data.user.username);
            } else {
                showLoginPrompt();
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            showLoginPrompt();
        }
    }
    
    function showWelcomeMessage(username) {
        const header = document.querySelector('.cute-title');
        if (header) {
            header.innerHTML = `Welcome back, ${username}! 😊<br><span style="font-size: 1.2rem; font-weight: normal;">How are you feeling today?</span>`;
        }
    }
    
    function showLoginPrompt() {
        // Redirect to login page or show login modal
        window.location.href = '/login.html';
    }
    
    async function saveEmotionRecord(userResponse) {
        if (!emotionDetector.currentEmotion || !isLoggedIn) return;
        
        try {
            const response = await fetch('/save-emotion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    emotion: emotionDetector.currentEmotion,
                    confidence: 0.8, // You can get this from the actual detection result
                    user_response: userResponse,
                    suggestions: 'Generated suggestions based on emotion'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                console.log('Emotion record saved successfully');
            }
        } catch (error) {
            console.error('Error saving emotion record:', error);
        }
    }
    
    // Logout functionality
    document.querySelector('.logout-btn')?.addEventListener('click', async function(e) {
        e.preventDefault();
        
        try {
            const response = await fetch('/logout');
            if (response.ok) {
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Error logging out:', error);
        }
    });
    
    // Add some fun interactions
    addFloatingElements();
    setupParallaxEffect();
});

function addFloatingElements() {
    const floatingElements = ['🌸', '🌈', '⭐', '💫', '🦋', '🌺'];
    
    setInterval(() => {
        if (Math.random() > 0.7) { // 30% chance every interval
            const element = document.createElement('div');
            element.textContent = floatingElements[Math.floor(Math.random() * floatingElements.length)];
            element.style.cssText = `
                position: fixed;
                font-size: ${Math.random() * 20 + 20}px;
                left: ${Math.random() * window.innerWidth}px;
                top: ${window.innerHeight}px;
                pointer-events: none;
                z-index: 1000;
                animation: floatUp 4s linear forwards;
                opacity: 0.7;
            `;
            
            document.body.appendChild(element);
            
            setTimeout(() => {
                element.remove();
            }, 4000);
        }
    }, 2000);
}

function setupParallaxEffect() {
    let ticking = false;
    
    function updateParallax() {
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        document.querySelector('.paper-background')?.style.setProperty('transform', `translateY(${rate}px)`);
        
        ticking = false;
    }
    
    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestTick);
}

// Add CSS for floating animation
const floatingCSS = `
@keyframes floatUp {
    0% {
        transform: translateY(0) rotate(0deg);
        opacity: 0.7;
    }
    100% {
        transform: translateY(-100vh) rotate(360deg);
        opacity: 0;
    }
}
`;

const style = document.createElement('style');
style.textContent = floatingCSS;
document.head.appendChild(style);
