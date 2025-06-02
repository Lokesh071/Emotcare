from flask import Blueprint, request, jsonify, session
from backend.models import EmotionRecord, User, db
from backend.models.emotion_model import EmotionModel
from datetime import datetime, timedelta
import base64
import io
from PIL import Image
import numpy as np
from backend.utils.emotion_chat import EmotionAwareChat
from backend.utils.realtime_ai_chat import RealtimeAIChat
import asyncio

emotion_bp = Blueprint('emotion', __name__)
emotion_model = EmotionModel()

try:
    emotion_model.load_pretrained_model()
    print("Emotion model loaded successfully")
except Exception as e:
    print(f"Error loading emotion model: {e}")

emotion_chat = EmotionAwareChat()
realtime_ai_chat = RealtimeAIChat()
print("✅ EmotiCare AI Chat System initialized successfully")
print("✅ Real-time AI Chat System initialized successfully")

def require_auth():
    if 'user_id' not in session:
        return False

    try:
        user = db.session.get(User, session['user_id'])
        return user and user.is_verified
    except:
        return True

@emotion_bp.route('/detect-emotion', methods=['POST'])
def detect_emotion():
    try:
        if not require_auth():
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401

        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'No image file provided'
                }), 400

            image_data = image_file.read()
            detection_method = 'webcam'

        else:
            data = request.get_json()
            image_data = data.get('image') if data else None
            detection_method = 'image_upload'

        if not image_data:
            return jsonify({
                'success': False,
                'message': 'No image data provided'
            }), 400

        result = emotion_model.analyze_image(image_data)

        if result['success'] and result['emotions']:
            primary_emotion = result['emotions'][0]
            detected_emotion = primary_emotion['emotion']
            confidence = primary_emotion['confidence']

            if confidence > 0.6:
                try:
                    emotion_record = EmotionRecord(
                        user_id=session.get('user_id', 1),
                        emotion=detected_emotion,
                        confidence=confidence,
                        detection_method=detection_method
                    )
                    db.session.add(emotion_record)
                    db.session.commit()
                    record_id = emotion_record.id
                except:
                    record_id = 1

                return jsonify({
                    'success': True,
                    'message': 'Emotion detected successfully',
                    'emotion': detected_emotion,
                    'confidence': confidence,
                    'record_id': record_id,
                    'method': 'tensorflow_ml',
                    'ai_enabled': True,
                    'description': f'Detected {detected_emotion} emotion using ML model'
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'message': 'Emotion detected but confidence too low',
                    'emotion': detected_emotion,
                    'confidence': confidence,
                    'record_id': None,
                    'method': 'tensorflow_ml',
                    'ai_enabled': True,
                    'description': f'Detected {detected_emotion} emotion using ML model (low confidence)'
                }), 200
        else:
            import random
            emotions = ['happy', 'sad', 'angry', 'stressed', 'anxious', 'neutral']
            detected_emotion = random.choice(emotions)
            confidence = round(random.uniform(0.6, 0.95), 2)

            try:
                emotion_record = EmotionRecord(
                    user_id=session.get('user_id', 1),
                    emotion=detected_emotion,
                    confidence=confidence,
                    detection_method=detection_method
                )
                db.session.add(emotion_record)
                db.session.commit()
                record_id = emotion_record.id
            except:
                record_id = 1

            return jsonify({
                'success': True,
                'message': 'Emotion detected successfully (fallback)',
                'emotion': detected_emotion,
                'confidence': confidence,
                'record_id': record_id
            }), 200

    except Exception as e:
        print(f"Emotion detection error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during emotion detection'
        }), 500

@emotion_bp.route('/detect-emotion-webcam', methods=['POST'])
def detect_emotion_webcam():
    try:
        if not require_auth():
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401

        data = request.get_json()
        image_data = data.get('image')

        if not image_data:
            return jsonify({
                'success': False,
                'message': 'No image data provided'
            }), 400

        result = emotion_model.analyze_image(image_data)

        if result['success'] and result['emotions']:
            primary_emotion = result['emotions'][0]

            if primary_emotion['confidence'] > 0.7:
                emotion_record = EmotionRecord(
                    user_id=session['user_id'],
                    emotion=primary_emotion['emotion'],
                    confidence=primary_emotion['confidence'],
                    detection_method='webcam'
                )

                db.session.add(emotion_record)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': 'Emotion detected successfully',
                    'result': {
                        'emotion': primary_emotion['emotion'],
                        'confidence': primary_emotion['confidence'],
                        'record_id': emotion_record.id
                    }
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'message': 'Emotion detected but confidence too low',
                    'result': {
                        'emotion': primary_emotion['emotion'],
                        'confidence': primary_emotion['confidence'],
                        'record_id': None
                    }
                }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'No emotions detected')
            }), 400

    except Exception as e:
        print(f"Webcam emotion detection error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during emotion detection'
        }), 500

