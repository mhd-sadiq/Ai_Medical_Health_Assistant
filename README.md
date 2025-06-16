# 🩺 AI Medical Health Assistant

An AI-powered web application designed to provide users with basic health assistance by simulating intelligent conversations. It helps users check symptoms, receive diet suggestions, and access non-emergency medical guidance — powered by Google’s Gemini API and built using Python and Flask.

---

## 📘 About the Project

This project is an **AI Medical Health Assistant** that aims to provide a friendly, intelligent health assistant to users through a web interface. The system uses **Gemini API** to respond to health-related queries and simulate realistic interactions. It offers:

* Symptom analysis (non-diagnostic)
* Personalized diet planning
* Basic medical guidance
* Placeholder for emergency instructions

---

## 🎯 Project Objectives

* ✅ Create a web-based conversational AI assistant for health support.
* ✅ Use Google’s Gemini API to interpret user queries.
* ✅ Provide customized diet plans based on user goals.
* ✅ Offer basic symptom insights.
* ✅ Ensure a clean, user-friendly, and mobile-responsive interface.

---

## 🚀 Features Overview

| Feature                | Description                                                                 |
| ---------------------- | --------------------------------------------------------------------------- |
| 🤖 AI Symptom Checker  | User can enter symptoms and receive possible causes using Gemini AI         |
| 🥗 Diet Planner        | User receives a personalized meal plan based on their fitness goal          |
| 💬 Medical Q\&A        | General medical questions are answered contextually                         |
| 🆘 Emergency Resources | A dedicated section for emergency awareness (can be expanded in the future) |

---

## 🧰 Tech Stack Used

| Component           | Technology Used              |
| ------------------- | ---------------------------- |
| Language            | Python                       |
| Backend Framework   | Flask                        |
| AI API              | Google Gemini API            |
| Frontend            | HTML, CSS, Bootstrap, Jinja2 |
| Markdown Rendering  | markdown2, MarkupSafe        |
| Location Handling   | Geopy (for future expansion) |
| Environment Control | python-dotenv                |

---

## 🛠️ Project Architecture

### 🧱 System Components

* **Frontend**: Accepts user input and renders results
* **Flask Backend**: Handles user requests and API calls
* **Gemini AI Engine**: Generates intelligent responses
* **Markdown Renderer**: Converts AI output to HTML

### 🔄 Data Flow

```text
User Input → Flask → Gemini API → AI Markdown Output → HTML Render → User View
```

---

## 🛠️ Setup and Installation

Follow these steps to run the project locally:

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/mhd-sadiq/ai_medical_health_assistant.git
cd ai_medical_health_assistant
```

### 2️⃣ Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Set up Environment Variables

Create a `.env` file in the root directory and add your API key securely:

```env
GEMINI_API_KEY=AIzaSyBma-nl2BCMKSGXdM5yS-bRyYt0K0_sxdg
```

> 🔐 **Note**: Never share this API key publicly. Keep `.env` in your `.gitignore`.

### 5️⃣ Run the Application

```bash
python app.py
```

Open your browser and go to: `http://localhost:5000`

---

## 🔮 Application Routes

| Route        | Functionality                                   |
| ------------ | ----------------------------------------------- |
| `/`          | Homepage / General interface                    |
| `/symptom`   | Accepts symptoms → Returns possible causes      |
| `/diet`      | Accepts goals → Returns custom diet plan        |
| `/chat`      | General-purpose health questions                |
| `/emergency` | Placeholder for emergency info and instructions |

---

## 🖼️ Screenshots

### 🔷 Homepage – AI Health Assistant Dashboard

![AI Health Assistant Homepage](screenshots/hom![Screenshot 2025-06-16 114820](https://github.com/user-attachments/assets/cdfb302c-b536-495e-8791-16af090c3f57)
epage.png)

> The homepage provides access to all major services: symptom checker, diet tips, AI chat, and emergency tools — built with a clean, accessible design.

---

## 🔐 Emergency Resource Module

This section is designed to be expanded later. Currently, it contains:

* 🚨 Emergency tips placeholder
* 📞 Plans to integrate emergency contact numbers
* 📉 Plans to add First Aid guidance
* 📍 Optional geolocation-based services (using Geopy)

---

## 📊 Future Enhancements

* 🌐 Multilingual support
* 🎤 Voice input and Text-to-Speech features
* 📲 Android/iOS mobile app version
* 👤 User login and history tracking
* 📡 Real-time emergency help suggestions
* 🤖 Smarter symptom checker using NLP training

---

## 👨‍💼 Author & Maintainer

* **👤 Muhammed Sadiq K**
  🗓️ Project Created: 15 June 2025
  📧 Email: [sadiqkalathil77@gmail.com](mailto:sadiqkalathil77@gmail.com)
  🔗 GitHub: [mhd-sadiq](https://github.com/mhd-sadiq)

---



⭐ \*If you find this project helpful, feel free to star the repository an
