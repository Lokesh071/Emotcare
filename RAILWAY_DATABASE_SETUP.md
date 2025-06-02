# 🗄️ Railway Database Setup Guide for EmotiCare

## 📋 Overview

Your EmotiCare application needs two databases:
1. **PostgreSQL** - Main database for user data, emotions, analytics
2. **Redis** - Session management and caching

## 🚀 Step-by-Step Database Setup

### **Step 1: Access Railway Dashboard**

1. Go to [railway.app](https://railway.app)
2. Sign in with your GitHub account
3. Select your **EmotiCare project**

You should see your project dashboard with your web service already deployed.

### **Step 2: Add PostgreSQL Database**

**Visual Guide:**
```
Railway Dashboard → Your Project → [+ New] Button
```

1. **Click the "+ New" button** (purple button in your project)
2. **Select "Database"** from the dropdown menu
3. **Choose "Add PostgreSQL"** from the database options
4. **Wait for provisioning** (1-2 minutes)

**What you'll see:**
- A new PostgreSQL service appears in your project
- Status changes from "Deploying" to "Active"
- Green checkmark indicates successful deployment

**✅ Railway automatically:**
- Creates a PostgreSQL 15+ instance
- Generates secure connection credentials
- Injects `DATABASE_URL` environment variable into your web service
- Sets up automatic backups

### **Step 3: Add Redis Database**

**Visual Guide:**
```
Railway Dashboard → Your Project → [+ New] Button (again)
```

1. **Click "+ New"** again (same purple button)
2. **Select "Database"** from the dropdown menu
3. **Choose "Add Redis"** from the database options
4. **Wait for provisioning** (1-2 minutes)

**What you'll see:**
- A new Redis service appears in your project
- Status changes from "Deploying" to "Active"
- Green checkmark indicates successful deployment

**✅ Railway automatically:**
- Creates a Redis 7+ instance
- Generates secure connection credentials
- Injects `REDIS_URL` environment variable into your web service
- Configures memory limits and persistence

### **Step 4: Configure Environment Variables**

Go to your **web service** → **"Variables"** tab and add:

```env
# Database Configuration
USE_POSTGRES=true
FLASK_ENV=production

# Application Security
SECRET_KEY=your-secret-key-here-make-it-long-and-random

# AI API Keys
GROQ_API_KEY=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

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=faceauth1@gmail.com
MAIL_PASSWORD=kvik axuf aeqy yhex
MAIL_DEFAULT_SENDER=faceauth1@gmail.com
```

**Note**: Railway automatically provides:
- ✅ `DATABASE_URL` (PostgreSQL connection string)
- ✅ `REDIS_URL` (Redis connection string)
- ✅ `PORT` (Application port)

## 🔍 Verify Database Setup

### **Check Database Connections**

1. **PostgreSQL**: Look for `DATABASE_URL` in your service variables
2. **Redis**: Look for `REDIS_URL` in your service variables
3. **Application Logs**: Should show database connection success

### **Expected Log Messages**

```
✅ PostgreSQL database connected successfully
✅ Redis session store configured
✅ Database tables created/updated
```

## 📊 Database Schema

Your EmotiCare application will create these tables:

### **Users Table**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_token VARCHAR(100),
    reset_token VARCHAR(100),
    reset_token_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Emotions Table**
```sql
CREATE TABLE emotions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    emotion VARCHAR(50) NOT NULL,
    confidence FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context TEXT,
    method VARCHAR(50)
);
```

### **Chat History Table**
```sql
CREATE TABLE chat_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    user_message TEXT NOT NULL,
    ai_response TEXT NOT NULL,
    emotion_context VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Database Configuration Details

### **PostgreSQL Configuration**
- **Version**: PostgreSQL 15+
- **Storage**: 1GB (Railway free tier)
- **Connections**: Up to 20 concurrent
- **Backup**: Automatic daily backups

### **Redis Configuration**
- **Version**: Redis 7+
- **Memory**: 25MB (Railway free tier)
- **Persistence**: RDB snapshots
- **Use Cases**: Session storage, caching

## 🌐 Connection Examples

### **PostgreSQL Connection (Automatic)**
```python
# Railway automatically injects DATABASE_URL
# Your app.py already handles this:

if os.getenv('USE_POSTGRES') == 'true':
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
```

### **Redis Connection (Automatic)**
```python
# Railway automatically injects REDIS_URL
# Your app.py already handles this:

redis_url = os.getenv('REDIS_URL')
if redis_url:
    app.config['SESSION_REDIS'] = redis.from_url(redis_url)
```

## 🔍 Troubleshooting

### **Common Issues**

#### **Database Connection Failed**
```
❌ Error: could not connect to server
```
**Solution**: 
- Check if PostgreSQL service is running in Railway
- Verify `DATABASE_URL` is injected
- Check Railway service logs

#### **Redis Connection Failed**
```
❌ Redis connection error
```
**Solution**:
- Check if Redis service is running in Railway
- Verify `REDIS_URL` is injected
- Check Redis service status

#### **Tables Not Created**
```
❌ relation "users" does not exist
```
**Solution**:
- Check application startup logs
- Verify database migrations ran
- Check PostgreSQL service logs

### **Verification Commands**

#### **Check Database Status**
Visit your app URL + `/test-groq` to see database status

#### **Check Environment Variables**
In Railway dashboard → Service → Variables tab:
- ✅ `DATABASE_URL` should be present
- ✅ `REDIS_URL` should be present
- ✅ `USE_POSTGRES=true` should be set

## 📈 Database Monitoring

### **Railway Dashboard**
- **Metrics**: CPU, Memory, Storage usage
- **Logs**: Real-time database logs
- **Backups**: Automatic backup status

### **Application Monitoring**
- **Connection Status**: Check app startup logs
- **Query Performance**: Monitor response times
- **Error Rates**: Watch for database errors

## 🎯 Expected Results

After successful setup:

1. **✅ User Registration**: New users saved to PostgreSQL
2. **✅ Login Sessions**: Managed by Redis
3. **✅ Emotion Data**: Stored in PostgreSQL
4. **✅ Chat History**: Persistent across sessions
5. **✅ Analytics**: Historical data available
6. **✅ Email Verification**: Token storage working

## 🔄 Database Maintenance

### **Automatic Features**
- ✅ **Backups**: Daily automatic backups
- ✅ **Updates**: Automatic security updates
- ✅ **Monitoring**: Built-in health checks
- ✅ **Scaling**: Automatic resource management

### **Manual Tasks**
- 🔧 **Environment Variables**: Update as needed
- 🔧 **Schema Changes**: Deploy via app updates
- 🔧 **Data Cleanup**: Implement in application logic

## 🎉 Success Indicators

Your databases are working correctly when:

1. **✅ Application Starts**: No database connection errors
2. **✅ User Registration**: New accounts can be created
3. **✅ Login Works**: Sessions persist across requests
4. **✅ Emotion Detection**: Data is saved and retrieved
5. **✅ Analytics**: Historical data displays correctly

---

## 🚀 Quick Setup Checklist

- [ ] Add PostgreSQL database in Railway
- [ ] Add Redis database in Railway
- [ ] Set `USE_POSTGRES=true` environment variable
- [ ] Set `GROQ_API_KEY` environment variable
- [ ] Set `SECRET_KEY` environment variable
- [ ] Set email configuration variables
- [ ] Verify `DATABASE_URL` is auto-injected
- [ ] Verify `REDIS_URL` is auto-injected
- [ ] Check application startup logs
- [ ] Test user registration and login
- [ ] Test emotion detection and storage

**Your EmotiCare application will be fully functional with persistent data storage!** 🎯
