from flask import Blueprint, request, jsonify, session, render_template, url_for, current_app
from backend.models import User, db
from backend.utils.email_service import EmailService
from flask_bcrypt import Bcrypt
import secrets
import re
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def get_email_service():
    """Get EmailService instance with proper mail configuration"""
    try:
        from flask_mail import Mail
        mail = current_app.extensions.get('mail')
        if mail:
            return EmailService(mail)
        else:
            # Fallback to SMTP method
            return EmailService()
    except:
        # Fallback to SMTP method
        return EmailService()

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')

        if not username or len(username) < 3:
            return jsonify({
                'success': False,
                'message': 'Username must be at least 3 characters long'
            }), 400

        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Please enter a valid email address'
            }), 400

        is_valid, password_message = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': password_message
            }), 400

        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 400

        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'message': 'Email already registered'
            }), 400

        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        verification_token = secrets.token_urlsafe(32)

        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            verification_token=verification_token
        )

        db.session.add(user)
        db.session.commit()

        email_service = get_email_service()
        email_sent = email_service.send_verification_email(user)

        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Registration successful! Please check your email to verify your account.',
                'user_id': user.id
            }), 201
        else:
            return jsonify({
                'success': True,
                'message': 'Registration successful! However, there was an issue sending the verification email. Please contact support.',
                'user_id': user.id
            }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during registration. Please try again.'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)

        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            if not user.is_verified:
                return jsonify({
                    'success': False,
                    'message': 'Please verify your email address before logging in',
                    'needs_verification': True,
                    'user_id': user.id
                }), 401

            user.last_login = datetime.utcnow()
            db.session.commit()

            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email

            if remember_me:
                session.permanent = True

            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'created_at': user.created_at.isoformat(),
                    'last_login': user.last_login.isoformat() if user.last_login else None
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401

    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during login. Please try again.'
        }), 500

@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    try:
        user = User.query.filter_by(verification_token=token).first()

        if user:
            user.is_verified = True
            user.verification_token = None
            user.email_verified_at = datetime.utcnow()
            db.session.commit()

            return render_template('verification_success.html',
                                 username=user.username,
                                 email=user.email)
        else:
            return render_template('verification_failed.html'), 404

    except Exception as e:
        print(f"Email verification error: {e}")
        return render_template('verification_failed.html'), 500

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()

        user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({
                'success': False,
                'message': 'No account found with this email address'
            }), 404

        if user.is_verified:
            return jsonify({
                'success': False,
                'message': 'This account is already verified'
            }), 400

        user.verification_token = secrets.token_urlsafe(32)
        db.session.commit()

        email_service = get_email_service()
        email_sent = email_service.send_verification_email(user)

        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Verification email sent successfully!'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send verification email. Please try again later.'
            }), 500

    except Exception as e:
        print(f"Resend verification error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()

        user = User.query.filter_by(email=email).first()

        if user:
            temp_password = generate_temp_password()

            user.password_hash = bcrypt.generate_password_hash(temp_password).decode('utf-8')
            user.reset_token = None
            user.reset_token_expires = None
            db.session.commit()

            email_service = get_email_service()
            email_sent = email_service.send_password_reset_email(user, temp_password)

            if email_sent:
                return jsonify({
                    'success': True,
                    'message': 'Temporary password sent to your email! Please check your inbox and update your password after logging in.'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to send temporary password email. Please try again later.'
                }), 500
        else:
            return jsonify({
                'success': True,
                'message': 'If an account with this email exists, a temporary password will be sent.'
            }), 200

    except Exception as e:
        print(f"Forgot password error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

def generate_temp_password(length=12):
    import string
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        user = User.query.filter_by(reset_token=token).first()

        if not user or not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            return render_template('reset_password_failed.html'), 400

        if request.method == 'GET':
            return render_template('reset_password.html', token=token)

        elif request.method == 'POST':
            data = request.get_json()
            new_password = data.get('password', '')

            is_valid, password_message = validate_password(new_password)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'message': password_message
                }), 400

            user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.reset_token = None
            user.reset_token_expires = None
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Password reset successful! You can now log in with your new password.'
            }), 200

    except Exception as e:
        print(f"Reset password error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
    except Exception as e:
        print(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred during logout'
        }), 500

@auth_bp.route('/check-auth')
def check_auth():
    try:
        if 'user_id' in session:
            user = db.session.get(User, session['user_id'])
            if user and user.is_verified:
                return jsonify({
                    'success': True,
                    'authenticated': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email
                    }
                }), 200

        return jsonify({
            'success': False,
            'authenticated': False,
            'message': 'Not authenticated'
        }), 401

    except Exception as e:
        print(f"Check auth error: {e}")
        return jsonify({
            'success': False,
            'authenticated': False,
            'message': 'Error checking authentication'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401

        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')

        user = User.query.get(session['user_id'])

        if not bcrypt.check_password_hash(user.password_hash, current_password):
            return jsonify({
                'success': False,
                'message': 'Current password is incorrect'
            }), 400

        is_valid, password_message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': password_message
            }), 400

        user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Password changed successfully!'
        }), 200

    except Exception as e:
        print(f"Change password error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500

@auth_bp.route('/update-profile', methods=['POST'])
def update_profile():
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'message': 'Please log in first'
            }), 401

        data = request.get_json()
        username = data.get('username', '').strip()

        user = db.session.get(User, session['user_id'])

        if username and len(username) >= 3:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({
                    'success': False,
                    'message': 'Username is already taken'
                }), 400

            user.username = username
            session['username'] = username

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Profile updated successfully!',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }), 200

    except Exception as e:
        print(f"Update profile error: {e}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again.'
        }), 500
