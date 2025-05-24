// emotion-detection.js
class EmotionDetector {
    constructor() {
        this.model = null;
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.isDetecting = false;
        this.currentEmotion = null;
        
        // Emotion responses and suggestions
        this.emotionResponses = {
            happy: {
                questions: [
                    "That's wonderful! 😊 What's making you feel so happy today?",
                    "I love seeing you smile! What brought this joy to your day?",
                    "Your happiness is contagious! Care to share what's going well?"
                ],
                praises: [
                    "That sounds absolutely amazing! 🌟 Keep embracing these positive moments!",
                    "What a beautiful reason to be happy! 💖 These are the moments that make life special.",
                    "I'm so glad you're experiencing this joy! ✨ Remember to savor these feelings."
                ],
                generalPraise: [
                    "Happiness looks great on you! 😄 Keep shining bright!",
                    "Your positive energy is wonderful! 🌈 Keep spreading those good vibes!",
                    "Seeing you happy makes my day too! 💫 Stay awesome!"
                ]
            },
            sad: {
                questions: [
                    "I can see you're feeling down. 💙 Would you like to talk about what's troubling you?",
                    "It's okay to feel sad sometimes. 🫂 What's weighing on your heart?",
                    "I'm here to listen. 💭 What's making you feel this way?"
                ],
                suggestions: {
                    withReason: [
                        "I understand that must be really difficult for you. Here are some gentle ways to help yourself feel better:",
                        "Thank you for sharing with me. These strategies might help you work through these feelings:",
                        "It takes courage to open up about sadness. Let me offer some supportive suggestions:"
                    ],
                    general: [
                        "Sometimes sadness visits us unexpectedly. Here are some gentle ways to nurture yourself:",
                        "Even when we can't pinpoint why we're sad, we can still care for ourselves. Try these:",
                        "Your feelings are valid, even if you're not sure why you're sad. Consider these self-care ideas:"
                    ]
                },
                activities: [
                    "🎵 Listen to your favorite calming music or songs that comfort you",
                    "📞 Reach out to a trusted friend or family member for a gentle conversation",
                    "📝 Write in a journal about your feelings - sometimes putting thoughts on paper helps",
                    "🚶‍♀️ Take a slow, mindful walk in nature or around your neighborhood",
                    "🫖 Make yourself a warm, comforting drink like tea or hot chocolate",
                    "🛁 Take a warm bath or shower to help relax your body and mind",
                    "📚 Read a book that brings you comfort or watch a feel-good movie",
                    "🧘‍♀️ Try some gentle breathing exercises or meditation",
                    "🎨 Express yourself through creative activities like drawing or crafting",
                    "💤 Ensure you're getting enough rest - sometimes sadness is our body's way of saying we need care"
                ]
            },
            stressed: {
                detection: [
                    "I notice you might be feeling stressed. 😟 Let me help you find some calm.",
                    "Stress can be overwhelming. 💭 Here are some ways to ease that tension:",
                    "Take a deep breath with me. 🌸 Let's work on reducing this stress together."
                ],
                suggestions: [
                    "🌬️ Deep breathing: Inhale for 4 counts, hold for 4, exhale for 6. Repeat 5 times.",
                    "💪 Progressive muscle relaxation: Tense and release each muscle group for 5 seconds.",
                    "📋 Write down what's stressing you and break it into smaller, manageable tasks.",
                    "🏃‍♀️ Do some light physical activity - even 10 minutes can help release tension.",
                    "🎵 Listen to calming music or nature sounds to help your mind relax.",
                    "📱 Step away from screens and technology for a few minutes.",
                    "☕ Stay hydrated and avoid excessive caffeine which can increase stress.",
                    "🗣️ Talk to someone you trust about what's causing your stress.",
                    "⏰ Practice time management and prioritize your most important tasks.",
                    "🛏️ Ensure you're getting quality sleep - stress and poor sleep often feed each other."
                ]
            },
            angry: {
                detection: [
                    "I can sense some anger. 😤 Let's work on channeling this energy positively.",
                    "Anger is a valid emotion. 🔥 Here are some healthy ways to process it:",
                    "Take a moment to breathe. 💨 Let's find constructive ways to handle this anger."
                ],
                suggestions: [
                    "🥊 Physical release: Do jumping jacks, punch a pillow, or go for a vigorous walk.",
                    "🌬️ Deep breathing: Take 10 slow, deep breaths to activate your calm response.",
                    "📝 Write it out: Express your anger in a journal or letter (you don't have to send it).",
                    "🧊 Cool down technique: Hold an ice cube or splash cold water on your face.",
                    "🔢 Count to 100 slowly, focusing only on the numbers.",
                    "🏃‍♀️ Go for a run or do intense exercise to release the energy constructively.",
                    "🎵 Listen to music that matches your mood, then gradually shift to calmer songs.",
                    "🗣️ Talk to someone who can listen without judgment.",
                    "🧘‍♀️ Try a anger-focused meditation or mindfulness exercise.",
                    "⏰ Take a timeout from the situation if possible - sometimes space helps perspective."
                ]
            },
            anxious: {
                detection: [
                    "I notice you might be feeling anxious. 😰 Let's work on grounding techniques together.",
                    "Anxiety can feel overwhelming. 🌊 Here are some ways to find your calm center:",
                    "Your anxiety is understandable. 💭 Let me guide you through some calming strategies."
                ],
                suggestions: [
                    "👀 5-4-3-2-1 grounding: Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
                    "🌬️ Box breathing: Inhale for 4, hold for 4, exhale for 4, hold for 4. Repeat.",
                    "🦶 Feel your feet on the ground and remind yourself you are safe in this moment.",
                    "💭 Challenge anxious thoughts: Ask 'Is this thought helpful? Is it realistic?'",
                    "📱 Use a meditation app for guided anxiety relief (Headspace, Calm, etc.).",
                    "☕ Limit caffeine and sugar which can worsen anxiety symptoms.",
                    "📋 Make a list of what you can and cannot control, focus only on what you can influence.",
                    "🏃‍♀️ Gentle exercise like yoga or walking can help reduce anxiety hormones.",
                    "🛁 Take a warm bath with calming scents like lavender.",
                    "📞 Reach out to your support network - you don't have to face anxiety alone."
                ]
            },
            neutral: {
                detection: [
                    "You seem calm and centered today. 😌 How are you feeling overall?",
                    "I sense a peaceful energy from you. 🕊️ Is there anything on your mind?",
                    "You appear balanced and serene. ⚖️ What would you like to talk about?"
                ],
                suggestions: [
                    "🌱 This is a great time for self-reflection and planning.",
                    "📚 Consider learning something new or picking up a hobby.",
                    "🤝 Reach out to friends or family you haven't connected with lately.",
                    "🎯 Set some goals for the week or month ahead.",
                    "🧘‍♀️ Practice gratitude by listing three things you appreciate today.",
                    "🚶‍♀️ Take a mindful walk and notice the beauty around you.",
                    "📝 Journal about your thoughts and experiences.",
                    "🎨 Engage in a creative activity that brings you joy.",
                    "💪 Focus on healthy habits like exercise, good nutrition, or better sleep.",
                    "🌍 Consider how you might help others or contribute to your community."
                ]
            }
        };
    }

