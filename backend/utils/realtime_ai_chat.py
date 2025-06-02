from typing import Dict, Optional
from datetime import datetime
import os
import base64
import io
import time

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    print("✅ Groq AI library loaded successfully")
    print(f"✅ Groq library version: {getattr(Groq, '__version__', 'unknown')}")
except ImportError as e:
    GROQ_AVAILABLE = False
    print(f"⚠️ Groq not available - ImportError: {e}")
    print("⚠️ Install with: pip install groq")
except Exception as e:
    GROQ_AVAILABLE = False
    print(f"⚠️ Groq library error: {e}")

try:
    import openai
    OPENAI_AVAILABLE = True
    print("✅ OpenAI library loaded successfully")
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI not available - install with: pip install openai")


class RealtimeAIChat:

    def __init__(self):
        self.conversation_history = []
        self.user_emotions = []
        self.session_context = {}
        self.first_emotion = None

        self.groq_client = None
        self.openai_client = None

        self.last_api_call = 0
        self.min_api_interval = 2.0
        self.rate_limit_errors = 0
        if GROQ_AVAILABLE:
            groq_api_key = os.getenv('GROQ_API_KEY')
            print(f"🔍 GROQ_API_KEY from environment: {groq_api_key[:20] + '...' if groq_api_key else 'NOT_SET'}")

            # Clean the API key (remove any prefixes or whitespace)
            if groq_api_key:
                groq_api_key = groq_api_key.strip()
                # Remove any potential prefix
                if groq_api_key.startswith('GROQ_API_KEY='):
                    groq_api_key = groq_api_key.replace('GROQ_API_KEY=', '')
                    print("🧹 Cleaned API key prefix")

            # Fallback to hardcoded key if environment variable not set
            if not groq_api_key:
                groq_api_key = "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"
                print("🔄 Using hardcoded fallback API key")

            if groq_api_key and groq_api_key != 'gsk_demo_key_for_testing':
                try:
                    print("🔧 Attempting to initialize Groq client...")
                    print(f"🔑 Final API key: {groq_api_key[:20]}...")

                    # Try to import and create client with more error handling
                    from groq import Groq

                    # Create client with minimal parameters to avoid compatibility issues
                    try:
                        self.groq_client = Groq(api_key=groq_api_key)
                    except TypeError as te:
                        print(f"🔄 TypeError creating Groq client: {te}")
                        # Try with just the API key, no other parameters
                        try:
                            import groq
                            self.groq_client = groq.Groq(api_key=groq_api_key)
                        except Exception as e2:
                            print(f"❌ Alternative Groq creation failed: {e2}")
                            raise te

                    print("🧪 Testing Groq API connection...")
                    test_response = self.groq_client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=5,
                        timeout=30  # Add timeout for Railway
                    )

                    print("✅ Groq AI client initialized successfully with real API key!")
                    print("🚀 Real AI responses are now ENABLED!")
                    print(f"🧪 Test response: {test_response.choices[0].message.content}")
                except ImportError as ie:
                    print(f"❌ Groq import failed: {ie}")
                    self.groq_client = None
                except Exception as e:
                    print(f"❌ Failed to initialize Groq client: {e}")
                    print(f"❌ Error type: {type(e).__name__}")
                    print(f"❌ Error details: {str(e)}")
                    # Try without timeout if client was created
                    if self.groq_client:
                        try:
                            print("🔄 Retrying without timeout...")
                            test_response = self.groq_client.chat.completions.create(
                                model="llama3-8b-8192",
                                messages=[{"role": "user", "content": "Hello"}],
                                max_tokens=5
                            )
                            print("✅ Groq client working on retry!")
                        except:
                            print("❌ Retry also failed")
                            self.groq_client = None
                    else:
                        self.groq_client = None
            else:
                print("💡 Set GROQ_API_KEY environment variable for real AI responses")
        else:
            print("❌ Groq library not available")

        if OPENAI_AVAILABLE:
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                try:
                    self.openai_client = openai.OpenAI(api_key=openai_api_key)
                    print("✅ OpenAI client initialized successfully")
                except Exception as e:
                    print(f"❌ Failed to initialize OpenAI client: {e}")

        if not self.groq_client and not self.openai_client:
            print("🤖 Using enhanced rule-based responses (no AI API keys configured)")
            print("💡 For real AI responses, set GROQ_API_KEY environment variable")

        if self.groq_client:
            print("🎥 Visual emotion detection with AI is available!")
            print("💡 You can now detect emotions directly from camera images using Llama Vision")
        self.system_prompts = {
            'base': """You are EmotiCare AI, a compassionate and intelligent emotional support companion.
            You provide real-time, personalized responses to help users understand and manage their emotions.

            Key principles:
            - Be empathetic, warm, and genuinely caring
            - Provide practical, actionable advice
            - Validate emotions while offering hope
            - Use a conversational, supportive tone
            - Keep responses concise but meaningful (2-3 sentences max)
            - Focus on the user's immediate emotional needs""",

            'first_emotion': """This is the user's FIRST emotion detected in this session. This is crucial context that will guide the entire conversation.
            Give special attention to this first emotion as it sets the foundation for their emotional state today.
            Acknowledge the significance of this being their starting emotion and provide comprehensive, welcoming support.""",

            'emotion_change': """The user's emotion has changed during our conversation. This transition is important to acknowledge and explore.
            Help them understand this emotional shift and provide guidance for navigating the change."""
        }

    async def get_ai_response(self, user_message: str, emotion: str, context: Optional[Dict] = None) -> str:

        if context is None:
            context = {}

        system_prompt = self.system_prompts['base']

        if context.get('is_first_emotion'):
            system_prompt += "\n\n" + self.system_prompts['first_emotion']

        if context.get('emotion_change'):
            system_prompt += "\n\n" + self.system_prompts['emotion_change']

        if context.get('chat_continues_after_detection'):
            system_prompt += "\n\nNote: The user has stopped emotion detection but wants to continue chatting. Base your response on their last detected emotion and the conversation context. Be supportive and maintain conversation flow."

        emotion_context = f"\n\nCurrent emotion detected: {emotion}"
        if context.get('previous_emotion'):
            emotion_context += f"\nPrevious emotion: {context['previous_emotion']}"
        if context.get('chat_continues_after_detection'):
            emotion_context += f"\nNote: Chat continues after detection stopped - use last detected emotion: {emotion}"

        system_prompt += emotion_context

        messages = [{"role": "system", "content": system_prompt}]

        recent_history = self.conversation_history[-6:] if len(self.conversation_history) > 6 else self.conversation_history
        for entry in recent_history:
            if 'user' in entry:
                messages.append({"role": "user", "content": entry['user']})
            if 'ai' in entry:
                messages.append({"role": "assistant", "content": entry['ai']})

        messages.append({"role": "user", "content": user_message})
        if self.groq_client:
            try:
                current_time = time.time()
                time_since_last_call = current_time - self.last_api_call

                if time_since_last_call < self.min_api_interval:
                    wait_time = self.min_api_interval - time_since_last_call
                    print(f"Rate limiting: waiting {wait_time:.1f}s before API call")
                    time.sleep(wait_time)

                self.last_api_call = time.time()

                response = self.groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                self.rate_limit_errors = 0
                return response.choices[0].message.content.strip()
            except Exception as e:
                error_str = str(e)
                print(f"Groq API error: {e}")

                if "rate_limit" in error_str.lower() or "429" in error_str:
                    self.rate_limit_errors += 1
                    self.min_api_interval = min(10.0, self.min_api_interval * 1.5)
                    print(f"Rate limit hit! Increasing interval to {self.min_api_interval:.1f}s")

        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI API error: {e}")

        return self._get_fallback_response(user_message, emotion, context)

    async def check_content_safety(self, message: str) -> Dict:
        """
        Use meta-llama/llama-prompt-guard-2-86m to check content safety
        Returns safety score and analysis
        """
        if not self.groq_client:
            return {
                'is_safe': True,
                'safety_score': 1.0,
                'analysis': 'Safety check not available',
                'method': 'fallback'
            }

        try:
            response = self.groq_client.chat.completions.create(
                model="meta-llama/llama-prompt-guard-2-86m",
                messages=[
                    {
                        "role": "user",
                        "content": f"Analyze this message for safety and appropriateness: {message}"
                    }
                ],
                temperature=0.1,
                max_tokens=100,  # Max 512 for this model
                stream=False,  # Prompt guard doesn't support streaming
            )

            safety_response = response.choices[0].message.content.strip()

            # Parse the response (usually a number between 0-1)
            try:
                safety_score = float(safety_response)
                is_safe = safety_score < 0.5  # Lower scores = safer content
            except ValueError:
                # If not a number, assume safe
                safety_score = 0.1
                is_safe = True

            return {
                'is_safe': is_safe,
                'safety_score': safety_score,
                'analysis': safety_response,
                'method': 'prompt_guard',
                'model': 'meta-llama/llama-prompt-guard-2-86m'
            }

        except Exception as e:
            print(f"Safety check error: {e}")
            # Default to safe if check fails
            return {
                'is_safe': True,
                'safety_score': 0.1,
                'analysis': f'Safety check failed: {e}',
                'method': 'fallback_safe'
            }

    async def detect_emotion_from_image(self, image_data_url: str) -> Dict:
        if not self.groq_client:
            return {
                'emotion': 'neutral',
                'confidence': 0.0,
                'method': 'fallback',
                'message': 'Visual AI emotion detection not available'
            }

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert facial emotion detection AI with advanced computer vision capabilities. Analyze the person's face in the image with high precision.

