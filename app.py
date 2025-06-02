from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from flask import Flask, render_template, session, redirect, url_for, jsonify
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
        # Production: Use provided DATABASE_URL (Render/Railway will provide this)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        print("🔧 Using production database from DATABASE_URL")
    elif use_postgres:
        # Development with PostgreSQL (Example URI, replace if needed)
        postgres_uri = os.environ.get('POSTGRES_URI', 'postgresql://user:password@host:port/dbname')
        app.config['SQLALCHEMY_DATABASE_URI'] = postgres_uri
        print("🔧 Using PostgreSQL database for development")
    else:
        # Development with SQLite
        sqlite_db_path = os.path.join(app.instance_path, 'emotcare_local.db')
        os.makedirs(app.instance_path, exist_ok=True)
        sqlite_uri = f'sqlite:///{sqlite_db_path}'
        app.config['SQLALCHEMY_DATABASE_URI'] = sqlite_uri
        print(f"🔧 Using SQLite database for development at {sqlite_uri}")

    app.config['REDIS_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

    # Session Configuration (Filesystem recommended for simplicity unless Redis is required)
    try:
        app.config['SESSION_TYPE'] = 'filesystem'
        app.config['SESSION_PERMANENT'] = False
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_FILE_DIR'] = os.path.join(os.getcwd(), 'temp_sessions')
        app.config['SESSION_FILE_THRESHOLD'] = 100 # Number of sessions before cleanup
        os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
        print("✅ Filesystem session configuration set.")
    except Exception as e:
        print(f"⚠️ Filesystem session configuration issue: {e}. Falling back to null session.")
        app.config['SESSION_TYPE'] = 'null'

    # Mail Configuration with fallbacks to hardcoded values
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'false').lower() == 'true'

    # Use environment variables first, then fallback to hardcoded credentials
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'faceauth1@gmail.com')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'kvik axuf aeqy yhex')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', app.config['MAIL_USERNAME'])

    # Debug logging for email configuration
    print(f"📧 Email Configuration:")
    print(f"   MAIL_SERVER: {app.config['MAIL_SERVER']}")
    print(f"   MAIL_PORT: {app.config['MAIL_PORT']}")
    print(f"   MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"   MAIL_PASSWORD: {'***SET***' if app.config['MAIL_PASSWORD'] else 'NOT_SET'}")
    print(f"   MAIL_DEFAULT_SENDER: {app.config['MAIL_DEFAULT_SENDER']}")

    # Initialize extensions
    db.init_app(app)
    bcrypt = Bcrypt(app)
    mail = Mail(app)
    CORS(app) # Enable CORS for all routes
    Session(app)

    # Initialize Email Service
    email_service = EmailService(mail)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(emotion_bp, url_prefix='/api')

    # Create database tables if they don't exist
    database_connected = False
    try:
        with app.app_context():
            db.create_all()
            database_connected = True
            print("✅ Database tables checked/created successfully")
    except Exception as e:
        print(f"⚠️ Database connection/setup issue: {e}")
        print("⚠️ Application might run with limited functionality.")

    app.config['DATABASE_CONNECTED'] = database_connected

    # --- Routes --- #

    @app.route('/')
    def index():
        if 'user_id' in session:
            try:
                # Check if user exists and is verified
                user = db.session.get(User, session['user_id'])
                if user and user.is_verified:
                    return redirect(url_for('dashboard'))
                else:
                    session.clear() # Clear invalid session
            except Exception as e:
                print(f"Error checking session user: {e}")
                session.clear()
        # If no valid session, show login
        return render_template('login.html')

    @app.route('/dashboard')
    def dashboard():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        try:
            user = db.session.get(User, session['user_id'])
            if not user or not user.is_verified:
                session.clear()
                return redirect(url_for('index'))
            return render_template('dashboard.html', user=user)
        except Exception as e:
            print(f"Error loading dashboard: {e}")
            # Fallback for DB issues during demo/testing
            class MockUser: username, email, id = "Test User", "test@example.com", 1
            return render_template('dashboard.html', user=MockUser())

    @app.route('/analytics')
    def analytics():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        try:
            user = db.session.get(User, session['user_id'])
            if not user or not user.is_verified:
                session.clear()
                return redirect(url_for('index'))
            return render_template('analytics.html', user=user)
        except Exception as e:
            print(f"Error loading analytics: {e}")
            class MockUser: username, email, id = "Test User", "test@example.com", 1
            return render_template('analytics.html', user=MockUser())

    @app.route('/profile')
    def profile():
        if 'user_id' not in session:
            return redirect(url_for('index'))
        try:
            user = db.session.get(User, session['user_id'])
            if not user or not user.is_verified:
                session.clear()
                return redirect(url_for('index'))
            return render_template('profile.html', user=user)
        except Exception as e:
            print(f"Error loading profile: {e}")
            class MockUser: username, email, id = "Test User", "test@example.com", 1
            return render_template('profile.html', user=MockUser())

    # --- Error Handlers --- #
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        # Log the error for debugging
        print(f"Internal Server Error: {error}")
        db.session.rollback() # Rollback potentially failed DB transactions
        return render_template('500.html'), 500

    # --- Groq Test Route (Modified) --- #
    @app.route('/test-groq')
    def test_groq():
        """Test Groq API functionality using the fixed RealtimeAIChat class."""
        import os
        import asyncio
        # *** MODIFIED: Import the fixed version ***
        from backend.utils.realtime_ai_chat import RealtimeAIChat, GROQ_AVAILABLE

        results = {
            'environment_check': {},
            'groq_library_available': GROQ_AVAILABLE,
            'realtime_ai_chat_init': {},
            'groq_client_initialized_in_chat': False,
            'api_connection_test': {},
            'error_messages': [],
            'debug_logs': [] # Collect logs during the test
        }

        # 1. Check Environment Variables
        groq_api_key_env = os.getenv('GROQ_API_KEY')
        results['environment_check'] = {
            'GROQ_API_KEY_set': bool(groq_api_key_env),
            'GROQ_API_KEY_value_preview': groq_api_key_env[:20] + '...' if groq_api_key_env else 'NOT_SET',
            'PORT': os.getenv('PORT')
        }
        results['debug_logs'].append(f"Env Check: GROQ_API_KEY is {'SET' if groq_api_key_env else 'NOT SET'}")

        if not GROQ_AVAILABLE:
            results['error_messages'].append("Groq library not installed or import failed.")
            results['debug_logs'].append("❌ Groq library not available, skipping further tests.")
            return jsonify(results)

        # 2. Test RealtimeAIChat Initialization (using the fixed class)
        try:
            results['debug_logs'].append("Attempting to initialize RealtimeAIChat (fixed version)...")
            # Use a temporary instance for testing
            ai_chat_tester = RealtimeAIChat()
            results['realtime_ai_chat_init']['success'] = True
            results['groq_client_initialized_in_chat'] = bool(ai_chat_tester.groq_client)
            results['debug_logs'].append(f"RealtimeAIChat initialized. Groq client inside: {bool(ai_chat_tester.groq_client)}")

            if not ai_chat_tester.groq_client:
                 results['error_messages'].append("Groq client failed to initialize within RealtimeAIChat.")
                 results['debug_logs'].append("❌ Groq client is None after RealtimeAIChat init.")
            else:
                results['debug_logs'].append("✅ Groq client seems initialized within RealtimeAIChat.")
                # 3. Test API Connection via the initialized client
                try:
                    results['debug_logs'].append("Attempting API connection test via RealtimeAIChat client...")
                    test_response = ai_chat_tester.groq_client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": "Test from Railway (fixed)"}],
                        max_tokens=10,
                        timeout=30 # Keep timeout
                    )
                    results['api_connection_test']['success'] = True
                    results['api_connection_test']['response_preview'] = test_response.choices[0].message.content
                    results['debug_logs'].append(f"✅ API Connection Test successful. Response: {test_response.choices[0].message.content}")
                except Exception as api_e:
                    results['api_connection_test']['success'] = False
                    results['api_connection_test']['error'] = str(api_e)
                    results['error_messages'].append(f"API connection test failed: {api_e}")
                    results['debug_logs'].append(f"❌ API Connection Test failed: {api_e}")

        except Exception as init_e:
            results['realtime_ai_chat_init']['success'] = False
            results['realtime_ai_chat_init']['error'] = str(init_e)
            results['error_messages'].append(f"Failed to initialize RealtimeAIChat: {init_e}")
            results['debug_logs'].append(f"❌ RealtimeAIChat initialization failed: {init_e}")

        return jsonify(results)

    # --- Email Configuration Test Route --- #
    @app.route('/test-email')
    def test_email():
        """Test email configuration and SMTP settings."""
        results = {
            'email_config': {},
            'smtp_test': {},
            'environment_variables': {},
            'error_messages': [],
            'debug_logs': []
        }

        # Check email configuration
        results['email_config'] = {
            'MAIL_SERVER': app.config.get('MAIL_SERVER'),
            'MAIL_PORT': app.config.get('MAIL_PORT'),
            'MAIL_USE_TLS': app.config.get('MAIL_USE_TLS'),
            'MAIL_USE_SSL': app.config.get('MAIL_USE_SSL'),
            'MAIL_USERNAME': app.config.get('MAIL_USERNAME'),
            'MAIL_PASSWORD': '***SET***' if app.config.get('MAIL_PASSWORD') else 'NOT_SET',
            'MAIL_DEFAULT_SENDER': app.config.get('MAIL_DEFAULT_SENDER')
        }

        # Check environment variables
        results['environment_variables'] = {
            'MAIL_SERVER': os.environ.get('MAIL_SERVER', 'NOT_SET'),
            'MAIL_PORT': os.environ.get('MAIL_PORT', 'NOT_SET'),
            'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', 'NOT_SET'),
            'MAIL_USERNAME': os.environ.get('MAIL_USERNAME', 'NOT_SET'),
            'MAIL_PASSWORD': '***SET***' if os.environ.get('MAIL_PASSWORD') else 'NOT_SET',
            'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER', 'NOT_SET')
        }

        # Check if SMTP credentials are configured
        mail_username = app.config.get('MAIL_USERNAME')
        mail_password = app.config.get('MAIL_PASSWORD')

        if not mail_username or not mail_password:
            results['error_messages'].append("SMTP credentials not configured")
            results['debug_logs'].append("❌ MAIL_USERNAME or MAIL_PASSWORD not set")
        else:
            results['debug_logs'].append("✅ SMTP credentials are configured")

            # Test SMTP connection
            try:
                import smtplib
                smtp_server = app.config.get('MAIL_SERVER', 'smtp.gmail.com')
                smtp_port = app.config.get('MAIL_PORT', 587)

                results['debug_logs'].append(f"🔧 Testing SMTP connection to {smtp_server}:{smtp_port}")

                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(mail_username, mail_password)

                results['smtp_test']['success'] = True
                results['debug_logs'].append("✅ SMTP connection test successful")

            except Exception as e:
                results['smtp_test']['success'] = False
                results['smtp_test']['error'] = str(e)
                results['error_messages'].append(f"SMTP connection failed: {e}")
                results['debug_logs'].append(f"❌ SMTP connection failed: {e}")

        return jsonify(results)

    return app

# Create app instance for WSGI servers (Gunicorn, Waitress, etc.)
app = create_app()

if __name__ == '__main__':
    print("🚀 Starting EmotiCare Application in Development Mode...")
    # Use waitress for a production-like WSGI server locally if desired
    # from waitress import serve
    # serve(app, host='0.0.0.0', port=5000)
    # Or use Flask's built-in server for debugging:
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

