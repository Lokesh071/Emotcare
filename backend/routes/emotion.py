# routes/emotion.py
from flask import Blueprint, request, jsonify, session
from models import EmotionRecord, User, db
from models.emotion_model import EmotionModel
from datetime import datetime, timedelta
import base64
import io
from PIL import Image
import numpy as np

emotion_bp = Blueprint('emotion', __name__)
emotion_model = EmotionModel()

# Initialize the emotion model
try:
    emotion_model.load_pretrained_model()
    print("Emotion model loaded successfully")
except Exception as e:
    print(f"Error loading emotion model: {e}")

def require_auth():
    """Check if user is authenticated"""
    if 'user_id' not in session:
        return False
    
    user = User.query.get(session['user_id'])
    return user and user.is_verified

@emotion_bp.route('/detect-emotion', methods=['POST'])
def detect_emotion():
    """Detect emotion from uploaded image"""
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
        
        # Analyze the image for emotions
        result = emotion_model.analyze_image(image_data)
        
        if result['success'] and result['emotions']:
            # Get the primary emotion (first detected face)
            primary_emotion = result['emotions'][0]
            
            # Save emotion record
            emotion_record = EmotionRecord(
                user_id=session['user_id'],
                emotion=primary_emotion['emotion'],
                confidence=primary_emotion['confidence'],
                detection_method='image_upload'
            )
            
            db.session.add(emotion_record)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Emotion detected successfully',
                'result': {
                    'emotion': primary_emotion['emotion'],
                    'confidence': primary_emotion['confidence'],
                    'all_faces': result['emotions'],
                    'record_id': emotion_record.id
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result.get('message', 'No emotions detected'),
                'result': result
            }), 400
            
    except Exception as e:
        print(f"Emotion detection error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during emotion detection'
        }), 500

@emotion_bp.route('/detect-emotion-webcam', methods=['POST'])
def detect_emotion_webcam():
    """Detect emotion from webcam capture"""
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
        
        # Analyze the image for emotions
        result = emotion_model.analyze_image(image_data)
        
        if result['success'] and result['emotions']:
            # Get the primary emotion (first detected face)
            primary_emotion = result['emotions'][0]
            
            # Only save if confidence is high enough for webcam detection
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
    """Save user's response to emotion detection"""
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
            # Update existing record
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
            # Create new record
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
    """Get user's emotion history"""
    try:
        if not require_auth():
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401
        
        # Get query parameters
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        days = request.args.get('days', 30, type=int)
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query emotion records
        records = EmotionRecord.query.filter_by(user_id=session['user_id'])\
            .filter(EmotionRecord.timestamp >= start_date)\
            .order_by(EmotionRecord.timestamp.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        # Format response
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
        
        # Get emotion statistics
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
    """Get detailed emotion analytics"""
    try:
        if not require_auth():
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401
        
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Daily emotion trends
        daily_emotions = db.session.query(
            db.func.date(EmotionRecord.timestamp).label('date'),
            EmotionRecord.emotion,
            db.func.count(EmotionRecord.id).label('count'),
            db.func.avg(EmotionRecord.confidence).label('avg_confidence')
        ).filter_by(user_id=session['user_id'])\
         .filter(EmotionRecord.timestamp >= start_date)\
         .group_by(db.func.date(EmotionRecord.timestamp), EmotionRecord.emotion)\
         .all()
        
        # Format daily trends
        trends = {}
        for date, emotion, count, avg_confidence in daily_emotions:
            date_str = date.isoformat()
            if date_str not in trends:
                trends[date_str] = {}
            trends[date_str][emotion] = {
                'count': count,
                'avg_confidence': float(avg_confidence)
            }
        
        # Most frequent emotions
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
            confidence_data.append({
                'date': date.isoformat(),
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