CRITICAL INSTRUCTIONS:
1. Look specifically for a human face in the image
2. If NO clear human face is visible, return: {"emotion": "no_face", "confidence": 0.0, "description": "No clear human face detected"}
3. If face is too blurry/dark/unclear, return: {"emotion": "unclear", "confidence": 0.0, "description": "Face too unclear for analysis"}

For CLEAR faces, analyze these features with precision:
- Eyes: Shape, openness, brightness, tension around eyes
- Eyebrows: Position, furrow, arch, symmetry
- Mouth: Corners up/down, lip tension, openness
- Forehead: Wrinkles, tension, smoothness
- Cheeks: Raised/lowered, muscle tension
- Overall facial symmetry and micro-expressions

Return ONLY this JSON format:
{
    "emotion": "happy, sad, angry, surprised, fearful, disgusted, neutral, stressed, peaceful, depressed, excited, confused, or no_face/unclear",
    "confidence": 0.85,
    "description": "Detailed description of specific facial features observed"
}

Be extremely accurate - only high confidence detections."""
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this person's emotion from their facial expression:"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data_url
                                }
                            }
                        ]
                    }
                ],
                temperature=0.3,
                max_tokens=200,
                top_p=0.8
            )

            response_text = completion.choices[0].message.content.strip()

            import json
            try:
                emotion_data = json.loads(response_text)
                detected_emotion = emotion_data.get('emotion', 'neutral').lower()
                confidence = float(emotion_data.get('confidence', 0.8))
                description = emotion_data.get('description', 'AI detected emotion')

                return {
                    'emotion': detected_emotion,
                    'confidence': confidence,
                    'description': description,
                    'method': 'groq_vision',
                    'model': 'llama-3.2-90b-vision-preview',
                    'raw_response': response_text
                }
            except json.JSONDecodeError:
                response_lower = response_text.lower()
                emotions = ['happy', 'sad', 'angry', 'surprised', 'fearful', 'disgusted', 'neutral']
                detected_emotion = 'neutral'

                for emotion in emotions:
                    if emotion in response_lower:
                        detected_emotion = emotion
                        break

                return {
                    'emotion': detected_emotion,
                    'confidence': 0.7,
                    'description': response_text[:100],
                    'method': 'groq_vision_text_parse',
                    'model': 'llama-3.2-90b-vision-preview',
                    'raw_response': response_text
                }

        except Exception as e:
            print(f"Visual emotion detection error: {e}")
            return {
                'emotion': 'neutral',
                'confidence': 0.0,
                'method': 'error',
                'message': f'Error: {str(e)}'
            }

    def _get_fallback_response(self, user_message: str, emotion: str, context: Dict) -> str:

        message_lower = user_message.lower()
        if 'i am sad' in message_lower:
            if context.get('chat_continues_after_detection'):
                return "I can hear the sadness in your words. Even though we're not actively detecting emotions right now, I can sense you're going through a difficult time. What's weighing on your heart today?"
            else:
                return "I'm sorry to hear you're feeling sad. Your emotions are valid, and I'm here to listen. What's been making you feel this way today?"

        if 'sad today' in message_lower or 'not fine today' in message_lower:
            return "I'm sorry to hear you're having a difficult day. It sounds like you're going through something tough right now. Would you like to talk about what's making today particularly hard for you?"

        if 'not fine' in message_lower or 'not good' in message_lower or 'not okay' in message_lower:
            return "I hear that you're not feeling okay right now. That takes courage to acknowledge. What's been weighing on you? I'm here to listen."

        if 'tired' in message_lower or 'exhausted' in message_lower or 'drained' in message_lower:
            return "It sounds like you're really drained. Being tired can make everything feel harder. What's been taking so much out of you lately?"

        if 'work' in message_lower and ('stress' in message_lower or 'hard' in message_lower or 'difficult' in message_lower):
            return "Work stress can be really overwhelming. It sounds like things are challenging at your job right now. What's the most difficult part you're dealing with?"

        if 'lonely' in message_lower or 'alone' in message_lower:
            return "Feeling lonely can be really painful. Even when we're surrounded by people, we can still feel disconnected. What's making you feel most alone right now?"

        if 'anxious' in message_lower or 'worried' in message_lower or 'nervous' in message_lower:
            return "Anxiety can be so consuming and make everything feel uncertain. What thoughts or situations are causing you the most worry right now?"

        if 'angry' in message_lower or 'frustrated' in message_lower or 'mad' in message_lower:
            return "I can hear the frustration in your words. Anger often tells us that something important needs attention. What's at the core of what's bothering you?"

        if 'help' in message_lower or 'support' in message_lower:
            if context.get('chat_continues_after_detection'):
                return "I'm still here to help and support you, even without active emotion detection. What kind of support would feel most helpful right now? Sometimes just talking through things can make a difference."
            else:
                return "I'm here to help and support you. What kind of support would feel most helpful right now? Sometimes just talking through things can make a difference."

        if 'better' in message_lower and ('feel' in message_lower or 'getting' in message_lower):
            return "I'm glad to hear you're feeling better! That's wonderful progress. What's been helping you feel more positive?"

        if 'worse' in message_lower or 'bad' in message_lower:
            if context.get('chat_continues_after_detection'):
                return "I'm sorry things are feeling worse for you. Even though we're not actively detecting emotions, I can sense you're struggling. What's been making things feel particularly challenging?"
            else:
                return "I'm sorry things are feeling worse for you. It's okay to have difficult moments. What's been making things feel particularly challenging?"

        if context.get('chat_continues_after_detection'):
            if any(word in message_lower for word in ['continue', 'talk', 'chat', 'more']):
                return f"I'm glad you want to continue our conversation! Based on your last detected emotion ({emotion}), I'm here to keep supporting you. What would you like to talk about?"

        if 'family' in message_lower or 'relationship' in message_lower:
            return "Family and relationship issues can be really complex and emotionally draining. What's been going on that's affecting you?"

        if 'school' in message_lower or 'study' in message_lower or 'exam' in message_lower:
            return "Academic pressure can be really stressful. It sounds like you're dealing with some challenges in your studies. What's been the most difficult part?"

        if 'sleep' in message_lower or 'insomnia' in message_lower:
            return "Sleep issues can really affect how we feel during the day. Not getting enough rest makes everything harder. How has your sleep been affecting you?"

        enhanced_responses = {
            'happy': [
                "That's wonderful to hear! I love when someone shares positive moments. What's been the best part of your day?",
                "Your happiness comes through in your message! What's bringing you joy right now?",
                "It's great that you're feeling good! What would you like to share about what's going well?"
            ],
            'sad': [
                "I'm sorry you're feeling sad. It's okay to have difficult days. What's been the hardest part for you today?",
                "I hear that you're going through a tough time. Would you like to talk about what's making you feel this way?",
                "Sadness can be really heavy to carry. What's been on your mind that's bringing you down?"
            ],
            'stressed': [
                "It sounds like you're under a lot of pressure right now. What's the biggest source of stress you're dealing with?",
                "Stress can be overwhelming. What's been making things feel so intense for you lately?",
                "I can sense you're feeling overwhelmed. What would help you feel even a little bit better right now?"
            ],
            'anxious': [
                "Anxiety can make everything feel uncertain. What specific thoughts or worries are troubling you most?",
                "I understand that anxious feelings can be really consuming. What's been causing you the most concern?",
                "It's hard when anxiety takes over. What situations or thoughts are making you feel most nervous?"
            ],
            'angry': [
                "I can feel your frustration. Anger often signals that something important needs attention. What's bothering you most?",
                "It sounds like something has really upset you. What's at the core of your anger right now?",
                "Your feelings are valid. What situation or person has triggered these strong emotions?"
            ],
            'neutral': [
                "I'm here and ready to listen. What's on your mind today?",
                "How are you feeling right now? What would you like to talk about?",
                "I'm glad you're here. What's been going through your thoughts lately?"
            ]
        }

        if context.get('is_first_emotion'):
            prefix = "As we begin our conversation, "
        elif context.get('emotion_change'):
            prefix = f"I notice your emotions have shifted from {context.get('previous_emotion', 'before')} to {emotion}. "
        elif context.get('chat_continues_after_detection'):
            prefix = "I'm still here to chat with you! Based on our conversation and your last detected emotion, "
        else:
            prefix = ""

        base_responses = enhanced_responses.get(emotion, enhanced_responses['neutral'])
        import random
        base_response = random.choice(base_responses)
        if context.get('chat_continues_after_detection'):
            context_addition = " Feel free to continue sharing - I'm here to support you even without active emotion detection."
        elif 'work' in user_message.lower() or 'job' in user_message.lower():
            context_addition = " Work-related stress can be particularly challenging because it affects so many areas of our lives."
        elif 'family' in user_message.lower() or 'relationship' in user_message.lower():
            context_addition = " Relationships and family dynamics can bring up such complex emotions."
        elif 'health' in user_message.lower() or 'sick' in user_message.lower():
            context_addition = " Health concerns can be especially anxiety-provoking because they touch on our deepest fears."
        else:
            context_addition = ""

        return prefix + base_response + context_addition

    async def get_response(self, user_message: str, detected_emotion: str, **kwargs) -> Dict:

        context = {
            'is_first_emotion': kwargs.get('is_first_emotion', False),
            'emotion_change': kwargs.get('emotion_change', False),
            'previous_emotion': kwargs.get('previous_emotion'),
            'chat_continues_after_detection': kwargs.get('chat_continues_after_detection', False),
            'timestamp': datetime.now()
        }

        if context['is_first_emotion']:
            self.first_emotion = detected_emotion

        ai_service = 'enhanced_fallback'
        is_real_ai = False
        try:
            ai_response = await self.get_ai_response(user_message, detected_emotion, context)
            if self.groq_client or self.openai_client:
                ai_service = 'groq' if self.groq_client else 'openai'
                is_real_ai = True
        except Exception as e:
            print(f"AI response error: {e}")
            ai_response = self._get_fallback_response(user_message, detected_emotion, context)

        conversation_entry = {
            'user': user_message,
            'ai': ai_response,
            'emotion': detected_emotion,
            'timestamp': datetime.now(),
            **context
        }
        self.conversation_history.append(conversation_entry)
        self.user_emotions.append(detected_emotion)

        return {
            'response': ai_response,
            'follow_up': None,
            'coping_strategy': None,
            'suggestions': [],
            'detected_emotion': detected_emotion,
            'is_ai_response': is_real_ai,
            'ai_service': ai_service,
            **context
        }

    def get_conversation_summary(self) -> Dict:
        if not self.user_emotions:
            return {'dominant_emotion': 'neutral', 'emotion_count': {}, 'total_messages': 0}

        emotion_count = {}
        for emotion in self.user_emotions:
            emotion_count[emotion] = emotion_count.get(emotion, 0) + 1

        dominant_emotion = max(emotion_count.keys(), key=lambda x: emotion_count[x])

        return {
            'dominant_emotion': dominant_emotion,
            'first_emotion': self.first_emotion,
            'emotion_count': emotion_count,
            'total_messages': len(self.conversation_history),
            'ai_responses': len([entry for entry in self.conversation_history if 'ai' in entry])
        }
