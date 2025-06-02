from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, render_template, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_cors import CORS
from flask_session import Session
from backend.models import db, User
from backend.routes.auth import auth_bp
from backend.routes.emotion import emotion_bp
from backend.utils.email_service import EmailService
import os
import redis
from datetime import timedelta
from flask_session.sessions import RedisSessionInterface

def create_app():
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')
    static_dir = os.path.join(template_dir, 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    if isinstance(secret_key, bytes):
        secret_key = secret_key.decode('utf-8')
    app.config['SECRET_KEY'] = secret_key
    # Database configuration for production/development
    database_url = os.environ.get('DATABASE_URL')
    use_postgres = os.environ.get('USE_POSTGRES', 'false').lower() == 'true'

    if database_url:
        # Production: Use provided DATABASE_URL (Render will provide this)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print("🔧 Using production database from DATABASE_URL")
    elif use_postgres:
        # Development with PostgreSQL
        postgres_uri = 'postgresql://neondb_owner:npg_xjCwiJ2t9pLq@ep-orange-cake-a1jy3myz-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require'
        app.config['SQLALCHEMY_DATABASE_URI'] = postgres_uri
        print("🔧 Using PostgreSQL database for development")
    else:
        # Development with SQLite
        sqlite_uri = 'sqlite:///emotcare_local.db'
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
        print("🔧 Using SQLite database for development")
    app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
    try:
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'temp_sessions')
        app.config['SESSION_FILE_THRESHOLD'] = 100

        os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

        print("✅ Filesystem session configuration set (reliable)")
    except Exception as e:
        print(f"⚠️ Session configuration issue: {e}")
        app.config['SESSION_TYPE'] = 'null'
        print("⚠️ Using in-memory sessions as fallback")
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'faceauth1@gmail.com')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'kvik axuf aeqy yhex')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'faceauth1@gmail.com')

    db.init_app(app)
    bcrypt = Bcrypt(app)
    mail = Mail(app)
    CORS(app)
    Session(app)

    email_service = EmailService(mail)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(emotion_bp, url_prefix='/api')
    database_connected = False
    try:
        with app.app_context():
            db.create_all()
            database_connected = True
            print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Database connection issue: {e}")
        print("⚠️ Continuing without database - using mock data for testing")

    app.config['DATABASE_CONNECTED'] = database_connected

    print("✅ Session clearing configured for fresh start")

    @app.route('/clear-startup-sessions')
    def clear_startup_sessions():
        session.clear()
        return redirect(url_for('index'))

    @app.route('/')
    def index():
        if 'user_id' in session:
            try:
                user = db.session.get(User, session['user_id'])
                if user and user.is_verified:
                    return redirect(url_for('dashboard'))
            except:
                session.clear()

        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('index'))

        try:
            user = db.session.get(User, session['user_id'])
            if not user or not user.is_verified:
                return redirect(url_for('index'))
            return render_template('dashboard.html', user=user)
        except:
            class MockUser:
                def __init__(self):
                    self.username = "Test User"
                    self.email = "test@example.com"
                    self.id = 1
            return render_template('dashboard.html', user=MockUser())

    @app.route('/analytics')
    def analytics():
        if 'user_id' not in session:
            return redirect(url_for('index'))

        try:
            user = db.session.get(User, session['user_id'])
            if not user or not user.is_verified:
                return redirect(url_for('index'))
            return render_template('analytics.html', user=user)
        except:
            class MockUser:
                def __init__(self):
                    self.username = "Test User"
                    self.email = "test@example.com"
                    self.id = 1
            return render_template('analytics.html', user=MockUser())

    @app.route('/profile')
    def profile():
        if 'user_id' not in session:
            return redirect(url_for('index'))

        try:
            user = db.session.get(User, session['user_id'])
            if not user or not user.is_verified:
                return redirect(url_for('index'))
            return render_template('profile.html', user=user)
        except:
            class MockUser:
                def __init__(self):
                    self.username = "Test User"
                    self.email = "test@example.com"
                    self.id = 1
            return render_template('profile.html', user=MockUser())

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    @app.route('/test-groq')
    def test_groq():
        """Test Groq API functionality"""
        import os
        import asyncio
        from backend.utils.realtime_ai_chat import RealtimeAIChat

        results = {
            'environment_check': {},
            'groq_client_initialized': False,
            'basic_api_test': False,
            'chat_system_test': False,
            'error_messages': []
        }

        # Check environment variables
        results['environment_check'] = {
            'GROQ_API_KEY_set': bool(os.getenv('GROQ_API_KEY')),
            'GROQ_API_KEY_value': os.getenv('GROQ_API_KEY', 'NOT_SET')[:20] + '...' if os.getenv('GROQ_API_KEY') else 'NOT_SET',
            'USE_POSTGRES': os.getenv('USE_POSTGRES'),
            'FLASK_ENV': os.getenv('FLASK_ENV'),
            'PORT': os.getenv('PORT')
        }

        try:
            # Test AI chat initialization
            ai_chat = RealtimeAIChat()
            results['groq_client_initialized'] = bool(ai_chat.groq_client)

            if ai_chat.groq_client:
                # Test basic API call
                try:
                    response = ai_chat.groq_client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": "Test from Railway"}],
                        max_tokens=10
                    )
                    results['basic_api_test'] = True
                    results['test_response'] = response.choices[0].message.content

                    # Test the actual chat system
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        chat_response = loop.run_until_complete(
                            ai_chat.get_response("Hello, I'm feeling happy", "happy")
                        )
                        loop.close()
                        results['chat_system_test'] = True
                        results['chat_response'] = chat_response
                    except Exception as e:
                        results['error_messages'].append(f"Chat system test failed: {str(e)}")

                except Exception as e:
                    results['error_messages'].append(f"API call failed: {str(e)}")
            else:
                results['error_messages'].append("Groq client not initialized")

        except Exception as e:
            results['error_messages'].append(f"Initialization failed: {str(e)}")

        return results

    return app

# Create app instance for WSGI servers (Gunicorn, etc.)
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting EmotiCare Application...")
    print("🧹 All sessions will be cleared for fresh start")
    print("🔐 Application will start at login page")
    print("=" * 50)

    try:
        app = create_app()

        try:
            session_dir = app.config.get('SESSION_FILE_DIR')
            if session_dir and os.path.exists(session_dir):
                import glob
                session_files = glob.glob(os.path.join(session_dir, '*'))
                for file_path in session_files:
                    try:
                        os.remove(file_path)
                    except:
                        pass
                print(f"🧹 Cleaned up {len(session_files)} old session files")
        except Exception as e:
            print(f"⚠️ Session cleanup warning: {e}")

        if app.config.get('DATABASE_CONNECTED', False):
            print("✅ Application ready with database connection")
        else:
            print("⚠️ Application running in offline mode (no database)")
            print("💡 Tip: Set USE_POSTGRES=true environment variable to use PostgreSQL")

        print("🌐 Starting server on http://localhost:5000")
        print("=" * 50)

        app.run(debug=True, host='0.0.0.0', port=5000)

    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        print("💡 Application defaults to SQLite for local development")
        print("💡 Set USE_POSTGRES=true environment variable to use PostgreSQL")
        exit(1)
