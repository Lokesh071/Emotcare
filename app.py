from flask import Flask, render_template, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_cors import CORS
from flask_session import Session
from models import db, User
from routes.auth import auth_bp
from routes.emotion import emotion_bp
from utils.email_service import EmailService
import os
import redis
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///emotion_app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    
    # Redis configuration for session management
    redis_url = os.environ.get('REDIS_URL', 'redis://default:AZrAAAIjcDE0ODA0MzFiMWVmYmI0NjU2OTM4NjMyNmM3ODBmZDFiNXAxMA@talented-shrimp-39616.upstash.io:6379')
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_REDIS'] = redis.from_url(redis_url, ssl=True)
    
    # Email configuration
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'faceauth01@gmail.com')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'tavx rome qann smoq')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'faceauth01@gmail.com')
    
    # Initialize extensions
    db.init_app(app)
    bcrypt = Bcrypt(app)
    mail = Mail(app)
    CORS(app)
    Session(app)
    
    # Initialize email service
    email_service = EmailService(mail)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(emotion_bp, url_prefix='/api')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Routes
    @app.route('/')
    def index():
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user and user.is_verified:
                return render_template('dashboard.html', user=user)
        return render_template('login.html')
    
    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_verified:
            return redirect(url_for('index'))
        
        return render_template('dashboard.html', user=user)
    
    @app.route('/analytics')
    def analytics():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_verified:
            return redirect(url_for('index'))
        
        return render_template('analytics.html', user=user)
    
    @app.route('/profile')
    def profile():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        
        user = User.query.get(session['user_id'])
        if not user or not user.is_verified:
            return redirect(url_for('index'))
        
        return render_template('profile.html', user=user)
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
