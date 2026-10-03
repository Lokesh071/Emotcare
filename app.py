
import os
import secrets
import logging
from datetime import timedelta

from flask import Flask, render_template, session, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_cors import CORS
from flask_session import Session
from backend.models import db, User
from backend.routes.auth import auth_bp
from backend.routes.emotion import emotion_bp
from backend.utils.email_service import EmailService

import redis


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app():
    # --------------------------------------------------
    # Application setup
    # --------------------------------------------------
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(base_dir, "frontend")
    static_dir = os.path.join(template_dir, "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )

    # --------------------------------------------------
    # Environment and security configuration
    # --------------------------------------------------
    environment = os.environ.get("FLASK_ENV", "development").lower()
    is_production = (
        environment == "production"
        or bool(os.environ.get("RENDER"))
        or bool(os.environ.get("RAILWAY_ENVIRONMENT"))
    )

    secret_key = os.environ.get("SECRET_KEY")

    if not secret_key:
        if is_production:
            raise RuntimeError(
                "SECRET_KEY must be configured in production."
            )

        # Local development only. Sessions will reset after restart.
        secret_key = secrets.token_hex(32)
        logger.warning(
            "SECRET_KEY is not configured. Using a temporary "
            "development key."
        )

    app.config["SECRET_KEY"] = secret_key
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = is_production
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)

    # --------------------------------------------------
    # Database configuration
    # --------------------------------------------------
    database_url = (
        os.environ.get("DATABASE_URL")
        or os.environ.get("POSTGRES_URI")
    )

    if database_url:
        # Some platforms supply PostgreSQL URLs using postgres://.
        if database_url.startswith("postgres://"):
            database_url = database_url.replace(
                "postgres://",
                "postgresql://",
                1,
            )

        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        logger.info("Using the configured database URL.")
    elif is_production:
        raise RuntimeError(
            "DATABASE_URL must be configured in production."
        )
    else:
        # Local development only.
        sqlite_path = os.path.join(base_dir, "emotcare_local.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "sqlite:///" + sqlite_path.replace("\\", "/")
        )
        logger.info("Using local SQLite database.")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # --------------------------------------------------
    # Session configuration
    # --------------------------------------------------
    redis_url = os.environ.get("REDIS_URL")

    if redis_url:
        app.config["SESSION_TYPE"] = "redis"
        app.config["SESSION_REDIS"] = redis.from_url(redis_url)
        logger.info("Using Redis for session storage.")
    else:
        if is_production:
            logger.warning(
                "REDIS_URL is not configured. Filesystem sessions "
                "are being used; configure Redis for persistent, "
                "multi-instance production sessions."
            )

        session_dir = os.path.join(base_dir, "temp_sessions")
        os.makedirs(session_dir, exist_ok=True)

        app.config["SESSION_TYPE"] = "filesystem"
        app.config["SESSION_FILE_DIR"] = session_dir
        app.config["SESSION_FILE_THRESHOLD"] = 100
        logger.info("Using filesystem session storage.")

    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True

    # --------------------------------------------------
    # Email configuration
    # --------------------------------------------------
    app.config["MAIL_SERVER"] = os.environ.get(
        "MAIL_SERVER", "smtp.gmail.com"
    )
    app.config["MAIL_PORT"] = int(
        os.environ.get("MAIL_PORT", "587")
    )
    app.config["MAIL_USE_TLS"] = (
        os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    )
    app.config["MAIL_USE_SSL"] = (
        os.environ.get("MAIL_USE_SSL", "false").lower() == "true"
    )
    app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get(
        "MAIL_DEFAULT_SENDER",
        app.config["MAIL_USERNAME"],
    )

    # --------------------------------------------------
    # Initialize extensions
    # --------------------------------------------------
    db.init_app(app)
    Bcrypt(app)
    mail = Mail(app)
    CORS(app)
    Session(app)

    # Keep the email service available to code that needs it.
    email_service = EmailService(mail)
    app.extensions["email_service"] = email_service

    # --------------------------------------------------
    # Register blueprints
    # --------------------------------------------------
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(emotion_bp, url_prefix="/api")

    # --------------------------------------------------
    # Database initialization
    # --------------------------------------------------
    database_connected = False

    try:
        with app.app_context():
            db.create_all()
            database_connected = True
            logger.info("Database tables initialized successfully.")
    except Exception:
        logger.exception("Database initialization failed.")

        if is_production:
            # Fail startup rather than run a broken production app.
            raise

    app.config["DATABASE_CONNECTED"] = database_connected

    # --------------------------------------------------
    # Helper: load a verified, authenticated user
    # --------------------------------------------------
    def get_current_user():
        user_id = session.get("user_id")

        if user_id is None:
            return None

        try:
            user = db.session.get(User, user_id)

            if user and user.is_verified:
                return user

        except Exception:
            logger.exception("Unable to load the current user.")
            db.session.rollback()

        session.clear()
        return None

    # --------------------------------------------------
    # Routes
    # --------------------------------------------------
    @app.route("/")
    def index():
        user = get_current_user()

        if user:
            return redirect(url_for("dashboard"))

        return render_template("login.html")

    @app.route("/dashboard")
    def dashboard():
        user = get_current_user()

        if not user:
            return redirect(url_for("index"))

        return render_template("dashboard.html", user=user)

    @app.route("/analytics")
    def analytics():
        user = get_current_user()

        if not user:
            return redirect(url_for("index"))

        return render_template("analytics.html", user=user)

    @app.route("/profile")
    def profile():
        user = get_current_user()

        if not user:
            return redirect(url_for("index"))

        return render_template("profile.html", user=user)

    @app.route("/clear-startup-sessions")
    def clear_startup_sessions():
        # This clears only the current browser session.
        session.clear()
        return redirect(url_for("index"))

    # --------------------------------------------------
    # Error handlers
    # --------------------------------------------------
    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    return app


# ------------------------------------------------------
# Run application locally
# ------------------------------------------------------
if __name__ == "__main__":
    try:
        app = create_app()

        if app.config.get("DATABASE_CONNECTED"):
            logger.info("Application database connection initialized.")
        else:
            logger.warning(
                "Application started without a confirmed database "
                "connection. Some features may not work."
            )

        host = os.environ.get("HOST", "127.0.0.1")
        port = int(os.environ.get("PORT", "5000"))
        debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

        if (
            debug
            and (
                os.environ.get("FLASK_ENV", "development").lower()
                == "production"
                or os.environ.get("RENDER")
                or os.environ.get("RAILWAY_ENVIRONMENT")
            )
        ):
            raise RuntimeError(
                "Debug mode must not be enabled in production."
            )

        logger.info("Starting EmotiCare on %s:%s", host, port)
        app.run(host=host, port=port, debug=debug)

    except Exception:
        logger.exception("Failed to start EmotiCare.")
        raise
