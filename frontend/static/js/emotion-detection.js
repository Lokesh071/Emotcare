// emotion-detection.js
class EmotionDetector {
    constructor() {
        this.model = null;
        this.video = null;
        this.canvas = null;
        this.ctx = null;
        this.isDetecting = false;
        this.currentEmotion = null;
        this.lastDetectedEmotion = null; // Track last emotion for chat continuity
        this.currentRecordId = null;
        this.firstEmotionDetected = false;
        this.sessionFirstEmotion = null;
        this.emotionHistory = [];
        this.sessionStartTime = new Date();
        this.useVisualAI = false; // Use ML detection + AI text responses

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
            // Clean up any existing stream first
            const video = document.getElementById('video');
            if (video && video.srcObject) {
                const existingStream = video.srcObject;
                existingStream.getTracks().forEach(track => track.stop());
                video.srcObject = null;
            }

            // Initialize video stream
            this.video = document.getElementById('video');
            this.canvas = document.getElementById('canvas');
            this.ctx = this.canvas.getContext('2d');

            const stream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                }
            });
            this.video.srcObject = stream;

            // Wait for video to be ready
            return new Promise((resolve) => {
                this.video.onloadedmetadata = () => {
                    this.video.play();
                    console.log('Video stream initialized successfully');
                    resolve(true);
                };
            });
        } catch (error) {
            console.error('Error initializing emotion detector:', error);
            return false;
        }
    }

    async detectEmotion() {
        if (!this.video) return null;

        try {
            // Capture frame from video
            this.canvas.width = this.video.videoWidth;
            this.canvas.height = this.video.videoHeight;
            this.ctx.drawImage(this.video, 0, 0);

            // Use reliable ML detection for emotion, AI for responses
            return await this.detectEmotionWithML();
        } catch (error) {
            console.error('Error detecting emotion:', error);
            return null;
        }
    }

    async detectEmotionWithAI() {
        try {
            // Convert canvas to data URL for AI processing
            const imageDataUrl = this.canvas.toDataURL('image/jpeg', 0.8);

            // Send to AI visual emotion detection endpoint
            const response = await fetch('/api/visual-emotion-detection', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    image: imageDataUrl
                })
            });

            if (!response.ok) {
                throw new Error('Failed to detect emotion with AI');
            }

            const result = await response.json();

            if (result.success && result.emotion) {
                return {
                    emotion: result.emotion,
                    confidence: result.confidence || 0.8,
                    method: 'groq_vision',
                    description: result.description,
                    contextual_message: result.contextual_message
                };
            }

            return null;
        } catch (error) {
            console.error('AI emotion detection error:', error);
            // Fallback to traditional ML detection
            return await this.detectEmotionWithML();
        }
    }

    async detectEmotionWithML() {
        try {
            // Convert canvas to blob for traditional ML processing
            const blob = await new Promise(resolve => {
                this.canvas.toBlob(resolve, 'image/jpeg', 0.8);
            });

            // Create form data
            const formData = new FormData();
            formData.append('image', blob, 'emotion_frame.jpg');

            // Send to traditional ML emotion detection endpoint
            const response = await fetch('/api/detect-emotion', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to detect emotion with ML');
            }

            const result = await response.json();

            if (result.success && result.emotion) {
                return {
                    emotion: result.emotion,
                    confidence: result.confidence || 0.8,
                    method: 'tensorflow',
                    description: `Detected ${result.emotion} emotion using ML model`,
                    record_id: result.record_id
                };
            }

            return null;
        } catch (error) {
            console.error('ML emotion detection error:', error);
            return null;
        }
    }



    startDetection() {
        if (this.isDetecting) {
            console.log('Detection already running, skipping start');
            return;
        }

        console.log('Starting emotion detection...');
        this.isDetecting = true;

        const detectLoop = async () => {
            if (!this.isDetecting) {
                console.log('Detection stopped, exiting loop');
                return;
            }

            try {
                const result = await this.detectEmotion();
                if (result && this.isDetecting) {
                    this.handleEmotionDetected(result);
                }
            } catch (error) {
                console.error('Error in detection loop:', error);
            }

            // Continue loop only if still detecting
            if (this.isDetecting) {
                setTimeout(detectLoop, 1000); // Check every second
            }
        };

        detectLoop();
    }

    stopDetection() {
        this.isDetecting = false;

        // Clear current emotion but keep last detected for chat continuity
        this.currentEmotion = null;

        // Stop camera stream properly
        const video = document.getElementById('video');
        if (video && video.srcObject) {
            const stream = video.srcObject;
            stream.getTracks().forEach(track => {
                track.stop();
                console.log('Stopped track:', track.kind);
            });
            video.srcObject = null;
        }

        // Update button visibility
        const startBtn = document.getElementById('startDetection');
        const stopBtn = document.getElementById('stopDetection');

        if (startBtn) startBtn.style.display = 'inline-block';
        if (stopBtn) stopBtn.style.display = 'none';

        // Hide emotion display but keep chat section visible
        const emotionDisplay = document.getElementById('emotionDisplay');
        if (emotionDisplay) {
            emotionDisplay.style.display = 'none';
        }

        // Keep chat section visible for continued conversation
        const chatSection = document.querySelector('.chat-section');
        if (chatSection) {
            chatSection.style.display = 'flex'; // Keep it visible

            // Add a message indicating detection stopped but chat continues
            const conversationArea = chatSection.querySelector('.conversation-area');
            if (conversationArea && conversationArea.children.length > 0) {
                this.addMessageToConversation(
                    "📷 Emotion detection stopped, but I'm still here to chat with you! Feel free to continue our conversation.",
                    'bot',
                    conversationArea
                );
            }
        }

        console.log('Emotion detection stopped, chat remains active');
    }

    reset() {
        // Reset all detection state for fresh start
        this.isDetecting = false;
        this.currentEmotion = null;
        this.currentRecordId = null;
        this.model = null;

        // Don't reset these for chat continuity:
        // this.lastDetectedEmotion = null;
        // this.firstEmotionDetected = false;
        // this.sessionFirstEmotion = null;
        // this.emotionHistory = [];

        console.log('Emotion detector reset for new session');
    }

    handleEmotionDetected(result) {
        this.currentEmotion = result.emotion;
        this.lastDetectedEmotion = result.emotion; // Store for chat continuity
        this.currentRecordId = result.record_id || null;
        const emotionDisplay = document.getElementById('emotionDisplay');
        const conversationArea = document.getElementById('conversationArea');

        // Track emotion history
        this.emotionHistory.push({
            emotion: result.emotion,
            confidence: result.confidence,
            timestamp: new Date()
        });

        // Check if this is the first emotion detected in this session
        const isFirstEmotion = !this.firstEmotionDetected;
        if (isFirstEmotion) {
            this.firstEmotionDetected = true;
            this.sessionFirstEmotion = result.emotion;
        }

        // Show emotion result with special styling for first emotion
        const badgeClass = isFirstEmotion ? `${result.emotion} first-emotion` : result.emotion;
        const badgeTitle = isFirstEmotion ? 'First Emotion Detected!' : 'Current Emotion';

        emotionDisplay.innerHTML = `
            <div class="emotion-badge ${badgeClass}">
                ${isFirstEmotion ? '<div class="first-emotion-indicator">🌟 First Detection 🌟</div>' : ''}
                <span class="emotion-emoji">${this.getEmotionEmoji(result.emotion)}</span>
                <span class="emotion-text">${badgeTitle}: ${result.emotion.charAt(0).toUpperCase() + result.emotion.slice(1)}</span>
                ${isFirstEmotion ? '<div class="session-context">This will guide our conversation today</div>' : ''}
            </div>
        `;

        // Start conversation - prioritize first emotion or continue existing conversation
        if (isFirstEmotion) {
            // Special first emotion conversation
            this.startFirstEmotionConversation(result.emotion, conversationArea);
        } else if (conversationArea.children.length === 0) {
            // Regular emotion conversation if no conversation exists
            this.startEmotionConversation(result.emotion, conversationArea);
        } else {
            // Update ongoing conversation with new emotion context
            this.updateEmotionContext(result.emotion, conversationArea);
        }
    }

    async startFirstEmotionConversation(emotion, conversationArea) {
        // Special handling for the first emotion detected - more comprehensive and welcoming
        try {
            const welcomeMessage = `Welcome to EmotiCare! I've detected that you're feeling ${emotion} as we begin our session today. This is important - your first emotion helps me understand how to best support you.`;

            const aiResponse = await fetch('/api/ai-chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: welcomeMessage,
                    detected_emotion: emotion,
                    is_first_emotion: true
                })
            });

            if (aiResponse.ok) {
                const data = await aiResponse.json();

                if (data.success) {
                    // Add single comprehensive welcome message for first emotion
                    const welcomeMessage = `🌟 <strong>Welcome to your EmotiCare session!</strong><br>
                    I've detected that you're feeling <strong>${emotion}</strong> as we start today. ${data.reply}`;

                    this.addMessageToConversation(welcomeMessage, 'bot', conversationArea, true);
                } else {
                    this.startEmotionConversationFallback(emotion, conversationArea);
                }
            } else {
                this.startEmotionConversationFallback(emotion, conversationArea);
            }
        } catch (error) {
            console.error('First emotion conversation error:', error);
            this.startEmotionConversationFallback(emotion, conversationArea);
        }
    }

    async updateEmotionContext(newEmotion, conversationArea) {
        // Handle emotion changes during an ongoing conversation
        if (newEmotion !== this.sessionFirstEmotion) {
            const contextMessage = `I notice your emotion has shifted to ${newEmotion}. How are you feeling about this change?`;

            try {
                const aiResponse = await fetch('/api/ai-chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message: contextMessage,
                        detected_emotion: newEmotion,
                        previous_emotion: this.sessionFirstEmotion,
                        emotion_change: true
                    })
                });

                if (aiResponse.ok) {
                    const data = await aiResponse.json();
                    if (data.success) {
                        const changeMessage = `🔄 <strong>Emotion Update:</strong> I've noticed you're now feeling ${newEmotion}. ${data.reply}`;
                        this.addMessageToConversation(changeMessage, 'bot', conversationArea, true);
                    }
                }
            } catch (error) {
                console.error('Emotion context update error:', error);
                const fallbackMessage = `🔄 I notice you're now feeling ${newEmotion}. How has your mood shifted since we started?`;
                this.addMessageToConversation(fallbackMessage, 'bot', conversationArea);
            }
        }
    }

    async startEmotionConversation(emotion, conversationArea) {
        // Use AI chat system for initial conversation
        try {
            const initialMessage = `I just detected that you're feeling ${emotion}`;
            const aiResponse = await fetch('/api/ai-chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: initialMessage,
                    detected_emotion: emotion
                })
            });

            if (aiResponse.ok) {
                const data = await aiResponse.json();

                if (data.success) {
                    // Add single AI response only
                    this.addMessageToConversation(data.reply, 'bot', conversationArea);
                } else {
                    // Fallback to original system
                    this.startEmotionConversationFallback(emotion, conversationArea);
                }
            } else {
                // Fallback to original system
                this.startEmotionConversationFallback(emotion, conversationArea);
            }
        } catch (error) {
            console.error('AI conversation start error:', error);
            // Fallback to original system
            this.startEmotionConversationFallback(emotion, conversationArea);
        }
    }

    startEmotionConversationFallback(emotion, conversationArea) {
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

    async handleUserResponse(userInput, conversationArea) {
        // Get current emotion for context - use last detected emotion or neutral if detection stopped
        const emotion = this.currentEmotion || this.lastDetectedEmotion || 'neutral';

        // Add user message to conversation
        this.addMessageToConversation(userInput, 'user', conversationArea);

        // Save user response to backend
        this.saveUserResponse(userInput, emotion);

        // Enhanced: Use EmotiCare AI Chat System for dynamic response
        try {
            const aiResponse = await fetch('/api/ai-chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userInput,
                    detected_emotion: emotion,
                    chat_continues_after_detection: !this.isDetecting // Indicate if detection is stopped
                })
            });

            if (aiResponse.ok) {
                const data = await aiResponse.json();

                if (data.success) {
                    // Add single AI response only
                    this.addMessageToConversation(data.reply, 'bot', conversationArea);
                } else {
                    this.addMessageToConversation('Sorry, I could not process your request right now.', 'bot', conversationArea);
                }
            } else {
                this.addMessageToConversation('Sorry, I could not process your request right now.', 'bot', conversationArea);
            }
        } catch (error) {
            console.error('AI Chat error:', error);
            this.addMessageToConversation('Sorry, there was a problem connecting to the AI service.', 'bot', conversationArea);
        }
    }

    async saveUserResponse(userInput, emotion) {
        try {
            await fetch('/api/save-emotion-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    record_id: this.currentRecordId,
                    user_response: userInput,
                    emotion: emotion,
                    emotion_context: `User interaction with ${emotion} emotion detection`
                })
            });
        } catch (error) {
            console.error('Error saving user response:', error);
        }
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

