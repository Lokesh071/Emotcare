# Security Audit Findings - Emotcare

This document summarizes critical security issues found in the codebase. Please address these immediately.

## 🔴 CRITICAL ISSUES (High Priority)

### 1. Hardcoded API Keys in `backend/utils/realtime_ai_chat.py`

**Location:** Lines 61, 78
**Severity:** 🔴 CRITICAL - Credentials exposed in source code

**Issues:**
- **Line 61:** Together.ai API key hardcoded: `tgp_v1_AUZnh62yhM0hkFRv4pmvBHikZHw3MfWJ_8eAF4dBiyA`
- **Line 78:** Groq API key hardcoded: `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`

**Action Required:**
```python
# ❌ CURRENT (Line 61):
self.together_api_key = "tgp_v1_AUZnh62yhM0hkFRv4pmvBHikZHw3MfWJ_8eAF4dBiyA"

# ✅ FIXED:
self.together_api_key = os.getenv('TOGETHER_API_KEY')
if not self.together_api_key:
    raise ValueError("TOGETHER_API_KEY environment variable is not set")

# ❌ CURRENT (Line 78):
if not groq_api_key:
    groq_api_key = "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"

# ✅ FIXED:
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set")
```

**Immediate Actions:**
1. **Revoke both keys immediately** from Together.ai and Groq dashboards
2. Generate new API keys
3. Set them as environment variables in production
4. Remove the hardcoded fallback keys from the code
5. Force-push to remove from git history or use BFG Repo-Cleaner

---

### 2. Authentication Bypass in `backend/routes/emotion.py` - `require_auth()`

**Location:** Lines 27-35
**Severity:** 🔴 CRITICAL - Authentication fails open

**Issue:**
```python
def require_auth():
    if 'user_id' not in session:
        return False
    try:
        user = db.session.get(User, session['user_id'])
        return user and user.is_verified
    except:
        return True  # ❌ CRITICAL BUG: Returns True when lookup fails!
```

**Why it's dangerous:**
- When database lookup fails, the function returns `True`, authenticating the user
- This allows ANY failed lookup to bypass authentication
- Callers expect `False` on auth failure, `True` on success

**Fix:**
```python
def require_auth():
    """Verify user is authenticated and verified in database"""
    if 'user_id' not in session:
        return False
    
    try:
        user = db.session.get(User, session['user_id'])
        return user is not None and user.is_verified
    except Exception as e:
        print(f"Error during auth verification: {e}")
        return False  # ✅ Fail securely on error
```

---

### 3. Unauthenticated Endpoint Leaking Exception Details

**Location:** `backend/routes/emotion.py` - `/visual-emotion-detection` (Lines 664-749)
**Severity:** 🔴 CRITICAL - Information disclosure + no auth check

**Issues:**
1. **No login check** - endpoint is publicly accessible
2. **Returns raw exception text** to client (line 748): `'error': str(e)`
3. Exposes internal error details that aid attackers

**Current Code (Lines 743-749):**
```python
except Exception as e:
    print(f"Visual emotion detection error: {e}")
    return jsonify({
        'success': False,
        'message': 'Error processing visual emotion detection',
        'error': str(e)  # ❌ Leaks exception details
    }), 500
```

**Fix:**
```python
@emotion_bp.route('/visual-emotion-detection', methods=['POST'])
def visual_emotion_detection():
    """Advanced visual emotion detection using Groq's Llama Vision AI"""
    
    # ✅ ADD AUTH CHECK at the start:
    if not require_auth():
        return jsonify({
            'success': False,
            'message': 'Please log in first'
        }), 401
    
    try:
        # ... existing code ...
    except Exception as e:
        print(f"Visual emotion detection error: {e}")
        # ✅ Don't expose exception details to client
        return jsonify({
            'success': False,
            'message': 'Error processing visual emotion detection'
        }), 500
```

---

## 🟠 HIGH PRIORITY ISSUES

### 4. Default `SECRET_KEY` in `backend/config.py`

**Location:** Line 4
**Severity:** 🟠 HIGH - Session forgery vulnerability

**Issue:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-this')
```

**Problem:**
- If `SECRET_KEY` env var is not set, the default fallback is used
- Default `'replace-this'` is weak and publicly known
- Attackers can forge session cookies

**Fix:**
```python
import os
from pathlib import Path

