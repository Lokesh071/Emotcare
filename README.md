# 🌟 EmotiCare - AI-Powered Emotion Detection & Mental Health Support

<div align="center">

![EmotiCare Logo](https://img.shields.io/badge/EmotiCare-AI%20Emotion%20Detection-purple?style=for-the-badge&logo=brain&logoColor=white)

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Visit%20App-success?style=for-the-badge)](https://emotcare.onrender.com)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge&logo=github)](https://github.com/Lokesh071/Emotcare)
[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-green?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com)

**A comprehensive web application that combines real-time emotion detection with AI-powered mental health support**

</div>

---

## ✨ Features

### 🎭 **Real-Time Emotion Detection**
- 📹 **Live Camera Feed**: Real-time emotion analysis through webcam
- 🧠 **Advanced ML Models**: TensorFlow-powered emotion recognition
- 😊 **Multiple Emotions**: Detects happy, sad, stressed, depressed, and peaceful states
- 📊 **Visual Feedback**: Beautiful UI with emotion indicators and confidence levels

### 🤖 **AI-Powered Chat Support**
- 🚀 **Groq AI Integration**: Real-time AI responses using Llama models
- 💬 **Contextual Conversations**: AI responds based on detected emotions
- 🎯 **Emotional Support**: Personalized suggestions and coping strategies
- ⚡ **Continuous Chat**: Chat remains active even after stopping emotion detection

### 📊 **Analytics & Insights**
- 📈 **Emotion Tracking**: Historical emotion data and trends
- 📋 **Progress Monitoring**: Track emotional well-being over time
- 📊 **Visual Charts**: Interactive charts showing emotion patterns
- 📝 **Personalized Reports**: Detailed insights into emotional health

### 🔐 **User Management**
- 🔒 **Secure Authentication**: Email verification and password reset
- 👤 **User Profiles**: Personalized user accounts and settings
- 🛡️ **Session Management**: Secure session handling
- 🔐 **Privacy Protection**: User data protection and privacy controls

---



## 🛠️ Technology Stack

<div align="center">

### Backend
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat&logo=tensorflow&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-27338e?style=flat&logo=OpenCV&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)

### Frontend
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![Chart.js](https://img.shields.io/badge/Chart.js-FF6384?style=flat&logo=chartdotjs&logoColor=white)



</div>

---

## 📋 Prerequisites

- **Python 3.8+**
- **Webcam** (for emotion detection)
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)

---

## 🔧 Local Installation & Setup

### 1. **Clone Repository**
```bash
git clone https://github.com/Lokesh071/Emotcare.git
cd Emotcare
```

### 2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Environment Variables**
Create a `.env` file:
```env
SECRET_KEY=your-secret-key-here
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 5. **Run Application**
```bash
python app.py
```

Visit `http://localhost:5000` 🌐

---

## 🌐 Deployment

### **Deploy to Render** (Recommended)

1. **Fork this repository**
2. **Connect to Render**: [dashboard.render.com](https://dashboard.render.com)
3. **Create Web Service** from your GitHub repository
4. **Configure**:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
5. **Set Environment Variables** (API keys, etc.)
6. **Deploy** 🚀

📖 **Detailed Guide**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 📁 Project Structure

```
EmotiCare/
├── 📄 app.py                    # Main Flask application
├── 📄 wsgi.py                   # WSGI entry point
├── 📄 requirements.txt          # Dependencies
├── 📄 Procfile                  # Deployment config
├── 📂 backend/                  # Backend logic
│   ├── 📂 models/              # ML & database models
│   ├── 📂 routes/              # API routes
│   └── 📂 utils/               # Utilities
├── 📂 frontend/                 # Frontend
│   ├── 📂 static/              # CSS, JS, assets
│   └── 📄 *.html               # Templates
├── 📂 models/                   # Pre-trained ML models
└── 📄 README.md                # This file
```

---

## 🎯 Key Features Showcase

### **🎭 Emotion Detection Interface**
- Large, responsive camera view
- Real-time emotion analysis
- Single-line emotion display
- Professional UI with purple glow effects

### **💬 AI Chat Integration**
- Context-aware responses based on emotions
- Support for multiple AI providers (Groq, OpenAI)
- Continuous conversation flow
- Emotional support and suggestions

### **📊 Analytics Dashboard**
- Emotion tracking over time
- Visual charts and graphs
- Progress monitoring
- Personalized insights

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Open** Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

<div align="center">

**Lokesh071**

[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Lokesh071)
[![Portfolio](https://img.shields.io/badge/Portfolio-FF5722?style=for-the-badge&logo=todoist&logoColor=white)](https://github.com/Lokesh071)

</div>

---

## 🙏 Acknowledgments

- **TensorFlow** team for ML frameworks
- **OpenCV** community for computer vision tools
- **Groq** for advanced AI capabilities
- **Render** for reliable cloud hosting
- **Open Source** community for inspiration

---

<div align="center">

**⭐ Star this repository if you found it helpful!**

**Made with ❤️ by [Lokesh071](https://github.com/Lokesh071)**

</div>