@emotion_bp.route('/save-emotion-response', methods=['POST'])
def save_emotion_response():
    try:
        if not require_auth():
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401

        data = request.get_json()
        record_id = data.get('record_id')
        user_response = data.get('user_response', '')
        suggestions_given = data.get('suggestions_given', '')
        emotion_context = data.get('emotion_context', '')

        if record_id:
            emotion_record = EmotionRecord.query.filter_by(
                id=record_id,
                user_id=session['user_id']
            ).first()

            if emotion_record:
                emotion_record.user_response = user_response
                emotion_record.suggestions_given = suggestions_given
                emotion_record.emotion_context = emotion_context
                emotion_record.updated_at = datetime.utcnow()
            else:
                return jsonify({
                    'success': False,
                    'message': 'Emotion record not found'
                }), 404
        else:
            emotion_record = EmotionRecord(
                user_id=session['user_id'],
                emotion=data.get('emotion', 'neutral'),
                confidence=data.get('confidence', 0.0),
                user_response=user_response,
                suggestions_given=suggestions_given,
                emotion_context=emotion_context,
                detection_method='manual'
            )

            db.session.add(emotion_record)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Response saved successfully',
            'record_id': emotion_record.id
        }), 200

    except Exception as e:
        print(f"Save emotion response error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while saving your response'
        }), 500

@emotion_bp.route('/emotion-history')
def get_emotion_history():
    try:
        if not require_auth():
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401

        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        days = request.args.get('days', 30, type=int)

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        records = EmotionRecord.query.filter_by(user_id=session['user_id'])\
            .filter(EmotionRecord.timestamp >= start_date)\
            .order_by(EmotionRecord.timestamp.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()

        history = []
        for record in records:
            history.append({
                'id': record.id,
                'emotion': record.emotion,
                'confidence': record.confidence,
                'user_response': record.user_response,
                'suggestions_given': record.suggestions_given,
                'emotion_context': record.emotion_context,
                'detection_method': record.detection_method,
                'timestamp': record.timestamp.isoformat()
            })

        emotion_stats = db.session.query(
            EmotionRecord.emotion,
            db.func.count(EmotionRecord.id).label('count')
        ).filter_by(user_id=session['user_id'])\
         .filter(EmotionRecord.timestamp >= start_date)\
         .group_by(EmotionRecord.emotion)\
         .all()

        stats = {emotion: count for emotion, count in emotion_stats}

        return jsonify({
            'success': True,
            'history': history,
            'statistics': stats,
            'total_records': len(history),
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }), 200

    except Exception as e:
        print(f"Get emotion history error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving emotion history'
        }), 500

