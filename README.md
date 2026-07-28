# 💊 Medicine Reminder System - Web & Vercel Edition

A modern, full-featured **Medicine Reminder System** with rich aesthetics, real-time dose tracking, schedule management, adherence analytics, and browser audio/desktop push notifications.

Built with a responsive, glassmorphism dark-mode UI designed for deployment on **Vercel** and local execution.

---

## 🌟 Key Features

- **🔐 User Authentication**: Multi-user registration, secure login, and session persistence.
- **💊 Medicine CRUD**: Add, edit, delete, and view medicines with dosage, frequency, times, and special instructions.
- **📅 Daily Schedule Generator**: Auto-generates dose logs for any date with real-time **Mark as Taken** / **Mark as Missed** actions.
- **⏰ Real-Time Alerts & Sound Notifications**: Web Audio API sound alerts and Web Notification API desktop popups when doses are due.
- **📊 Adherence Metrics & CSV Reports**: Summary statistics, adherence rate calculation, filterable history logs, and instant CSV exports.
- **🌐 Vercel-Ready**: Zero `npm` build requirement. Deploys natively to Vercel via GitHub.

---

## 🚀 How to Run Locally

You can run the web application locally on Windows, macOS, or Linux using Python's built-in HTTP server:

```powershell
# 1. Navigate to project directory
cd "d:\Medicine Remainder System.11"

# 2. Start local web server with Python
& "C:\Users\Sivani\AppData\Local\Programs\Python\Python312\python.exe" -m http.server 8000
```

Then open your browser and navigate to: **`http://localhost:8000`**

---

## ☁️ Deploying to Vercel

1. Push this repository to **GitHub** (already configured).
2. Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New Project"**.
3. Import `https://github.com/harshi20068-bvrc/Medicine-Remainder-System11.git`.
4. Click **Deploy**. Vercel will automatically detect `vercel.json`, `index.html`, and `api/index.py` and deploy your web app instantly!

---

## 📁 Repository Structure

```
.
├── index.html        # Main Single Page Web Application
├── index.css         # Glassmorphism Dark Mode Design System
├── app.js            # Frontend State, Storage, Audio Alerts & Logic
├── vercel.json       # Vercel Deployment Configuration
├── api/
│   └── index.py      # Vercel Serverless Function Handler
├── main.py           # Desktop Python Entry Point (Legacy)
├── requirements.txt  # Python requirements
└── README.md         # Project Documentation
```
