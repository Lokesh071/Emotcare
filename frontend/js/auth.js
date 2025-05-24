// auth.js
class AuthManager {
    constructor() {
        this.loginForm = document.getElementById('loginForm');
        this.registerForm = document.getElementById('registerForm');
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        // Login form
        this.loginForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });
        
        // Register form
        this.registerForm?.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });
        
        // Form switching
        document.getElementById('showRegister')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showRegisterForm();
        });
        
        document.getElementById('showLogin')?.addEventListener('click', (e) => {
            e.preventDefault();
            this.showLoginForm();
        });
        
        // Password strength indicator
        document.getElementById('password')?.addEventListener('input', (e) => {
            this.updatePasswordStrength(e.target.value);
        });
        
        document.getElementById('registerPassword')?.addEventListener('input', (e) => {
            this.updatePasswordStrength(e.target.value, 'register');
        });
    }
    
    async handleLogin() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const submitBtn = document.getElementById('loginSubmit');
        
        this.setButtonLoading(submitBtn, true);
        
        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage('Login successful! Welcome back! 😊', 'success');
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                this.showMessage(data.message, 'error');
            }
        } catch (error) {
            this.showMessage('An error occurred during login. Please try again.', 'error');
        } finally {
            this.setButtonLoading(submitBtn, false);
        }
    }
    
    async handleRegister() {
        const username = document.getElementById('registerUsername').value;
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const submitBtn = document.getElementById('registerSubmit');
        
        // Client-side validation
        if (password !== confirmPassword) {
            this.showMessage('Passwords do not match', 'error');
            return;
        }
        
        this.setButtonLoading(submitBtn, true);
        
        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, password })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showMessage(data.message, 'success');
                setTimeout(() => {
                    this.showLoginForm();
                }, 3000);
            } else {
                this.showMessage(data.message, 'error');
            }
        } catch (error) {
            this.showMessage('An error occurred during registration. Please try again.', 'error');
        } finally {
            this.setButtonLoading(submitBtn, false);
        }
    }
    
    showLoginForm() {
        document.getElementById('loginFormContainer').style.display = 'block';
        document.getElementById('registerFormContainer').style.display = 'none';
        document.querySelector('.form-title').textContent = 'Welcome Back! 😊';
    }
    
    showRegisterForm() {
        document.getElementById('loginFormContainer').style.display = 'none';
        document.getElementById('registerFormContainer').style.display = 'block';
        document.querySelector('.form-title').textContent = 'Join EmotiCare! 🌟';
    }
    
    updatePasswordStrength(password, type = 'login') {
        const strengthIndicator = document.getElementById(type === 'login' ? 'passwordStrength' : 'registerPasswordStrength');
        if (!strengthIndicator) return;
        
        let strength = 0;
        let feedback = [];
        
        if (password.length >= 8) strength++;
        else feedback.push('At least 8 characters');
        
        if (/[A-Z]/.test(password)) strength++;
        else feedback.push('One uppercase letter');
        
        if (/[a-z]/.test(password)) strength++;
        else feedback.push('One lowercase letter');
        
        if (/\d/.test(password)) strength++;
        else feedback.push('One number');
        
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        else feedback.push('One special character');
        
        const strengthTexts = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const strengthColors = ['#ff4757', '#ff6348', '#ffa502', '#2ed573', '#1e90ff'];
        
        strengthIndicator.textContent = password ? strengthTexts[strength] || 'Very Weak' : '';
        strengthIndicator.style.color = strengthColors[strength] || '#ff4757';
        
        if (feedback.length > 0 && password) {
            strengthIndicator.textContent += ` (Need: ${feedback.join(', ')})`;
        }
    }
    
    setButtonLoading(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.innerHTML = '<span class="loading"></span> Please wait...';
        } else {
            button.disabled = false;
            const originalText = button.dataset.originalText || 
                (button.id.includes('login') ? 'Sign In' : 'Create Account');
            button.innerHTML = originalText;
        }
    }
    
    showMessage(message, type) {
        const messageContainer = document.getElementById('messageContainer');
        if (!messageContainer) return;
        
        messageContainer.className = `message-container ${type}`;
        messageContainer.textContent = message;
        messageContainer.style.display = 'block';
        
        setTimeout(() => {
            messageContainer.style.display = 'none';
        }, 5000);
    }
}

// Initialize auth manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new AuthManager();
});