class Config:
    # ✅ Require environment variable; don't have a default
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        raise ValueError(
            "SECRET_KEY environment variable must be set. "
            "Generate a strong key with: python -c 'import secrets; print(secrets.token_hex(32))'"
        )
    SECRET_KEY = secret_key
    
    # ... rest of config ...
```

---

### 5. User ID Fallback to 1 When Logged Out

**Location:** Multiple routes in `backend/routes/emotion.py`
**Severity:** 🟠 HIGH - Data leakage to default user

**Lines affected:**
- Line 78: `user_id=session.get('user_id', 1)`
- Line 118: `user_id=session.get('user_id', 1)`
- Line 631: `user_id=session.get('user_id', 1)`

**Issue:**
- When users aren't logged in, records default to `user_id=1`
- All unauthenticated users' data gets mixed under user 1
- User 1 can see emotion records from unlogged users

**Fix:**
After the `require_auth()` check, always use `session['user_id']` directly:
```python
# ❌ Don't do this:
user_id=session.get('user_id', 1)

# ✅ After require_auth() passes, safely access:
user_id=session['user_id']  # Guaranteed to exist if auth passed
```

---

### 6. API Key Logging (Lines 66, 85)

**Location:** `backend/utils/realtime_ai_chat.py` - Lines 66, 85
**Severity:** 🟠 HIGH - Sensitive data in logs

**Issue:**
```python
# Line 66:
print(f"🔍 GROQ_API_KEY from environment: {groq_api_key[:20] + '...' if groq_api_key else 'NOT_SET'}")

# Line 85:
print(f"🔑 Using API key: {groq_api_key[:20]}...")
```

**Problem:**
- Even truncated API keys in logs can aid attackers (prefix guessing)
- Log aggregators (CloudWatch, DataDog, Splunk) expose these
- Violates secrets management best practices

**Fix:**
```python
# ✅ Only log redacted info:
print(f"🔍 GROQ_API_KEY from environment: {'SET' if groq_api_key else 'NOT_SET'}")
print(f"🔑 Using API key: [REDACTED]")
```

---

## 🟡 MEDIUM PRIORITY ISSUES

### 7. Secrets in Git History

**Severity:** 🟡 MEDIUM - Old expired secrets (currently harmless)

**Details:**
- Old Neon and Gmail secrets in commit `dbe2512` (now expired)
- They're harmless since expired, but cleaning up is good practice

**Action (Optional):**
Use `git-filter-repo` or `BFG Repo-Cleaner` to remove old secrets from history:
```bash
# Install BFG
brew install bfg

# Remove patterns
bfg --replace-text patterns.txt .

# Force push
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force
```

---

## 🔧 DEPLOYMENT CHECKLIST

- [ ] Revoke Together.ai API key (`tgp_v1_...`)
- [ ] Revoke Groq API key (`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`)
- [ ] Fix `require_auth()` to return `False` on exception
- [ ] Add auth check to `/visual-emotion-detection`
- [ ] Remove `str(e)` from error responses
- [ ] Fix `SECRET_KEY` default to raise error
- [ ] Replace `session.get('user_id', 1)` with `session['user_id']` after auth
- [ ] Remove API key prefixes from log statements
- [ ] Generate new API keys and set env vars in production
- [ ] Enable GitHub secret scanning in Settings → Code security
- [ ] Test each endpoint with invalid/missing auth
- [ ] Review `backend/routes/auth.py` separately
- [ ] Review Dockerfile and deployment configs for hardcoded secrets

---

## 📚 ADDITIONAL RECOMMENDATIONS

### GitHub Security Settings
In **Settings → Code security:**
1. ✅ Enable Secret scanning for the repository
2. ✅ Enable Push protection (blocks commits with secrets)
3. ✅ Review any existing secret detection alerts

### Env Var Management
- Use `.env` file locally (add to `.gitignore`)
- Use managed secrets in production (Railway, Heroku, GitHub Secrets, AWS Secrets Manager)
- Never commit `.env` file

### Secret Rotation
- Rotate all API keys regularly (monthly)
- Use key expiration where provider supports it
- Audit key usage in provider dashboards

---

## Questions?
Review the linked code sections and reach out if clarification is needed on any fix.
