# utils/email_service.py
from flask_mail import Message
from flask import url_for, current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

class EmailService:
    def __init__(self, mail=None):
        self.mail = mail
        self.logger = logging.getLogger(__name__)
    
    def send_verification_email(self, user):
        """Send email verification to user"""
        try:
            subject = "Welcome to EmotiCare - Verify Your Email 🌟"
            verification_url = url_for('auth.verify_email', token=user.verification_token, _external=True)
            
            html_content = self._get_verification_email_template(user, verification_url)
            
            return self._send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            self.logger.error(f"Error sending verification email: {e}")
            return False
    
    def send_password_reset_email(self, user):
        """Send password reset email to user"""
        try:
            subject = "EmotiCare - Password Reset Request 🔐"
            reset_url = url_for('auth.reset_password', token=user.reset_token, _external=True)
            
            html_content = self._get_password_reset_email_template(user, reset_url)
            
            return self._send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            self.logger.error(f"Error sending password reset email: {e}")
            return False
    
    def send_welcome_email(self, user):
        """Send welcome email after successful verification"""
        try:
            subject = "Welcome to EmotiCare! Let's Begin Your Journey 🚀"
            
            html_content = self._get_welcome_email_template(user)
            
            return self._send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            self.logger.error(f"Error sending welcome email: {e}")
            return False
    
    def send_emotion_summary_email(self, user, emotion_data):
        """Send weekly emotion summary to user"""
        try:
            subject = "Your Weekly Emotion Summary 📊"
            
            html_content = self._get_emotion_summary_email_template(user, emotion_data)
            
            return self._send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content
            )
            
        except Exception as e:
            self.logger.error(f"Error sending emotion summary email: {e}")
            return False
    
    def send_support_email(self, user, subject, message):
        """Send support email from user"""
        try:
            support_subject = f"EmotiCare Support: {subject}"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Support Request from {user.username}</h2>
                <p><strong>User Email:</strong> {user.email}</p>
                <p><strong>User ID:</strong> {user.id}</p>
                <p><strong>Subject:</strong> {subject}</p>
                <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 20px 0;">
                    <h3>Message:</h3>
                    <p>{message}</p>
                </div>
                <p><em>Sent from EmotiCare Support System</em></p>
            </div>
            """
            
            return self._send_email(
                to_email=current_app.config.get('SUPPORT_EMAIL', 'support@emoticare.com'),
                subject=support_subject,
                html_content=html_content,
                reply_to=user.email
            )
            
        except Exception as e:
            self.logger.error(f"Error sending support email: {e}")
            return False
    
    def _send_email(self, to_email, subject, html_content, reply_to=None):
        """Send email using Flask-Mail or SMTP"""
        try:
            if self.mail:
                # Use Flask-Mail
                msg = Message(
                    subject=subject,
                    recipients=[to_email],
                    html=html_content
                )
                if reply_to:
                    msg.reply_to = reply_to
                
                self.mail.send(msg)
                return True
            else:
                # Use direct SMTP
                return self._send_smtp_email(to_email, subject, html_content, reply_to)
                
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False
    
    def _send_smtp_email(self, to_email, subject, html_content, reply_to=None):
        """Send email using direct SMTP"""
        try:
            smtp_server = current_app.config.get('MAIL_SERVER', 'smtp.gmail.com')
            smtp_port = current_app.config.get('MAIL_PORT', 587)
            smtp_username = current_app.config.get('MAIL_USERNAME')
            smtp_password = current_app.config.get('MAIL_PASSWORD')
            
            if not smtp_username or not smtp_password:
                self.logger.error("SMTP credentials not configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = smtp_username
            msg['To'] = to_email
            if reply_to:
                msg['Reply-To'] = reply_to
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending SMTP email: {e}")
            return False
    
    def _get_verification_email_template(self, user, verification_url):
        """Get HTML template for verification email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to EmotiCare</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Comic Sans MS', cursive, Arial, sans-serif;">
            <div style="background: linear-gradient(45deg, #ffecd2 0%, #fcb69f 100%); padding: 20px; min-height: 100vh;">
                <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; border: 4px solid #ff6b6b; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <div style="background: linear-gradient(45deg, #ff6b6b 0%, #4ecdc4 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                            Welcome to EmotiCare! 😊
                        </h1>
                        <p style="color: white; margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                            Your emotional wellness journey starts here
                        </p>
                    </div>
                    
                    <!-- Content -->
                    <div style="padding: 40px 30px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <div style="font-size: 4rem; margin-bottom: 20px;">🌟</div>
                            <h2 style="color: #ff6b6b; margin: 0 0 15px 0; font-size: 1.8rem;">
                                Hi {user.username}!
                            </h2>
                            <p style="color: #666; font-size: 1.1rem; line-height: 1.6; margin: 0;">
                                We're thrilled to have you join our community of emotional wellness! 
                                Get ready to discover, understand, and improve your emotional well-being with AI-powered insights.
                            </p>
                        </div>
                        
                        <!-- Features -->
                        <div style="background: linear-gradient(45deg, #a8e6cf 0%, #dcedc1 100%); padding: 25px; border-radius: 15px; margin: 30px 0; border: 3px solid #fff;">
                            <h3 style="color: #2d5a27; margin: 0 0 20px 0; text-align: center; font-size: 1.3rem;">
                                🎯 What you can do with EmotiCare:
                            </h3>
                            <ul style="color: #2d5a27; margin: 0; padding: 0; list-style: none;">
                                <li style="margin: 12px 0; padding-left: 30px; position: relative;">
                                    <span style="position: absolute; left: 0; top: 0;">🎭</span>
                                    Real-time emotion detection through facial recognition
                                </li>
                                <li style="margin: 12px 0; padding-left: 30px; position: relative;">
                                    <span style="position: absolute; left: 0; top: 0;">💬</span>
                                    Personalized conversations based on your emotions
                                </li>
                                <li style="margin: 12px 0; padding-left: 30px; position: relative;">
                                    <span style="position: absolute; left: 0; top: 0;">💡</span>
                                    Helpful suggestions for managing different emotional states
                                </li>
                                <li style="margin: 12px 0; padding-left: 30px; position: relative;">
                                    <span style="position: absolute; left: 0; top: 0;">📊</span>
                                    Track your emotional journey over time
                                </li>
                                <li style="margin: 12px 0; padding-left: 30px; position: relative;">
                                    <span style="position: absolute; left: 0; top: 0;">🌈</span>
                                    Build better emotional awareness and wellness habits
                                </li>
                            </ul>
                        </div>
                        
                        <!-- Verification Button -->
                        <div style="text-align: center; margin: 40px 0;">
                            <p style="color: #666; font-size: 1.1rem; margin-bottom: 25px;">
                                To get started with your emotional wellness journey, please verify your email address:
                            </p>
                            <a href="{verification_url}" style="display: inline-block; background: linear-gradient(45deg, #ff6b6b 0%, #4ecdc4 100%); color: white; padding: 18px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 1.2rem; border: 3px solid #fff; box-shadow: 0 8px 25px rgba(0,0,0,0.2); transition: transform 0.3s ease;">
                                ✨ Verify My Email ✨
                            </a>
                        </div>
                        
                        <!-- Tips -->
                        <div style="background: linear-gradient(45deg, #ffd3a5 0%, #fd9853 100%); padding: 25px; border-radius: 15px; margin: 30px 0; border: 3px solid #fff;">
                            <h3 style="color: white; margin: 0 0 15px 0; text-align: center;">
                                💫 Quick Tips for Better Emotional Wellness:
                            </h3>
                            <ul style="color: white; margin: 0; padding: 0; list-style: none; font-size: 0.95rem;">
                                <li style="margin: 8px 0;">🌅 Start each day with a moment of mindfulness</li>
                                <li style="margin: 8px 0;">📝 Keep a daily emotion journal</li>
                                <li style="margin: 8px 0;">🤗 Practice self-compassion and kindness</li>
                                <li style="margin: 8px 0;">🌱 Remember that emotional growth is a journey</li>
                            </ul>
                        </div>
                        
                        <!-- Support -->
                        <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 2px solid #f0f0f0;">
                            <p style="color: #999; font-size: 0.9rem; margin: 0 0 10px 0;">
                                If you didn't create an account with EmotiCare, please ignore this email.
                            </p>
                            <p style="color: #ff6b6b; font-weight: bold; margin: 0; font-size: 1.1rem;">
                                💖 The EmotiCare Team By Lokesh071💖
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_password_reset_email_template(self, user, reset_url):
        """Get HTML template for password reset email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your EmotiCare Password</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Comic Sans MS', cursive, Arial, sans-serif;">
            <div style="background: linear-gradient(45deg, #ffecd2 0%, #fcb69f 100%); padding: 20px; min-height: 100vh;">
                <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; border: 4px solid #ff6b6b; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <div style="background: linear-gradient(45deg, #fd79a8 0%, #e84393 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 2.2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                            🔐 Password Reset Request
                        </h1>
                    </div>
                    
                    <!-- Content -->
                    <div style="padding: 40px 30px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <div style="font-size: 3rem; margin-bottom: 20px;">🔑</div>
                            <h2 style="color: #ff6b6b; margin: 0 0 15px 0; font-size: 1.6rem;">
                                Hi {user.username}!
                            </h2>
                            <p style="color: #666; font-size: 1.1rem; line-height: 1.6; margin: 0;">
                                We received a request to reset your EmotiCare password. 
                                Don't worry, it happens to the best of us! 😊
                            </p>
                        </div>
                        
                        <!-- Reset Button -->
                        <div style="text-align: center; margin: 40px 0;">
                            <p style="color: #666; font-size: 1rem; margin-bottom: 25px;">
                                Click the button below to create a new password:
                            </p>
                            <a href="{reset_url}" style="display: inline-block; background: linear-gradient(45d

, #fd79a8 0%, #e84393 100%); color: white; padding: 18px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 1.2rem; border: 3px solid #fff; box-shadow: 0 8px 25px rgba(0,0,0,0.2);">
                                🔐 Reset My Password
                            </a>
                        </div>
                        
                        <!-- Security Notice -->
                        <div style="background: linear-gradient(45deg, #74b9ff 0%, #0984e3 100%); padding: 25px; border-radius: 15px; margin: 30px 0; border: 3px solid #fff;">
                            <h3 style="color: white; margin: 0 0 15px 0; text-align: center;">
                                🛡️ Security Notice:
                            </h3>
                            <ul style="color: white; margin: 0; padding: 0; list-style: none; font-size: 0.95rem;">
                                <li style="margin: 8px 0;">⏰ This link will expire in 1 hour for security</li>
                                <li style="margin: 8px 0;">🔒 Only you should have access to this email</li>
                                <li style="margin: 8px 0;">❌ If you didn't request this, please ignore this email</li>
                                <li style="margin: 8px 0;">📧 Contact support if you have concerns</li>
                            </ul>
                        </div>
                        
                        <!-- Alternative -->
                        <div style="text-align: center; margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 10px;">
                            <p style="color: #666; font-size: 0.9rem; margin: 0 0 10px 0;">
                                If the button doesn't work, copy and paste this link into your browser:
                            </p>
                            <p style="word-break: break-all; color: #007bff; font-size: 0.8rem; margin: 0;">
                                {reset_url}
                            </p>
                        </div>
                        
                        <!-- Support -->
                        <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 2px solid #f0f0f0;">
                            <p style="color: #999; font-size: 0.9rem; margin: 0 0 10px 0;">
                                If you didn't request a password reset, please ignore this email or contact our support team.
                            </p>
                            <p style="color: #ff6b6b; font-weight: bold; margin: 0; font-size: 1.1rem;">
                                💖 The EmotiCare Team BY Lokesh071💖
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_welcome_email_template(self, user):
        """Get HTML template for welcome email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to EmotiCare!</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Comic Sans MS', cursive, Arial, sans-serif;">
            <div style="background: linear-gradient(45deg, #ffecd2 0%, #fcb69f 100%); padding: 20px; min-height: 100vh;">
                <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; border: 4px solid #4ecdc4; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <div style="background: linear-gradient(45deg, #4ecdc4 0%, #44a08d 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 2.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                            🎉 Welcome to EmotiCare! 🎉
                        </h1>
                        <p style="color: white; margin: 10px 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                            Your emotional wellness journey begins now!
                        </p>
                    </div>
                    
                    <!-- Content -->
                    <div style="padding: 40px 30px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <div style="font-size: 4rem; margin-bottom: 20px;">🚀</div>
                            <h2 style="color: #4ecdc4; margin: 0 0 15px 0; font-size: 1.8rem;">
                                Congratulations {user.username}!
                            </h2>
                            <p style="color: #666; font-size: 1.1rem; line-height: 1.6; margin: 0;">
                                Your email has been verified and your EmotiCare account is now active! 
                                You're all set to begin exploring your emotional landscape with our AI-powered tools.
                            </p>
                        </div>
                        
                        <!-- Next Steps -->
                        <div style="background: linear-gradient(45deg, #a8e6cf 0%, #dcedc1 100%); padding: 25px; border-radius: 15px; margin: 30px 0; border: 3px solid #fff;">
                            <h3 style="color: #2d5a27; margin: 0 0 20px 0; text-align: center; font-size: 1.3rem;">
                                🎯 Next Steps:
                            </h3>
                            <ul style="color: #2d5a27; margin: 0; padding: 0; list-style: none;">
                                <li style="margin: 12px 0; padding-left: 30px; position: relative;">
                                    <span style="position: absolute; left: 0; top: 0;">1️⃣</span>
                                    Complete your profile setup
                                </li>
                                <li style="margin: 12px 0; padding-left: 30px; position: relative;">
                                    <span style="position: absolute; left: 0; top: 0;">2️⃣</span>
                                    Try your first emotion detection session
                                </li>
                                <li style="margin: 12px 0; padding-left: 30px; position: relative;">
                                    <span style="position: absolute; left: 0; top: 0;">3️⃣</span>
                                    Explore personalized wellness suggestions
                                </li>
                                <li style="margin: 12px 0; padding-left: 30px; position: relative;">
                                    <span style="position: absolute; left: 0; top: 0;">4️⃣</span>
                                    Start building healthy emotional habits
                                </li>
                            </ul>
                        </div>
                        
                        <!-- CTA Button -->
                        <div style="text-align: center; margin: 40px 0;">
                            <a href="{url_for('index', _external=True)}" style="display: inline-block; background: linear-gradient(45deg, #4ecdc4 0%, #44a08d 100%); color: white; padding: 18px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 1.2rem; border: 3px solid #fff; box-shadow: 0 8px 25px rgba(0,0,0,0.2);">
                                🌟 Start My Journey 🌟
                            </a>
                        </div>
                        
                        <!-- Tips -->
                        <div style="background: linear-gradient(45deg, #ffd3a5 0%, #fd9853 100%); padding: 25px; border-radius: 15px; margin: 30px 0; border: 3px solid #fff;">
                            <h3 style="color: white; margin: 0 0 15px 0; text-align: center;">
                                💡 Pro Tips for Success:
                            </h3>
                            <ul style="color: white; margin: 0; padding: 0; list-style: none; font-size: 0.95rem;">
                                <li style="margin: 8px 0;">📱 Check in with your emotions daily</li>
                                <li style="margin: 8px 0;">🎯 Set small, achievable wellness goals</li>
                                <li style="margin: 8px 0;">📊 Review your emotion patterns weekly</li>
                                <li style="margin: 8px 0;">🤝 Don't hesitate to reach out for support</li>
                            </ul>
                        </div>
                        
                        <!-- Support -->
                        <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 2px solid #f0f0f0;">
                            <p style="color: #666; font-size: 1rem; margin: 0 0 15px 0;">
                                Questions? We're here to help! Feel free to contact our support team anytime.
                            </p>
                            <p style="color: #4ecdc4; font-weight: bold; margin: 0; font-size: 1.1rem;">
                                💖 Welcome to the EmotiCare family! BY Lokesh071💖
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_emotion_summary_email_template(self, user, emotion_data):
        """Get HTML template for emotion summary email"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Weekly Emotion Summary</title>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Comic Sans MS', cursive, Arial, sans-serif;">
            <div style="background: linear-gradient(45deg, #ffecd2 0%, #fcb69f 100%); padding: 20px; min-height: 100vh;">
                <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; border: 4px solid #ff6b6b; overflow: hidden; box-shadow: 0 20px 40px rgba(0,0,0,0.1);">
                    
                    <!-- Header -->
                    <div style="background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                        <h1 style="color: white; margin: 0; font-size: 2.2rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                            📊 Your Weekly Summary
                        </h1>
                        <p style="color: white; margin: 10px 0 0 0; font-size: 1.1rem; opacity: 0.9;">
                            Insights into your emotional journey
                        </p>
                    </div>
                    
                    <!-- Content -->
                    <div style="padding: 40px 30px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h2 style="color: #667eea; margin: 0 0 15px 0; font-size: 1.6rem;">
                                Hi {user.username}! 👋
                            </h2>
                            <p style="color: #666; font-size: 1rem; line-height: 1.6; margin: 0;">
                                Here's a summary of your emotional patterns from the past week. 
                                Remember, awareness is the first step toward growth! 🌱
                            </p>
                        </div>
                        
                        <!-- Emotion Stats -->
                        <div style="background: linear-gradient(45deg, #a8e6cf 0%, #dcedc1 100%); padding: 25px; border-radius: 15px; margin: 30px 0; border: 3px solid #fff;">
                            <h3 style="color: #2d5a27; margin: 0 0 20px 0; text-align: center;">
                                🎭 Your Emotion Patterns:
                            </h3>
                            <div style="color: #2d5a27;">
                                {self._format_emotion_stats(emotion_data)}
                            </div>
                        </div>
                        
                        <!-- Insights -->
                        <div style="background: linear-gradient(45deg, #ffd3a5 0%, #fd9853 100%); padding: 25px; border-radius: 15px; margin: 30px 0; border: 3px solid #fff;">
                            <h3 style="color: white; margin: 0 0 15px 0; text-align: center;">
                                💡 Weekly Insights:
                            </h3>
                            <div style="color: white; font-size: 0.95rem;">
                                {self._generate_insights(emotion_data)}
                            </div>
                        </div>
                        
                        <!-- CTA -->
                        <div style="text-align: center; margin: 40px 0;">
                            <a href="{url_for('index', _external=True)}" style="display: inline-block; background: linear-gradient(45deg, #667eea 0%, #764ba2 100%); color: white; padding: 18px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 1.1rem; border: 3px solid #fff; box-shadow: 0 8px 25px rgba(0,0,0,0.2);">
                                📈 View Detailed Analytics
                            </a>
                        </div>
                        
                        <!-- Footer -->
                        <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 2px solid #f0f0f0;">
                            <p style="color: #666; font-size: 0.9rem; margin: 0 0 10px 0;">
                                Keep up the great work on your emotional wellness journey! 
                            </p>
                            <p style="color: #667eea; font-weight: bold; margin: 0; font-size: 1rem;">
                                💜 The EmotiCare Team BY Lokesh071💜
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _format_emotion_stats(self, emotion_data):
        """Format emotion statistics for email"""
        if not emotion_data:
            return "<p>No emotion data available for this period.</p>"
        
        stats_html = ""
        for emotion, count in emotion_data.get('frequency', {}).items():
            percentage = emotion_data.get('percentages', {}).get(emotion, 0)
            emoji = self._get_emotion_emoji(emotion)
            stats_html += f"""
            <div style="margin: 10px 0; padding: 10px; background: rgba(255,255,255,0.3); border-radius: 8px;">
                <span style="font-size: 1.2rem;">{emoji}</span>
                <strong>{emotion.title()}</strong>: {count} times ({percentage}%)
            </div>
            """
        
        return stats_html
    
    def _generate_insights(self, emotion_data):
        """Generate insights based on emotion data"""
        insights = []
        
        if emotion_data.get('most_frequent'):
            most_frequent = emotion_data['most_frequent']
            insights.append(f"📊 Your most frequent emotion this week was {most_frequent}")
        
        if emotion_data.get('trend') == 'improving':
            insights.append("📈 Your emotional wellness is trending positively!")
        elif emotion_data.get('trend') == 'declining':
            insights.append("📉 Consider focusing on self-care activities this week")
        
        if emotion_data.get('diversity_score', 0) > 0.7:
            insights.append("🌈 Great emotional diversity - you're experiencing a healthy range of emotions")
        
        if not insights:
            insights.append("🌟 Keep tracking your emotions to unlock personalized insights")
        
        return "<br>".join(f"• {insight}" for insight in insights)
    
    def _get_emotion_emoji(self, emotion):
        """Get emoji for emotion"""
        emojis = {
            'happy': '😊',
            'sad': '😢',
            'angry': '😠',
            'stressed': '😰',
            'anxious': '😟',
            'neutral': '😐',
            'surprised': '😲'
        }
        return emojis.get(emotion.lower(), '🤔')