    async initialize() {
        try {
            // Load the emotion detection model
            this.model = await tf.loadLayersModel('/models/emotion_model.json');
            
            // Initialize video stream
            this.video = document.getElementById('video');
            this.canvas = document.getElementById('canvas');
            this.ctx = this.canvas.getContext('2d');
            
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 640, height: 480 } 
            });
            this.video.srcObject = stream;
            
            return true;
        } catch (error) {
            console.error('Error initializing emotion detector:', error);
            return false;
        }
    }

    async detectEmotion() {
        if (!this.model || !this.video) return null;
        
        try {
            // Capture frame from video
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            this.ctx.drawImage(this.video, 0, 0);
            
            // Preprocess image for model
            const imageData = this.ctx.getImageData(0, 0, this.canvas.width, this.canvas.height);
            const tensor = tf.browser.fromPixels(imageData)
                .resizeNearestNeighbor([48, 48])
                .toFloat()
                .expandDims(0)
                .div(255.0);
            
            // Make prediction
            const prediction = await this.model.predict(tensor).data();
            
            // Clean up tensor
            tensor.dispose();
            
            // Map prediction to emotion
            const emotions = ['angry', 'anxious', 'happy', 'neutral', 'sad', 'stressed'];
            const maxIndex = prediction.indexOf(Math.max(...prediction));
            const confidence = prediction[maxIndex];
            
            if (confidence > 0.6) { // Only return if confidence is high enough
                return {
                    emotion: emotions[maxIndex],
                    confidence: confidence
                };
            }
            
            return null;
        } catch (error) {
            console.error('Error detecting emotion:', error);
            return null;
        }
    }

    startDetection() {
        if (this.isDetecting) return;
        
        this.isDetecting = true;
        const detectLoop = async () => {
            if (!this.isDetecting) return;
            
            const result = await this.detectEmotion();
            if (result) {
                this.handleEmotionDetected(result);
            }
            
            setTimeout(detectLoop, 1000); // Check every second
        };
        
        detectLoop();
    }

    stopDetection() {
        this.isDetecting = false;
    }

    handleEmotionDetected(result) {
        this.currentEmotion = result.emotion;
        const emotionDisplay = document.getElementById('emotionDisplay');
        const conversationArea = document.getElementById('conversationArea');
        const interactionSection = document.getElementById('interactionSection');
        
        // Show emotion result
        emotionDisplay.innerHTML = `
            <div class="emotion-badge ${result.emotion}">
                <span class="emotion-emoji">${this.getEmotionEmoji(result.emotion)}</span>
                <span class="emotion-text">Detected: ${result.emotion.charAt(0).toUpperCase() + result.emotion.slice(1)}</span>
                <span class="confidence">Confidence: ${Math.round(result.confidence * 100)}%</span>
            </div>
        `;
        
        // Start conversation based on emotion
        this.startEmotionConversation(result.emotion, conversationArea);
        
        // Show interaction section
        interactionSection.style.display = 'block';
        interactionSection.scrollIntoView({ behavior: 'smooth' });
    }

    startEmotionConversation(emotion, conversationArea) {
        const responses = this.emotionResponses[emotion];
        let message = '';
        
        switch (emotion) {
            case 'happy':
                message = this.getRandomItem(responses.questions);
                break;
            case 'sad':
                message = this.getRandomItem(responses.questions);
                break;
            case 'stressed':
                message = this.getRandomItem(responses.detection);
                this.showSuggestions(emotion, conversationArea);
                return;
            case 'angry':
                message = this.getRandomItem(responses.detection);
                this.showSuggestions(emotion, conversationArea);
                return;
            case 'anxious':
                message = this.getRandomItem(responses.detection);
                this.showSuggestions(emotion, conversationArea);
                return;
            case 'neutral':
                message = this.getRandomItem(responses.detection);
                break;
        }
        
        this.addMessageToConversation(message, 'bot', conversationArea);
    }

    handleUserResponse(userInput, conversationArea) {
        if (!this.currentEmotion) return;
        
        const emotion = this.currentEmotion;
        const responses = this.emotionResponses[emotion];
        
        // Add user message to conversation
        this.addMessageToConversation(userInput, 'user', conversationArea);
        
        // Generate appropriate response
        let botResponse = '';
        
        if (emotion === 'happy') {
            if (userInput.trim().length > 10) {
                // User provided a reason for happiness
                botResponse = this.getRandomItem(responses.praises);
            } else {
                // User didn't provide much detail
                botResponse = this.getRandomItem(responses.generalPraise);
            }
        } else if (emotion === 'sad') {
            if (userInput.trim().length > 10) {
                // User explained their sadness
                botResponse = this.getRandomItem(responses.suggestions.withReason);
                this.showSuggestions(emotion, conversationArea);
                return;
            } else {
                // User didn't explain much
                botResponse = this.getRandomItem(responses.suggestions.general);
                this.showSuggestions(emotion, conversationArea);
                return;
            }
        } else if (emotion === 'neutral') {
            botResponse = "Thank you for sharing! " + this.getRandomItem(responses.suggestions);
        }
        
        setTimeout(() => {
            this.addMessageToConversation(botResponse, 'bot', conversationArea);
        }, 1000);
    }

    showSuggestions(emotion, conversationArea) {
        const responses = this.emotionResponses[emotion];
        let suggestions = [];
        
        if (emotion === 'sad') {
            suggestions = responses.activities;
        } else {
            suggestions = responses.suggestions;
        }
        
        const suggestionList = suggestions.slice(0, 5).map(suggestion => 
            `<li class="suggestion-item">${suggestion}</li>`
        ).join('');
        
        const suggestionMessage = `
            <div class="suggestions-container">
                <h4>Here are some suggestions that might help:</h4>
                <ul class="suggestions-list">
                    ${suggestionList}
                </ul>
                <p class="encouragement">Remember, it's okay to take things one step at a time. You've got this! 💪</p>
            </div>
        `;
        
        setTimeout(() => {
            this.addMessageToConversation(suggestionMessage, 'bot', conversationArea, true);
        }, 1500);
    }

    addMessageToConversation(message, sender, container, isHTML = false) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${sender}-message`;
        
        if (isHTML) {
            messageElement.innerHTML = `
                <div class="message-content">
                    ${message}
                </div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            `;
        } else {
            messageElement.innerHTML = `
                <div class="message-content">
                    ${this.escapeHtml(message)}
                </div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            `;
        }
        
        container.appendChild(messageElement);
        container.scrollTop = container.scrollHeight;
        
        // Add animation
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            messageElement.style.transition = 'all 0.3s ease';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        }, 100);
    }

    getEmotionEmoji(emotion) {
        const emojis = {
            happy: '😊',
            sad: '😢',
            angry: '😠',
            stressed: '😰',
            anxious: '😟',
            neutral: '😐'
        };
        return emojis[emotion] || '🤔';
    }

    getRandomItem(array) {
        return array[Math.floor(Math.random() * array.length)];
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Additional CSS for conversation styling
const conversationCSS = `
.emotion-badge {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
    border: 3px solid #fff;
    background: linear-gradient(45deg, #a8e6cf 0%, #dcedc1 100%);
}

.emotion-badge.sad { background: linear-gradient(45deg, #74b9ff 0%, #a29bfe 100%); }
.emotion-badge.angry { background: linear-gradient(45deg, #fd79a8 0%, #e84393 100%); }
.emotion-badge.stressed { background: linear-gradient(45deg, #fdcb6e 0%, #e17055 100%); }
.emotion-badge.anxious { background: linear-gradient(45deg, #fd79a8 0%, #fdcb6e 100%); }
.emotion-badge.neutral { background: linear-gradient(45deg, #95a5a6 0%, #bdc3c7 100%); }

.emotion-emoji {
    font-size: 2rem;
}

.emotion-text {
    font-size: 1.2rem;
    font-weight: 700;
    color: #fff;
}

.confidence {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.8);
}

.message {
    margin: 15px 0;
    padding: 15px;
    border-radius: 15px;
    max-width: 80%;
}

.bot-message {
    background: linear-gradient(45deg, #74b9ff 0%, #0984e3 100%);
    color: white;
    margin-right: auto;
    border: 3px solid #fff;
}

.user-message {
    background: linear-gradient(45deg, #fd79a8 0%, #e84393 100%);
    color: white;
    margin-left: auto;
    border: 3px solid #fff;
}

.message-content {
    font-size: 1rem;
    line-height: 1.4;
}

.message-time {
    font-size: 0.8rem;
    opacity: 0.7;
    margin-top: 5px;
}

.suggestions-container {
    background: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 15px;
    margin: 10px 0;
}

.suggestions-container h4 {
    color: #fff;
    margin-bottom: 15px;
    font-size: 1.1rem;
}

.suggestions-list {
    list-style: none;
    padding: 0;
}

.suggestion-item {
    background: rgba(255,255,255,0.9);
    color: #333;
    padding: 10px 15px;
    margin: 8px 0;
    border-radius: 10px;
    border: 2px solid #fff;
    font-size: 0.95rem;
}

.encouragement {
    color: #fff;
    font-weight: 700;
    text-align: center;
    margin-top: 15px;
    font-size: 1rem;
}
`;

// Inject the CSS
const style = document.createElement('style');
style.textContent = conversationCSS;
document.head.appendChild(style);