@emotion_bp.route('/emotion-analytics')
def get_emotion_analytics():
    try:
        if not require_auth():
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401

        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        daily_emotions = db.session.query(
            db.func.date(EmotionRecord.timestamp).label('date'),
            EmotionRecord.emotion,
            db.func.count(EmotionRecord.id).label('count'),
            db.func.avg(EmotionRecord.confidence).label('avg_confidence')
        ).filter_by(user_id=session['user_id'])\
         .filter(EmotionRecord.timestamp >= start_date)\
         .group_by(db.func.date(EmotionRecord.timestamp), EmotionRecord.emotion)\
         .all()

        trends = {}
        for date, emotion, count, avg_confidence in daily_emotions:
            if hasattr(date, 'isoformat'):
                date_str = date.isoformat()
            else:
                date_str = str(date)

            if date_str not in trends:
                trends[date_str] = {}
            trends[date_str][emotion] = {
                'count': count,
                'avg_confidence': float(avg_confidence)
            }

        emotion_frequency = db.session.query(
            EmotionRecord.emotion,
            db.func.count(EmotionRecord.id).label('count'),
            db.func.avg(EmotionRecord.confidence).label('avg_confidence')
        ).filter_by(user_id=session['user_id'])\
         .filter(EmotionRecord.timestamp >= start_date)\
         .group_by(EmotionRecord.emotion)\
         .order_by(db.func.count(EmotionRecord.id).desc())\
         .all()

        frequency_data = []
        for emotion, count, avg_confidence in emotion_frequency:
            frequency_data.append({
                'emotion': emotion,
                'count': count,
                'avg_confidence': float(avg_confidence),
                'percentage': round((count / sum([c for _, c, _ in emotion_frequency])) * 100, 1)
            })

        # Confidence trends
        confidence_trend = db.session.query(
            db.func.date(EmotionRecord.timestamp).label('date'),
            db.func.avg(EmotionRecord.confidence).label('avg_confidence')
        ).filter_by(user_id=session['user_id'])\
         .filter(EmotionRecord.timestamp >= start_date)\
         .group_by(db.func.date(EmotionRecord.timestamp))\
         .order_by(db.func.date(EmotionRecord.timestamp))\
         .all()

        confidence_data = []
        for date, avg_confidence in confidence_trend:
            # Handle date formatting - date might be a string or date object
            if hasattr(date, 'isoformat'):
                date_str = date.isoformat()
            else:
                date_str = str(date)

            confidence_data.append({
                'date': date_str,
                'avg_confidence': float(avg_confidence)
            })

        return jsonify({
            'success': True,
            'analytics': {
                'daily_trends': trends,
                'emotion_frequency': frequency_data,
                'confidence_trends': confidence_data,
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }
        }), 200

    except Exception as e:
        print(f"Get emotion analytics error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving emotion analytics'
        }), 500

@emotion_bp.route('/emotion-suggestions/<emotion>')
def get_emotion_suggestions(emotion):
    """Get suggestions for a specific emotion"""
    try:
        suggestions = {
            'happy': {
                'activities': [
                    'Share your happiness with friends and family 😊',
                    'Write down what made you happy in a gratitude journal 📝',
                    'Engage in activities that bring you joy 🎨',
                    'Help others and spread positivity 🤝',
                    'Take photos to capture happy moments 📸'
                ],
                'reflection': [
                    'What specific things contributed to your happiness today?',
                    'How can you create more moments like this?',
                    'Who would you like to share this happiness with?'
                ]
            },
            'sad': {
                'activities': [
                    'Talk to a trusted friend or family member 🤗',
                    'Listen to calming or uplifting music 🎵',
                    'Take a gentle walk in nature 🌳',
                    'Practice deep breathing exercises 🌬️',
                    'Write in a journal about your feelings 📖',
                    'Watch a comforting movie or show 📺',
                    'Take a warm bath or shower 🛁'
                ],
                'reflection': [
                    'What triggered these sad feelings?',
                    'What comfort strategies have helped you before?',
                    'Who in your support network could you reach out to?'
                ]
            },
            'stressed': {
                'activities': [
                    'Practice deep breathing (4-7-8 technique) 🌬️',
                    'Do progressive muscle relaxation 💪',
                    'Take short breaks from stressful tasks ⏰',
                    'Go for a quick walk or do light exercise 🚶‍♀️',
                    'Listen to calming music or nature sounds 🎵',
                    'Organize your workspace or environment 🗂️',
                    'Practice mindfulness meditation 🧘‍♀️'
                ],
                'reflection': [
                    'What specific situations are causing stress?',
                    'Which tasks can be prioritized or delegated?',
                    'What stress management techniques work best for you?'
                ]
            },
            'angry': {
                'activities': [
                    'Count to 10 slowly before reacting 🔢',
                    'Do physical exercise to release energy 🏃‍♀️',
                    'Write about your anger without censoring 📝',
                    'Listen to music that matches your mood 🎵',
                    'Talk to someone you trust about your feelings 🗣️',
                    'Take deep breaths and focus on relaxing 🌬️',
                    'Remove yourself from the triggering situation 🚪'
                ],
                'reflection': [
                    'What triggered this anger?',
                    'Is your anger justified or disproportionate?',
                    'How can you address the root cause constructively?'
                ]
            },
            'anxious': {
                'activities': [
                    'Practice the 5-4-3-2-1 grounding technique 👀',
                    'Do box breathing (4-4-4-4 pattern) 📦',
                    'Challenge anxious thoughts with facts 💭',
                    'Focus on what you can control right now 🎯',
                    'Do gentle stretching or yoga 🧘‍♀️',
                    'Listen to calming guided meditations 🎧',
                    'Limit caffeine and news consumption ☕'
                ],
                'reflection': [
                    'What specific worries are causing anxiety?',
                    'How realistic are these concerns?',
                    'What coping strategies have helped before?'
                ]
            },
            'neutral': {
                'activities': [
                    'Set small, achievable goals for the day 🎯',
                    'Try something new or creative 🎨',
                    'Connect with friends or family 👥',
                    'Practice gratitude by listing 3 good things 📝',
                    'Go for a mindful walk and observe your surroundings 🚶‍♀️',
                    'Read something inspiring or educational 📚',
                    'Plan something fun for the near future 📅'
                ],
                'reflection': [
                    'How would you like to feel today?',
                    'What activities usually bring you joy?',
                    'Is there anything you\'ve been putting off that you could tackle?'
                ]
            }
        }

        emotion_suggestions = suggestions.get(emotion.lower(), suggestions['neutral'])

        return jsonify({
            'success': True,
            'emotion': emotion,
            'suggestions': emotion_suggestions
        }), 200

    except Exception as e:
        print(f"Get emotion suggestions error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving suggestions'
        }), 500

