# 🩺 Dr.Wise – AI Medical Health Assistant

**Dr.Wise** is an AI-powered web application that delivers intelligent, personalized medical assistance using **Google Gemini (Text + Vision)** and **Flask (Python)**. It helps users understand symptoms, manage health goals, identify medicines, and track wellness — all while ensuring admin control and secure user access.

---

## 📘 About the Project

Dr.Wise bridges the gap between people and essential health support. It is not a diagnostic tool, but an AI-powered assistant for educational and lifestyle improvement purposes. It simulates a doctor-patient interaction and responds with expert-like clarity using the Gemini AI model.

Users can:
- Analyze symptoms and receive insights
- Generate personalized meal plans
- Identify pills using image OCR
- Calculate BMI and track fitness
- Set pill reminders
- Interact with a health chat AI
- Use a complete admin dashboard

---

## 🎯 Project Objectives

- ✅ Build a conversational AI-powered medical support system
- ✅ Use Google Gemini API for text and image-based intelligence
- ✅ Enable secure login, registration, and session tracking
- ✅ Store all user activity using a relational database (SQLite)
- ✅ Provide an Admin Panel to manage users and health logs
- ✅ Offer modules like diet tips, BMI calculator, pill reminder, and workouts
- ✅ Support image-based medicine identification using OCR
- ✅ Ensure a user-friendly and mobile-responsive UI

---

## 🧰 Tech Stack

| Component      | Technology                                |
|----------------|--------------------------------------------|
| Language       | Python 3.x                                 |
| Web Framework  | Flask                                      |
| AI Model       | Google Gemini 1.5 Flash (Text & Vision)    |
| OCR            | pytesseract + Pillow                       |
| Frontend       | HTML5, CSS3, Bootstrap 5, Jinja2 Templates |
| Database       | SQLite + SQLAlchemy ORM                    |
| Auth           | Flask-Login                                |
| Markdown       | markdown2 + MarkupSafe                     |
| Config         | python-dotenv                              |

---

## 🛠️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/mhd-sadiq/ai_medical_health_assistant.git
cd ai_medical_health_assistant
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4. Add Gemini API Key in `.env` File

Create a `.env` file with your Gemini API key:

```env
GEMINI_API_KEY=AIzaSyBma-nl2BCMKSGXdM5yS-bRyYt0K0_sxdg
```

> ⚠️ Keep this file secure. Never upload your `.env` to GitHub.

### 5. Run the Application

```bash
python app.py
```

Open browser at: [http://localhost:5000](http://localhost:5000)

---

## 🧭 Application Routes Overview

| Route             | Description                             |
|-------------------|-----------------------------------------|
| `/`               | Homepage                                |
| `/symptom`        | Symptom checker                         |
| `/diet`           | Diet planning module                    |
| `/chat`           | General medical AI Q&A                  |
| `/bmi`            | BMI calculator                          |
| `/medicine`       | Medicine identifier using image         |
| `/exercise`       | Fitness guidance and logger             |
| `/pill_reminder`  | Pill schedule manager                   |
| `/blood_donor`    | Donor registry & search                 |
| `/admin`          | Admin dashboard                         |

---

## 🚀 Features in Detail

### 🤖 1. AI Health Chat

- Users ask any health-related question (e.g., "What is jaundice?")
- AI responds with a clean Markdown format:
  - Overview
  - Symptoms
  - Causes
  - Treatments
  - When to see a doctor
- Chat logs are stored per-user and viewable by admins.

---

### 🤒 2. Symptom Checker

- Users enter symptoms (with age, gender, severity, etc.)
- Gemini AI identifies patterns and gives a non-diagnostic report.
- Response includes:
  - Disclaimer
  - Possible causes
  - Next steps
  - Urgency suggestions

---

### 🥗 3. Diet Planner

- Personalized based on:
  - Age, gender, height, weight
  - Activity level and health goals
- AI creates:
  - Foods to include/avoid
  - Sample daily diet plan
  - Nutrition advice
- Chats are logged and admin-accessible.

---

### ⚖️ 4. BMI Calculator

- BMI is calculated as per the formula:
  > BMI = weight(kg) / (height(m)²)
- Categorizes user as:
  - Underweight
  - Normal
  - Overweight
  - Obese
- Provides tailored advice based on result.

---

### 💊 5. Pill Reminder System

- Add medicines with:
  - Dosage
  - Time of day or exact time
  - Start/end date
  - Frequency (daily, weekly, etc.)
- Activate/deactivate/delete reminders anytime.

---

### 🧠 6. Medicine Identifier

- Upload photo of medicine strip or package
- OCR extracts visible text
- Gemini analyzes and provides:
  - Name
  - Usage
  - Dosage
  - Side effects

---

### 🏋️ 7. Exercise Logger & Library

- Categories:
  - Common
  - Muscle Building
  - Yoga
- Includes:
  - Title, duration, rest
  - Description
  - YouTube video embed
- Users can log and track exercise

---

### 🩸 8. Blood Donor Registry

- Users can:
  - Register with blood group & location
  - Search donors by location & group
  - Use chat for donor-specific queries
- Admin can view all blood donor records

---

### 🔐 9. Admin Dashboard

- Role-based access (Admin / Superuser)
- Admin actions:
  - Add / delete / promote / block users
  - View login records, chat logs, pill logs
  - View exercise and BMI records
- Dashboard designed for intuitive review and control

---

## 📊 Database Models Summary

| Model               | Purpose                                 |
|---------------------|-----------------------------------------|
| `User`              | Stores user info and role               |
| `LoginHistory`      | Login timestamps                        |
| `GeneralHealthChat` | General health chat                     |
| `SymptomCheckerChat`| Symptom inputs & outputs                |
| `DietTipsChat`      | Diet plan queries                       |
| `BMICalculatorChat` | BMI logs                                |
| `PillReminder`      | Medication reminders                    |
| `ExerciseHistory`   | Fitness activity logs                   |
| `BloodDonor`        | Donor registry                          |
| `BloodDonorChat`    | Blood donor chat history                |

---

## 📈 Future Enhancements

- 🌐 Multilingual support (e.g., Malayalam, Hindi)
- 🗣️ Voice interaction and speech-to-text
- 📱 Android/iOS app version
- 📍 Real-time emergency location help
- 📤 Export history as PDF
- 🔔 Notification system for pills & tips

---

## 👨‍💼 Author & Maintainer

**👤 Muhammed Sadiq K**  
📧 [sadiqkalathil77@gmail.com](mailto:sadiqkalathil77@gmail.com)  
🔗 [GitHub – mhd-sadiq](https://github.com/mhd-sadiq)  
🗓️ Project Started: June 2025

---

