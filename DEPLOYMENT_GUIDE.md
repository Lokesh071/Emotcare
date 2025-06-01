# EmotiCare Deployment Guide

## 🚀 Deploy to Render

### Prerequisites
1. GitHub account
2. Render account (free tier available)
3. Your EmotiCare code pushed to GitHub

### Step 1: Push to GitHub
```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit - EmotiCare application"

# Add your GitHub repository as remote
git remote add origin https://github.com/Lokesh071/Emotcare.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy on Render

1. **Go to Render Dashboard**
   - Visit [render.com](https://render.com)
   - Sign up/Login with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `Lokesh071/Emotcare`
   - Select the repository

3. **Configure Deployment**
   - **Name**: `emotcare`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Plan**: Free (or paid for better performance)

4. **Set Environment Variables**
   Add these environment variables in Render dashboard:
   ```
   SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   USE_POSTGRES=true
   GROQ_API_KEY=your-groq-api-key
   OPENAI_API_KEY=your-openai-api-key
   MAIL_USERNAME=faceauth1@gmail.com
   MAIL_PASSWORD=kvik axuf aeqy yhex
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_DEFAULT_SENDER=faceauth1@gmail.com
   ```

5. **Create Database**
   - In Render dashboard, create a new PostgreSQL database
   - Name it `emotcare-db`
   - Copy the database URL and add it as `DATABASE_URL` environment variable

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete (5-10 minutes)

### Step 3: Access Your Application
- Your app will be available at: `https://emotcare.onrender.com`
- Or the URL provided by Render

### 🔧 Configuration Files Created

1. **render.yaml** - Render deployment configuration
2. **Procfile** - Process file for deployment
3. **requirements.txt** - Updated with gunicorn
4. **.gitignore** - Updated for deployment
5. **app.py** - Updated for production database handling

### 🌟 Features Ready for Production

- ✅ **Emotion Detection**: ML models included
- ✅ **AI Chat**: Groq and OpenAI integration
- ✅ **User Authentication**: Login/Register system
- ✅ **Database**: PostgreSQL for production
- ✅ **Email Service**: Password reset functionality
- ✅ **Responsive Design**: Works on all devices
- ✅ **Session Management**: Secure user sessions

### 🔒 Security Notes

- Environment variables are used for sensitive data
- Database credentials are managed by Render
- Session keys are auto-generated
- HTTPS is enabled by default on Render

### 🐛 Troubleshooting

1. **Build Fails**: Check requirements.txt for compatibility
2. **Database Issues**: Ensure DATABASE_URL is set correctly
3. **AI Not Working**: Verify API keys are set
4. **Email Issues**: Check MAIL_* environment variables

### 📱 Post-Deployment

1. Test all features:
   - User registration/login
   - Emotion detection
   - AI chat functionality
   - Email verification

2. Monitor logs in Render dashboard
3. Set up custom domain (optional)

### 🔄 Updates

To update your deployed app:
```bash
git add .
git commit -m "Update description"
git push origin main
```

Render will automatically redeploy when you push to GitHub.

---

**Your EmotiCare app is now ready for the world! 🌍✨**