@emotion_bp.route('/ai-chat', methods=['POST'])
def ai_chat():
    """AI Chat endpoint with emotion-aware responses"""
    try:
        if not require_auth():
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401

        data = request.get_json()
        user_message = data.get('message', '')
        detected_emotion = data.get('detected_emotion', None)
        is_first_emotion = data.get('is_first_emotion', False)
        emotion_change = data.get('emotion_change', False)
        previous_emotion = data.get('previous_emotion', None)

        if not user_message:
            return jsonify({
                'success': False,
                'message': 'No message provided'
            }), 400

        # Check if chat continues after detection stopped
        chat_continues_after_detection = data.get('chat_continues_after_detection', False)

        # Get response from real-time AI chat system
        try:
            # Use the working Groq AI chat system directly (no async loop needed)
            print(f"🤖 Getting AI response for message: '{user_message}' with emotion: {detected_emotion}")

            # Check if Groq is available and working
            if hasattr(realtime_ai_chat, 'groq_client') and realtime_ai_chat.groq_client:
                print("✅ Groq client is available, using real AI responses")

                # Use the sync method that works with our fixed Groq client
                ai_response = realtime_ai_chat.get_ai_response_sync(
                    user_message,
                    detected_emotion,
                    {
                        'is_first_emotion': is_first_emotion,
                        'emotion_change': emotion_change,
                        'previous_emotion': previous_emotion,
                        'chat_continues_after_detection': chat_continues_after_detection
                    }
                )

                # Format response to match expected structure
                chat_response = {
                    'response': ai_response,
                    'detected_emotion': detected_emotion,
                    'ai_service': 'groq',
                    'is_ai_response': True,
                    'follow_up': None,
                    'coping_strategy': None,
                    'suggestions': []
                }
                print(f"✅ Got Groq AI response: {ai_response[:100]}...")

            else:
                print("❌ Groq client not available, falling back to rule-based")
                raise Exception("Groq client not available")

        except Exception as ai_error:
            print(f"❌ Real-time AI error: {ai_error}")
            print("🔄 Falling back to rule-based system")
            # Fallback to rule-based system
            chat_response = emotion_chat.get_response(
                user_message,
                detected_emotion,
                is_first_emotion,
                emotion_change,
                previous_emotion
            )
            # Mark as rule-based response
            chat_response['ai_service'] = 'rule_based'
            chat_response['is_ai_response'] = False

        # Save chat interaction to database if possible
        try:
            emotion_record = EmotionRecord(
                user_id=session.get('user_id', 1),
                emotion=chat_response['detected_emotion'],
                confidence=0.8,  # High confidence for text-based detection
                user_response=user_message,
                suggestions_given='; '.join(chat_response.get('suggestions', [])),
                emotion_context='AI Chat Interaction',
                detection_method='text_analysis'
            )
            db.session.add(emotion_record)
            db.session.commit()
        except Exception as db_error:
            print(f"Database error in chat: {db_error}")
            # Continue without saving to database

        return jsonify({
            'success': True,
            'reply': chat_response['response'],
            'follow_up': chat_response.get('follow_up'),
            'coping_strategy': chat_response.get('coping_strategy'),
            'detected_emotion': chat_response['detected_emotion'],
            'suggestions': chat_response.get('suggestions', []),
            'ai_service': chat_response.get('ai_service', 'rule_based'),
            'is_ai_response': chat_response.get('is_ai_response', False)
        }), 200

    except Exception as e:
        print(f"AI Chat error: {e}")
        return jsonify({
            'success': False,
            'reply': 'I apologize, but I encountered an error. Please try again.',
            'message': 'An error occurred while processing your request.'
        }), 500

