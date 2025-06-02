from typing import Dict, Optional
from datetime import datetime
import os
import base64
import io
import time
import inspect
import asyncio

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
        self.min_api_interval = 2.0  # Start with a reasonable interval
        self.rate_limit_errors = 0

        if GROQ_AVAILABLE:
            groq_api_key = os.getenv('GROQ_API_KEY')
            print(f"🔍 GROQ_API_KEY from environment: {groq_api_key[:20] + '...' if groq_api_key else 'NOT_SET'}")

            # Clean the API key (remove any prefixes or whitespace)
            if groq_api_key:
                groq_api_key = groq_api_key.strip()
                # Remove any potential prefix like 'GROQ_API_KEY='
                if '=' in groq_api_key:
                    groq_api_key = groq_api_key.split('=')[-1]
                    print("🧹 Cleaned potential prefix from API key")

            # Fallback to hardcoded key if environment variable not set
            if not groq_api_key:
                groq_api_key = "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"
                print("🔄 Using hardcoded fallback API key")

            # Proceed only if a potentially valid key exists
            if groq_api_key and groq_api_key != 'gsk_demo_key_for_testing':
                try:
                    print("🔧 Attempting to initialize Groq client directly...")
                    print(f"🔑 Using API key: {groq_api_key[:20]}...")

                    # --- ULTIMATE FIX: Multiple approaches to bypass Railway proxies issue ---
                    from groq import Groq
                    import sys
                    import importlib

                    # Method 1: Clear all proxy-related environment variables
                    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
                    original_proxy_values = {}
                    for var in proxy_vars:
                        if var in os.environ:
                            original_proxy_values[var] = os.environ[var]
                            del os.environ[var]

                    try:
                        # Method 2: Reload groq module to clear any cached proxy settings
                        if 'groq' in sys.modules:
                            importlib.reload(sys.modules['groq'])

                        # Method 3: Create client with minimal parameters
                        self.groq_client = Groq(api_key=groq_api_key)
                        print("✅ Groq client created successfully with environment cleanup")

                    except Exception as e1:
                        print(f"🔄 Method 1 failed: {e1}")

                        # Method 4: Try with explicit base_url to override defaults
                        try:
                            self.groq_client = Groq(
                                api_key=groq_api_key,
                                base_url="https://api.groq.com/openai/v1"
                            )
                            print("✅ Groq client created with explicit base_url")
                        except Exception as e2:
                            print(f"🔄 Method 2 failed: {e2}")

                            # Method 5: Manual HTTP client approach
                            try:
                                # Create a minimal working client
                                self.groq_client = self._create_minimal_groq_client(groq_api_key)
                                print("✅ Groq client created with minimal approach")
                            except Exception as e3:
                                print(f"❌ All methods failed: {e3}")
                                self.groq_client = None

                    finally:
                        # Restore original proxy environment variables
                        for var, value in original_proxy_values.items():
                            os.environ[var] = value
                    # --- End Ultimate Fix ---

                    # Test connection only if client was successfully created
                    if self.groq_client:
                        print("✅ Groq client initialized successfully!")
                        try:
                            print("🧪 Testing Groq API connection...")
                            test_response = self.groq_client.chat.completions.create(
                                model="llama3-8b-8192",
                                messages=[{"role": "user", "content": "Connection Test"}],
                                max_tokens=5,
                                timeout=30 # Keep timeout for potential network issues
                            )
                            print("✅ Groq API connection test successful!")
                            print(f"🧪 Test response: {test_response.choices[0].message.content}")
                            print("🚀 Real AI responses are now ENABLED!")
                        except Exception as test_e:
                            print(f"⚠️ Groq API connection test failed: {test_e}")
                            print(f"⚠️ Error type: {type(test_e).__name__}")
                            # Decide if client should be None if test fails.
                            # For now, we keep the client instance even if the test fails,
                            # as it might be a temporary network issue.
                            # self.groq_client = None # Uncomment if connection test failure should disable Groq
                    else:
                        print("❌ Groq client was not created successfully")

                except ImportError as ie:
                    print(f"❌ Groq import failed: {ie}")
                    self.groq_client = None
                except TypeError as te:
                    # Catch the specific error observed in logs
                    print(f"❌ Failed to initialize Groq client due to TypeError: {te}")
                    print(f"❌ This likely indicates an incompatibility or environment issue passing unexpected arguments.")
                    self.groq_client = None
                except Exception as e:
                    # Catch other potential errors during initialization
                    print(f"❌ Failed to initialize Groq client: {e}")
                    print(f"❌ Error type: {type(e).__name__}")
                    print(f"❌ Error details: {str(e)}")
                    self.groq_client = None
            else:
                print("💡 No valid GROQ_API_KEY found or using placeholder. Set environment variable for real AI responses.")
                self.groq_client = None
        else:
            print("❌ Groq library not available. Install with 'pip install groq'.")

        # Initialize OpenAI client (if available and key is set)
        if OPENAI_AVAILABLE:
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if openai_api_key:
                try:
                    self.openai_client = openai.OpenAI(api_key=openai_api_key)
                    print("✅ OpenAI client initialized successfully")
                except Exception as e:
                    print(f"❌ Failed to initialize OpenAI client: {e}")

        # Final check and message
        if not self.groq_client and not self.openai_client:
            print("🤖 Using enhanced rule-based responses (No AI API keys configured or initialization failed)")
        elif self.groq_client:
             print("🎥 Visual emotion detection with AI might be available via Groq!")

        # System prompts remain the same
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

        # Limit history to avoid overly long prompts
        recent_history = self.conversation_history[-6:]
        for entry in recent_history:
            if 'user' in entry:
                messages.append({"role": "user", "content": entry['user']})
            if 'ai' in entry:
                messages.append({"role": "assistant", "content": entry['ai']})

        messages.append({"role": "user", "content": user_message})

        # Try Groq first if available
        if self.groq_client:
            try:
                current_time = time.time()
                time_since_last_call = current_time - self.last_api_call

                # Basic rate limiting
                if time_since_last_call < self.min_api_interval:
                    wait_time = self.min_api_interval - time_since_last_call
                    print(f"Rate limiting: waiting {wait_time:.1f}s before Groq API call")
                    time.sleep(wait_time) # Use time.sleep for sync function

                self.last_api_call = time.time()

                response = self.groq_client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                self.rate_limit_errors = 0 # Reset error count on success
                # Add response to history
                self.conversation_history.append({'user': user_message, 'ai': response.choices[0].message.content.strip()})
                return response.choices[0].message.content.strip()

            except Exception as e:
                error_str = str(e).lower()
                print(f"❌ Groq API error: {e}")

                # Handle rate limits specifically
                if "rate_limit" in error_str or "429" in error_str:
                    self.rate_limit_errors += 1
                    # Increase interval exponentially, capped at 10s
                    self.min_api_interval = min(10.0, self.min_api_interval * (1.5 ** self.rate_limit_errors))
                    print(f"Rate limit hit! Increasing interval to {self.min_api_interval:.1f}s")
                # Fall through to OpenAI or fallback if Groq fails

        # Try OpenAI if Groq failed or wasn't available
        if self.openai_client:
            try:
                print("🔄 Falling back to OpenAI...")
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo", # Or your preferred OpenAI model
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7
                )
                # Add response to history
                self.conversation_history.append({'user': user_message, 'ai': response.choices[0].message.content.strip()})
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"❌ OpenAI API error: {e}")
                # Fall through to rule-based fallback

        # If both AI providers fail, use rule-based fallback
        print("🔄 Falling back to rule-based response.")
        fallback_response = self._get_fallback_response(user_message, emotion, context)
        self.conversation_history.append({'user': user_message, 'ai': fallback_response})
        return fallback_response

    async def check_content_safety(self, message: str) -> Dict:
        """
        Use meta-llama/llama-prompt-guard-2-86m to check content safety
        Returns safety score and analysis
        """
        if not self.groq_client:
            return {
                'is_safe': True,
                'safety_score': 1.0,
                'analysis': 'Safety check not available (Groq client not initialized)',
                'method': 'fallback_unavailable'
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

            # Basic parsing (adapt based on actual model output format)
            is_safe = 'unsafe' not in safety_response.lower()
            safety_score = 0.1 if is_safe else 0.9 # Simplified score

            return {
                'is_safe': is_safe,
                'safety_score': safety_score,
                'analysis': safety_response,
                'method': 'prompt_guard',
                'model': 'meta-llama/llama-prompt-guard-2-86m'
            }

        except Exception as e:
            print(f"❌ Safety check error: {e}")
            # Default to safe if check fails
            return {
                'is_safe': True,
                'safety_score': 0.1,
                'analysis': f'Safety check failed: {e}',
                'method': 'fallback_error'
            }

    async def detect_emotion_from_image(self, image_data_url: str) -> Dict:
        """Detect emotion from a base64 encoded image data URL using Groq Vision"""
        if not self.groq_client:
            return {
                'emotion': 'neutral',
                'confidence': 0.0,
                'method': 'fallback',
                'message': 'Visual AI emotion detection not available (Groq client not initialized)'
            }

        try:
            # Extract base64 data
            if not image_data_url.startswith('data:image'):
                raise ValueError("Invalid image data URL format")
            header, encoded = image_data_url.split(',', 1)
            # image_format = header.split(';')[0].split('/')[1] # e.g., 'png', 'jpeg'
            # image_bytes = base64.b64decode(encoded)

            # Use Groq Vision model
            completion = self.groq_client.chat.completions.create(
                model="llama-3.2-90b-vision-preview", # Use the correct vision model ID
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze the primary emotion displayed in this image. Respond with only one word from this list: happy, sad, stressed, depressed, peaceful, neutral."
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
                max_tokens=10, # Only need one word
                temperature=0.1 # Be precise
            )

            detected_emotion = completion.choices[0].message.content.strip().lower()
            valid_emotions = ["happy", "sad", "stressed", "depressed", "peaceful", "neutral"]

            if detected_emotion not in valid_emotions:
                print(f"⚠️ Vision model returned unexpected emotion: {detected_emotion}")
                detected_emotion = "neutral" # Default to neutral if invalid

            return {
                'emotion': detected_emotion,
                'confidence': 0.9, # Placeholder confidence for AI detection
                'method': 'groq_vision',
                'model': 'llama-3.2-90b-vision-preview'
            }

        except Exception as e:
            print(f"❌ Vision emotion detection error: {e}")
            return {
                'emotion': 'neutral',
                'confidence': 0.0,
                'method': 'fallback_error',
                'message': f'Vision detection failed: {e}'
            }

    def _get_fallback_response(self, user_message: str, emotion: str, context: Optional[Dict] = None) -> str:
        """Provides a simple rule-based fallback response."""
        if context is None:
            context = {}

        base_responses = {
            'happy': "It's wonderful to see you feeling happy! What's bringing you joy today?",
            'sad': "I'm sorry to hear you're feeling sad. Remember, your feelings are valid. Would you like to talk about what's on your mind?",
            'stressed': "Feeling stressed can be overwhelming. Take a deep breath. Is there anything specific causing the stress that you'd like to share?",
            'depressed': "Dealing with feelings of depression is tough, and I want you to know you're not alone. Sometimes just acknowledging it is a big step. I'm here to listen without judgment.",
            'peaceful': "It sounds like you're in a peaceful state, that's lovely. What helps you find this sense of calm?",
            'neutral': "Thanks for checking in. How are you feeling right now? Is there anything you'd like to explore?"
        }

        response = base_responses.get(emotion, base_responses['neutral'])

        if context.get('is_first_emotion'):
            response = f"I notice you're starting our session feeling {emotion}. {response}"
        elif context.get('emotion_change'):
            prev_emotion = context.get('previous_emotion', 'a different')
            response = f"I see your emotion has shifted from {prev_emotion} to {emotion}. {response}"

        # Add a generic follow-up
        response += " Remember, I'm here to support you."
        return response

    def _create_minimal_groq_client(self, api_key: str):
        """Create a minimal Groq client that bypasses proxy issues"""
        try:
            # Import here to avoid module-level issues
            from groq import Groq

            # Create with absolutely minimal configuration
            class MinimalGroqClient:
                def __init__(self, api_key):
                    self.api_key = api_key
                    self.base_url = "https://api.groq.com/openai/v1"

                def chat_completions_create(self, **kwargs):
                    # Use requests directly to bypass any proxy issues
                    import requests
                    import json

                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }

                    data = {
                        "model": kwargs.get("model", "llama3-8b-8192"),
                        "messages": kwargs.get("messages", []),
                        "max_tokens": kwargs.get("max_tokens", 150),
                        "temperature": kwargs.get("temperature", 0.7)
                    }

                    response = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=data,
                        timeout=30
                    )

                    if response.status_code == 200:
                        result = response.json()
                        # Create a simple response object
                        class SimpleResponse:
                            def __init__(self, data):
                                self.choices = [SimpleChoice(data['choices'][0])]

                        class SimpleChoice:
                            def __init__(self, choice_data):
                                self.message = SimpleMessage(choice_data['message'])

                        class SimpleMessage:
                            def __init__(self, message_data):
                                self.content = message_data['content']

                        return SimpleResponse(result)
                    else:
                        raise Exception(f"API request failed: {response.status_code} - {response.text}")

            # Create the minimal client
            minimal_client = MinimalGroqClient(api_key)

            # Add the chat attribute to match expected interface
            class ChatWrapper:
                def __init__(self, client):
                    self.completions = CompletionsWrapper(client)

            class CompletionsWrapper:
                def __init__(self, client):
                    self.client = client

                def create(self, **kwargs):
                    return self.client.chat_completions_create(**kwargs)

            minimal_client.chat = ChatWrapper(minimal_client)

            return minimal_client

        except Exception as e:
            print(f"❌ Failed to create minimal Groq client: {e}")
            return None



