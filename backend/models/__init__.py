# models/__init__.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Email verification
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    email_verified_at = db.Column(db.DateTime)
    
    # Password reset
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expires = db.Column(db.DateTime)
    
    # Relationships
    emotion_records = db.relationship('EmotionRecord', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_verified': self.is_verified
        }

class EmotionRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Emotion data
    emotion = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    detection_method = db.Column(db.String(20), default='webcam')  # webcam, upload, manual
    
    # User interaction
    user_response = db.Column(db.Text)
    suggestions_given = db.Column(db.Text)
    emotion_context = db.Column(db.Text)  # What was happening when emotion was detected
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'emotion': self.emotion,
            'confidence': self.confidence,
            'user_response': self.user_response,
            'suggestions_given': self.suggestions_given,
            'emotion_context': self.emotion_context,
            'detection_method': self.detection_method,
            'timestamp': self.timestamp.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