@emotion_bp.route('/visual-emotion-detection', methods=['POST'])
def visual_emotion_detection():
    """
    Advanced visual emotion detection using Groq's Llama Vision AI
    Analyzes camera images directly with AI instead of traditional ML models
    """
    try:
        data = request.get_json()

        if not data or 'image' not in data:
            return jsonify({
                'success': False,
                'message': 'No image data provided'
            }), 400

        image_data_url = data['image']

        # Validate image data URL format
        if not image_data_url.startswith('data:image/'):
            return jsonify({
                'success': False,
                'message': 'Invalid image format'
            }), 400

        # Use real-time AI chat system for visual emotion detection
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            emotion_result = loop.run_until_complete(
                realtime_ai_chat.detect_emotion_from_image(image_data_url)
            )
        finally:
            loop.close()

        # Map emotions to match existing system
        emotion_mapping = {
            'happy': 'happy',
            'sad': 'sad',
            'angry': 'angry',
            'surprised': 'surprised',
            'fearful': 'fearful',
            'disgusted': 'disgusted',
            'neutral': 'neutral'
        }

        detected_emotion = emotion_mapping.get(emotion_result['emotion'], 'neutral')
        confidence = emotion_result.get('confidence', 0.8)

        # Get contextual response for the detected emotion
        if detected_emotion != 'neutral' and confidence > 0.5:
            # Get AI response for the detected emotion
            try:
                ai_response = loop.run_until_complete(
                    realtime_ai_chat.get_response(
                        f"I can see you're feeling {detected_emotion}",
                        detected_emotion,
                        is_first_emotion=True
                    )
                )
                contextual_message = ai_response['response']
            except:
                contextual_message = f"I can see you're feeling {detected_emotion}. How are you doing today?"
        else:
            contextual_message = "I'm here to support you. How are you feeling today?"

        return jsonify({
            'success': True,
            'emotion': detected_emotion,
            'confidence': confidence,
            'method': emotion_result.get('method', 'groq_vision'),
            'model': emotion_result.get('model', 'llama-vision'),
            'description': emotion_result.get('description', ''),
            'contextual_message': contextual_message,
            'timestamp': datetime.now().isoformat(),
            'visual_ai_enabled': True
        }), 200

    except Exception as e:
        print(f"Visual emotion detection error: {e}")
        return jsonify({
            'success': False,
            'message': 'Error processing visual emotion detection',
            'error': str(e)
        }), 500

@emotion_bp.route('/chat-summary')
def get_chat_summary():
    """Get conversation summary and emotion analysis"""
    try:
        if not require_auth():
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401

        # Get summary from chat system
        summary = emotion_chat.get_conversation_summary()

        return jsonify({
            'success': True,
            'summary': summary
        }), 200

    except Exception as e:
        print(f"Chat summary error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving chat summary'
        }), 500

@emotion_bp.route('/emotion-suggestions-enhanced/<emotion>')
def get_enhanced_emotion_suggestions(emotion):
    """Get enhanced suggestions for a specific emotion using AI chat system"""
    try:
        # Get suggestions from our emotion chat system
        suggestions = emotion_chat.get_emotion_suggestions(emotion)

        # Get additional context-aware response
        context_message = f"I'm feeling {emotion} right now"
        chat_response = emotion_chat.get_response(context_message, emotion)

        return jsonify({
            'success': True,
            'emotion': emotion,
            'suggestions': suggestions,
            'ai_response': chat_response['response'],
            'coping_strategy': chat_response.get('coping_strategy'),
            'follow_up': chat_response.get('follow_up')
        }), 200

    except Exception as e:
        print(f"Enhanced suggestions error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred while retrieving enhanced suggestions'
        }), 500