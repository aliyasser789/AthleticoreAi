# Athleticore.AI
### *The Intelligent Fitness & Nutrition Ecosystem*

<img src="Athleticore images/main.png" width="800">

---

## 🚀 Overview
**Athleticore.AI** is a comprehensive, AI-driven wellness platform developed for the **2025-2026** period. It serves as a personalized fitness coach and nutritionist, enabling users to track metabolic needs, log nutrition via natural language, and manage detailed workout regimes through a high-performance, futuristic interface.

<img src="Athleticore images/image.png" width="800">

## ✨ Key Features

### 🧠 AI Nutrition Coach & Tracker
* **Natural Language Processing**: Users can chat with an AI assistant to log meals; the system automatically extracts calories, protein, carbs, and fats.
* **Real-time Macro Visualization**: Interactive dashboards display daily totals for protein, carbohydrates, and fats.
* **Surplus Monitoring**: Automatically calculates the difference between consumed calories and the user's daily goal.
* **History Management**: A scrollable food feed allows for auditing and deleting past entries.

<img src="Athleticore images/image2.png" width="800">

### 🏋️ Advanced Workout Logger
* **Comprehensive Tracking**: Users can create logs for specific training sessions, recording exercise names, sets, reps, and weight.
* **Progressive Overload**: Tracks "Previous Weight" for every exercise to help users monitor strength gains over time.
* **Dynamic Management**: A visual feed of all workouts with detailed modals for updating session notes and performance stats.

<img src="Athleticore images/3.png" width="800">

### 📊 Metabolic & Goal Profile (TDEE)
* **AI-Assisted Calculation**: Personalized TDEE (Total Daily Energy Expenditure) calculation based on lifestyle and activity levels.
* **Goal Alignment**: Strategic planning for "Cut", "Bulk", or "Maintain" objectives.

### 🔒 Account & Profile Security
* **Robust Authentication**: Secure registration and login system with SHA-256 password hashing.
* **Automated Recovery**: Integrated password reset system that generates and emails temporary credentials via SMTP.
* **Body Stats Tuning**: Manage personal attributes including age, gender, height, and weight for optimized AI recommendations.

---

## 🛠 Tech Stack
* **Backend**: Python Flask
* **AI Engine**: Groq API utilizing the `llama-3.3-70b-versatile` model
* **Database**: SQLite
* **UI/UX**: Glassmorphism CSS design with 'Orbitron' and 'Inter' typography
* **Communication**: SMTPLib for secure automated emailing

---

## 📂 Project Structure
```text
AthleticoreAi/
├── app/
│   ├── api/          # Route handlers for auth, calories, chat, TDEE, and workouts
│   ├── db/           # Database helper and initialization scripts
│   ├── models/       # Data classes for users, logs, exercises, and profiles
│   ├── services/     # Business logic, AI coaching clients, and email management
│   ├── static/       # CSS stylesheets and UI image assets
│   └── templates/    # HTML templates for all application views
├── run.py            # Main application entry point
├── requirements.txt  # Python dependency list
└── .gitignore        # Version control exclude patterns
```

---

## 📖 Usage Guide

### 1. Account Setup & Profile
* **Registration**: Start by creating an account. You will need to provide your basic body metrics: Age, Gender, Height (cm), and Weight (kg). These are used by the AI to calculate your baseline requirements.
* **TDEE Calculation**: Navigate to the **TDEE** section to calculate your Total Daily Energy Expenditure. Select your activity level (Sedentary to Extremely Active) and set your fitness goal—whether it's to **Cut** (lose weight), **Bulk** (gain muscle), or **Maintain**.

### 2. AI Nutrition Tracking
* **Logging Meals**: Go to the **Calories** page and use the AI Chat. Instead of searching a database, simply type what you ate (e.g., "I had 2 boiled eggs and a piece of whole-wheat toast").
* **Automated Extraction**: The AI will automatically identify the food items and calculate their calories, protein, carbs, and fats.
* **Monitoring Progress**: Your **Dashboard** will update in real-time, showing your daily totals against your TDEE goal and highlighting any calorie surplus or deficit.

### 3. Workout Management
* **Create a Log**: Visit the **Create Log** page to record your training sessions. You can add multiple exercises per workout.
* **Exercise Details**: For each exercise, enter the name, number of sets, repetitions, and the weight used.
* **History & Progression**: View your **Workout History** to see past sessions. The system tracks "Previous Weight" for each exercise to help you ensure you are applying progressive overload in every session.

### 4. AI Coaching
* **Coach Chat**: If you need advice on training or nutrition, head to the **Coach** page. This is a general AI assistant ready to answer fitness-related questions and provide guidance on your journey.

### 5. Settings & Security
* **Update Stats**: As your weight or activity level changes, update your profile in **Settings** to keep your AI recommendations accurate.
* **Password Recovery**: If you forget your credentials, use the **Forgot Password** link on the login page to receive a temporary password via your registered email.

---

## ✍️ Author
* **Ali Yasser Ali**

---

## 📄 License
This project is licensed under the MIT License.

