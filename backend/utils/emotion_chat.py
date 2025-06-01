import random
import re
from datetime import datetime
from typing import Dict, List, Optional


class EmotionAwareChat:

    def __init__(self):
        self.conversation_history = []
        self.user_emotions = []
        self.initialize_responses()

    def initialize_responses(self):

        self.greetings = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening)\b',
            r'\bhow are you\b',
            r'\bwhat\'s up\b'
        ]
        self.emotion_responses = {
            'happy': {
                'responses': [
                    "I'm so glad to hear you're feeling happy! 😊 What's bringing you joy today?",
                    "That's wonderful! Happiness is such a beautiful emotion. Would you like to share what's making you feel this way?",
                    "Your happiness is contagious! 🌟 How can we make this feeling last longer?",
                    "I love seeing you happy! What activities or thoughts are contributing to this positive mood?"
                ],
                'follow_up': [
                    "What specific moment today made you smile the most?",
                    "How would you like to celebrate this happy feeling?",
                    "Who would you like to share this happiness with?"
                ]
            },
            'sad': {
                'responses': [
                    "I can sense you're feeling sad, and that's completely okay. 💙 Would you like to talk about what's on your mind?",
                    "Sadness is a natural emotion, and I'm here to listen. What's been weighing on your heart?",
                    "I'm sorry you're going through a difficult time. Sometimes talking helps - what's troubling you?",
                    "Your feelings are valid. Would you like to share what's making you feel this way, or would you prefer some gentle suggestions?"
                ],
                'follow_up': [
                    "What would help you feel a little better right now?",
                    "Is there someone you trust that you could talk to about this?",
                    "Would you like some suggestions for gentle activities that might help?"
                ]
            },
            'stressed': {
                'responses': [
                    "I can tell you're feeling stressed. Let's take a deep breath together. 🌬️ What's causing you the most pressure right now?",
                    "Stress can be overwhelming. You're not alone in this. What's the biggest challenge you're facing today?",
                    "I hear that you're stressed. Sometimes breaking things down helps - what's the main source of your stress?",
                    "Feeling stressed is tough. Let's work through this together. What's been on your mind lately?"
                ],
                'follow_up': [
                    "What's one small step you could take to reduce this stress?",
                    "Have you tried any relaxation techniques that work for you?",
                    "What usually helps you feel calmer when you're stressed?"
                ]
            },
            'anxious': {
                'responses': [
                    "Anxiety can feel overwhelming, but you're safe here. 🤗 What thoughts are making you feel anxious?",
                    "I understand anxiety can be really difficult. What's been triggering these feelings for you?",
                    "You're brave for acknowledging your anxiety. What specific worries are on your mind?",
                    "Anxiety is challenging, but you're stronger than you know. What's been causing you to feel this way?"
                ],
                'follow_up': [
                    "What grounding techniques have helped you before?",
                    "Would you like to try a simple breathing exercise together?",
                    "What makes you feel most secure and calm?"
                ]
            },
            'angry': {
                'responses': [
                    "I can sense your anger, and it's okay to feel this way. 🔥 What's frustrating you right now?",
                    "Anger often comes from feeling hurt or misunderstood. What's behind these feelings?",
                    "Your anger is valid. Sometimes it's our way of protecting ourselves. What triggered this feeling?",
                    "I hear your frustration. Anger can be a powerful emotion - what's causing it for you?"
                ],
                'follow_up': [
                    "What would help you process this anger in a healthy way?",
                    "Is there something specific that needs to change in your situation?",
                    "How do you usually cope when you feel this angry?"
                ]
            },
            'neutral': {
                'responses': [
                    "How are you feeling today? I'm here to listen and support you. 💭",
                    "What's on your mind? Sometimes it helps to talk through our thoughts.",
                    "I'm here for you. What would you like to talk about today?",
                    "How has your day been so far? I'm interested in hearing about your experiences."
                ],
                'follow_up': [
                    "What's been the highlight of your day?",
                    "Is there anything you'd like to explore or discuss?",
                    "How are you taking care of yourself today?"
                ]
            }
        }

        self.supportive_responses = [
            "I'm here to listen and support you through whatever you're experiencing.",
            "Your feelings are completely valid, and it's important to acknowledge them.",
            "Thank you for sharing that with me. It takes courage to open up about our emotions.",
            "I appreciate you trusting me with your feelings. How can I best support you right now?",
            "You're not alone in this. Many people experience similar emotions, and it's okay to feel this way."
        ]
        self.coping_strategies = {
            'sad': [
                "Try listening to music that comforts you",
                "Consider reaching out to a friend or family member",
                "Take a gentle walk in nature if possible",
                "Practice self-compassion - treat yourself as you would a good friend",
                "Write in a journal about your feelings"
            ],
            'stressed': [
                "Try the 4-7-8 breathing technique: breathe in for 4, hold for 7, exhale for 8",
                "Break large tasks into smaller, manageable steps",
                "Take regular breaks throughout your day",
                "Practice progressive muscle relaxation",
                "Consider what you can control vs. what you cannot"
            ],
            'anxious': [
                "Use the 5-4-3-2-1 grounding technique: 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste",
                "Practice deep, slow breathing",
                "Challenge anxious thoughts by asking: 'Is this thought helpful? Is it realistic?'",
                "Try gentle movement or stretching",
                "Focus on the present moment rather than future worries"
            ],
            'angry': [
                "Take slow, deep breaths to help calm your nervous system",
                "Try physical exercise to release tension",
                "Express your feelings through writing or art",
                "Practice the pause: count to 10 before responding",
                "Consider what boundary might need to be set"
            ]
        }

    def detect_emotion_from_text(self, text: str) -> str:
        text_lower = text.lower()

        emotion_keywords = {
            'happy': ['happy', 'joy', 'excited', 'great', 'wonderful', 'amazing', 'fantastic', 'good', 'smile', 'laugh'],
            'sad': ['sad', 'down', 'depressed', 'upset', 'hurt', 'cry', 'tears', 'lonely', 'empty', 'blue'],
            'stressed': ['stressed', 'pressure', 'overwhelmed', 'busy', 'deadline', 'work', 'tired', 'exhausted'],
            'anxious': ['anxious', 'worried', 'nervous', 'scared', 'afraid', 'panic', 'fear', 'uncertain'],
            'angry': ['angry', 'mad', 'furious', 'frustrated', 'annoyed', 'irritated', 'rage', 'hate']
        }

        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return emotion

        return 'neutral'

    def get_response(self, user_message: str, detected_emotion: Optional[str] = None, is_first_emotion: bool = False, emotion_change: bool = False, previous_emotion: Optional[str] = None) -> Dict:

        conversation_entry = {
            'user': user_message,
            'timestamp': datetime.now(),
            'detected_emotion': detected_emotion,
            'is_first_emotion': is_first_emotion,
            'emotion_change': emotion_change,
            'previous_emotion': previous_emotion
        }
        self.conversation_history.append(conversation_entry)

        if not detected_emotion:
            detected_emotion = self.detect_emotion_from_text(user_message)

        self.user_emotions.append(detected_emotion)

        if is_first_emotion:
            response = self.get_first_emotion_response(detected_emotion)
            follow_up = self.get_first_emotion_followup(detected_emotion)
            coping_strategy = self.get_first_emotion_strategy(detected_emotion)
        elif emotion_change and previous_emotion:
            response = self.get_emotion_change_response(detected_emotion, previous_emotion)
            follow_up = self.get_emotion_change_followup(detected_emotion, previous_emotion)
            coping_strategy = self.get_transition_strategy(detected_emotion, previous_emotion)
        elif any(re.search(pattern, user_message.lower()) for pattern in self.greetings):
            greeting_responses = [
                "Hello! I'm here to support you today. How are you feeling? 😊",
                "Hi there! I'm glad you're here. What's on your mind today?",
                "Hello! I'm your EmotiCare companion. How can I help you today?",
                "Hi! I'm here to listen and support you. How are you doing?"
            ]
            response = random.choice(greeting_responses)
            follow_up = "What brings you to EmotiCare today?"
            coping_strategy = None
        else:
            if detected_emotion in self.emotion_responses:
                response = random.choice(self.emotion_responses[detected_emotion]['responses'])
            else:
                response = random.choice(self.supportive_responses)

            follow_up = None
            if detected_emotion in self.emotion_responses:
                follow_up = random.choice(self.emotion_responses[detected_emotion]['follow_up'])

            coping_strategy = None
            if detected_emotion in self.coping_strategies:
                coping_strategy = random.choice(self.coping_strategies[detected_emotion])

        return {
            'response': response,
            'follow_up': follow_up,
            'coping_strategy': coping_strategy,
            'detected_emotion': detected_emotion,
            'suggestions': self.get_emotion_suggestions(detected_emotion),
            'is_first_emotion': is_first_emotion,
            'emotion_change': emotion_change
        }

    def get_emotion_suggestions(self, emotion: str) -> List[str]:
        if emotion in self.coping_strategies:
            return self.coping_strategies[emotion][:3]
        return []

    def get_conversation_summary(self) -> Dict:
        if not self.user_emotions:
            return {'dominant_emotion': 'neutral', 'emotion_count': {}}

        emotion_count = {}
        for emotion in self.user_emotions:
            emotion_count[emotion] = emotion_count.get(emotion, 0) + 1

        if emotion_count:
            dominant_emotion = max(emotion_count.keys(), key=lambda x: emotion_count[x])
        else:
            dominant_emotion = 'neutral'

        return {
            'dominant_emotion': dominant_emotion,
            'emotion_count': emotion_count,
            'total_messages': len(self.conversation_history),
            'conversation_length': len(self.conversation_history)
        }

    def get_first_emotion_response(self, emotion: str) -> str:
        first_emotion_responses = {
            'happy': [
                "What a wonderful way to start our session! Your happiness is radiating through, and I'm so glad to be here with you during this joyful moment.",
                "I'm delighted to see you beginning our time together with such positive energy! This happiness sets a beautiful foundation for our conversation.",
                "Starting with happiness is such a gift! I can sense your positive spirit, and I'm excited to explore what's bringing you this joy today."
            ],
            'sad': [
                "I want you to know that starting our session by acknowledging your sadness takes real courage. I'm here to walk through this with you, step by step.",
                "Thank you for trusting me with your sadness right from the start. This openness is the first step toward healing, and I'm honored to support you.",
                "Beginning our time together with such honesty about your feelings shows incredible strength. Let's explore this sadness together with compassion."
            ],
            'stressed': [
                "I can feel the weight you're carrying as we begin today. Starting our session by recognizing your stress is already a step toward relief.",
                "Thank you for bringing your stress into our space right away. This awareness is powerful, and together we can work on finding some peace.",
                "Starting with stress can feel overwhelming, but you've taken the brave step of seeking support. Let's work together to lighten this load."
            ],
            'anxious': [
                "I notice the anxiety you're experiencing as we start our session. Your willingness to be here despite these feelings shows incredible courage.",
                "Beginning our time together while feeling anxious takes real bravery. I'm here to help you find calm and stability in this moment.",
                "Thank you for trusting me with your anxiety from the very start. Together, we can work on finding some peace and grounding."
            ],
            'angry': [
                "I can sense the intensity of your anger as we begin. Thank you for bringing this powerful emotion into our space - it deserves to be heard and understood.",
                "Starting our session with anger takes courage. These feelings are valid and important, and I'm here to help you process them safely.",
                "Your anger is telling us something important. I'm grateful you're sharing this with me right from the start so we can explore it together."
            ],
            'neutral': [
                "I appreciate you starting our session with such openness. Sometimes neutral feelings can be just as meaningful as intense emotions.",
                "Thank you for being present with me today. Even in neutral moments, there's often much to explore and understand about ourselves.",
                "Starting our time together with a calm presence is valuable. Let's see what insights and discoveries await us in our conversation."
            ]
        }

        if emotion in first_emotion_responses:
            return random.choice(first_emotion_responses[emotion])
        else:
            return f"Thank you for sharing your {emotion} feelings with me as we begin our session. This gives me valuable insight into how to best support you today."

    def get_first_emotion_followup(self, emotion: str) -> str:
        first_emotion_followups = {
            'happy': "What specific moment or thought brought you this happiness as you started our session today?",
            'sad': "What would feel most supportive for you right now as we begin exploring these feelings together?",
            'stressed': "What's the most pressing concern that's weighing on you as we start our conversation?",
            'anxious': "What would help you feel most grounded and safe as we continue our session together?",
            'angry': "What's at the heart of this anger that you'd like to explore with me today?",
            'neutral': "What's been on your mind lately that you'd like to explore in our time together?"
        }

        return first_emotion_followups.get(emotion, f"How has this {emotion} feeling been affecting your day so far?")

    def get_first_emotion_strategy(self, emotion: str) -> str:
        first_emotion_strategies = {
            'happy': "To nurture this happiness: Take a moment to really savor this feeling. Notice what's happening in your body, your thoughts, and your environment that's contributing to this joy.",
            'sad': "For this sadness: Remember that feeling sad is a natural part of being human. Try placing a gentle hand on your heart and offering yourself the same compassion you'd give a dear friend.",
            'stressed': "To ease this stress: Take three deep breaths with me. Breathe in for 4 counts, hold for 4, and exhale for 6. This activates your body's natural relaxation response.",
            'anxious': "For your anxiety: Try the 5-4-3-2-1 grounding technique. Name 5 things you can see, 4 you can touch, 3 you can hear, 2 you can smell, and 1 you can taste.",
            'angry': "To process this anger: Acknowledge that your anger is valid and often signals that something important needs attention. Take slow, deep breaths to help your nervous system settle.",
            'neutral': "For reflection: Sometimes neutral moments are perfect for checking in with ourselves. Ask: 'What do I need right now?' and listen to what comes up."
        }

        return first_emotion_strategies.get(emotion, f"For your {emotion} feelings: Take a moment to breathe deeply and acknowledge that all emotions are valid and temporary.")

    def get_emotion_change_response(self, new_emotion: str, previous_emotion: str) -> str:
        change_responses = [
            f"I notice your emotional state has shifted from {previous_emotion} to {new_emotion}. This kind of emotional movement is completely natural during our conversations.",
            f"It's interesting how your feelings have evolved from {previous_emotion} to {new_emotion}. These transitions often tell us something important about what's happening inside.",
            f"I see you're now experiencing {new_emotion} after feeling {previous_emotion}. These emotional shifts can provide valuable insights into your inner world."
        ]
        return random.choice(change_responses)

    def get_emotion_change_followup(self, new_emotion: str, previous_emotion: str) -> str:
        return f"What do you think might have influenced this shift from {previous_emotion} to {new_emotion}?"

    def get_transition_strategy(self, new_emotion: str, previous_emotion: str) -> str:
        return f"During emotional transitions like this, it can help to pause and acknowledge both feelings. You've moved from {previous_emotion} to {new_emotion}, and both emotions have something to teach us."