// Additional CSS for conversation styling and side-by-side layout
const conversationCSS = `
.emotion-main-container {
    display: flex;
    gap: 20px;
    margin-top: 20px;
}

.camera-section {
    flex: 1;
    min-width: 300px;
}

.chat-section {
    flex: 1.5;
    min-width: 400px;
    display: flex;
    flex-direction: column;
    height: 700px;
}

.camera-controls {
    margin-top: 15px;
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 15px;
    align-items: center;
}

.detection-method-display {
    display: flex;
    justify-content: center;
    margin-bottom: 15px;
}

.ai-badge {
    text-align: center;
    padding: 15px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    max-width: 350px;
}

.ai-description {
    margin: 8px 0 0 0;
    font-size: 0.85em;
    color: rgba(255, 255, 255, 0.8);
    font-style: italic;
}

.badge {
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 0.9em;
    font-weight: bold;
    color: white;
    display: inline-block;
}

.badge-ai {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    animation: aiGlow 2s ease-in-out infinite alternate;
}

@keyframes aiGlow {
    from {
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    to {
        box-shadow: 0 4px 25px rgba(102, 126, 234, 0.6);
    }
}

.main-controls {
    display: flex;
    gap: 15px;
    justify-content: center;
    flex-wrap: wrap;
}

.conversation-area {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    margin: 10px 0;
    max-height: 500px;
    min-height: 400px;
}

.input-area {
    padding: 15px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    display: flex;
    gap: 10px;
    align-items: flex-end;
}

.cute-textarea {
    flex: 1;
    min-height: 60px;
    max-height: 120px;
    resize: vertical;
}

.welcome-message {
    text-align: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 15px;
    margin-bottom: 10px;
}

.welcome-message h3 {
    margin: 0 0 10px 0;
    color: #333;
    font-size: 1.2rem;
}

.welcome-message p {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
}

@media (max-width: 768px) {
    .emotion-main-container {
        flex-direction: column;
    }

    .chat-section {
        height: 600px;
    }

    .conversation-area {
        min-height: 350px;
        max-height: 450px;
    }
}

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

.emotion-badge.first-emotion {
    border: 4px solid #f39c12 !important;
    box-shadow: 0 0 20px rgba(243, 156, 18, 0.5);
    animation: firstEmotionGlow 2s ease-in-out infinite alternate;
}

@keyframes firstEmotionGlow {
    from { box-shadow: 0 0 20px rgba(243, 156, 18, 0.5); }
    to { box-shadow: 0 0 30px rgba(243, 156, 18, 0.8); }
}

.first-emotion-indicator {
    position: absolute;
    top: -10px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(45deg, #f39c12, #e67e22);
    color: white;
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    border: 2px solid #fff;
    animation: bounce 1s ease-in-out infinite;
}

@keyframes bounce {
    0%, 20%, 50%, 80%, 100% { transform: translateX(-50%) translateY(0); }
    40% { transform: translateX(-50%) translateY(-5px); }
    60% { transform: translateX(-50%) translateY(-3px); }
}

.session-context {
    font-size: 0.85rem;
    color: rgba(255,255,255,0.9);
    font-style: italic;
    margin-top: 5px;
    text-align: center;
}

.first-emotion-suggestions {
    border: 3px solid #f39c12 !important;
    background: linear-gradient(45deg, rgba(243, 156, 18, 0.1), rgba(230, 126, 34, 0.1)) !important;
}

.first-emotion-note {
    background: rgba(243, 156, 18, 0.2);
    padding: 10px;
    border-radius: 10px;
    color: #fff !important;
    font-weight: bold;
    text-align: center;
    margin-top: 15px;
    border: 2px solid #f39c12;
}

.ai-indicator {
    background: linear-gradient(45deg, #00d4aa, #00b894);
    color: white;
    padding: 4px 12px;
    border-radius: 15px;
    font-size: 0.75rem;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 8px;
    border: 1px solid rgba(255,255,255,0.3);
    box-shadow: 0 2px 8px rgba(0, 212, 170, 0.3);
    animation: aiGlow 2s ease-in-out infinite alternate;
}

@keyframes aiGlow {
    from { box-shadow: 0 2px 8px rgba(0, 212, 170, 0.3); }
    to { box-shadow: 0 2px 12px rgba(0, 212, 170, 0.6); }
}

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

.emotion-badge.warning {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    border: 2px solid rgba(245, 87, 108, 0.3);
    animation: warningPulse 2s ease-in-out infinite alternate;
}

@keyframes warningPulse {
    from {
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.3);
    }
    to {
        box-shadow: 0 4px 25px rgba(245, 87, 108, 0.6);
    }
}
`;

// Inject the CSS
const style = document.createElement('style');
style.textContent = conversationCSS;
document.head.appendChild(style);
