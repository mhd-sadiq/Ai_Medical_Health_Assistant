from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from dotenv import load_dotenv
import os
import google.generativeai as genai
import markdown2
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
from werkzeug.utils import secure_filename
from PIL import Image
import io
import mimetypes
import pytesseract
import requests
from datetime import datetime, timedelta
import logging
import sys
from markupsafe import Markup
import pytz
from getpass import getpass
try:
    from zoneinfo import ZoneInfo
    IST = ZoneInfo('Asia/Kolkata')
except ImportError:
    IST = pytz.timezone('Asia/Kolkata')

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# Ensure the instance folder exists before initializing the database
os.makedirs('instance', exist_ok=True)

# Initialize Flask
app = Flask(__name__)
# Use absolute path for SQLite database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, 'instance', 'users.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SECRET_KEY'] = 'your_secret_key_here'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_superuser = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Add new models for separate chat tables
class GeneralHealthChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

class DietTipsChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

# Add new model for SymptomCheckerChat
class SymptomCheckerChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

# Add new model for BMICalculatorChat
class BMICalculatorChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

class LoginHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

class BloodDonor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)

class BloodDonorChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

class ExerciseHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise_title = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in seconds
    timestamp = db.Column(db.DateTime, nullable=False)

class PillReminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pill_name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(100), nullable=False)  # e.g., "daily", "twice daily", "every 8 hours"
    time_of_day = db.Column(db.String(100), nullable=True)  # now optional
    exact_time = db.Column(db.Time, nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)  # null means ongoing
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(IST))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/symptom', methods=['GET', 'POST'])
@login_required
def symptom_checker():
    response = ""
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '')
        age = request.form.get('age', '')
        gender = request.form.get('gender', '')
        weight = request.form.get('weight', '')
        severity = request.form.get('severity', '')
        duration = request.form.get('duration', '')

        # Save user's symptom input to SymptomCheckerChat if user is logged in
        if symptoms and current_user.is_authenticated:
            try:
                user_chat = SymptomCheckerChat(
                    user_id=current_user.id,
                    message=f"User: {symptoms}",
                    timestamp=datetime.now(IST)
                )
                db.session.add(user_chat)
                db.session.commit()
            except Exception as e:
                print(f"Error saving user message: {e}")

        prompt = f"""
You are an AI-powered symptom checker. Your job is to analyze the user's input and determine if it contains real symptoms (such as fever, cough, pain, headache, nausea, vomiting, etc.).

The user described their symptoms as: "{symptoms}"

Instructions:
- If the input does NOT contain real symptoms, reply exactly:
"❌ Please enter valid symptoms for analysis."
- If the input DOES contain symptoms, analyze the user's symptoms and profile:
  - Symptoms: {symptoms}
  - Age Group: {age}
  - Gender: {gender}
  - Weight: {weight} kg
  - Severity: {severity}
  - Duration: {duration}
- Use clear, structured Markdown formatting.
- Use bold section headers (##) for each section: Disclaimer, Possible Causes, Next Steps, When to Seek Medical Help, Final Note.
- Use bullet points for lists.
- Do not merge sections or add extra commentary outside the specified sections.
- Ensure each section is clearly separated and formatted.
- If symptoms are mild, short duration, and user is young, suggest home remedies and rest.
- If symptoms are severe, long duration, or user is elderly, suggest urgent medical attention.
- If the user is female and has a headache for many days, analyze for migraines, stress, or other causes.
- Always start with a disclaimer that this is informational only.

## Disclaimer
## Possible Causes
## Next Steps
## When to Seek Medical Help
## Final Note

Be specific and do not repeat content.
"""

        try:
            raw_response = model.generate_content(prompt).text
            response = Markup(markdown2.markdown(raw_response))
            # Save AI response to SymptomCheckerChat
            if current_user.is_authenticated and raw_response:
                try:
                    ai_chat = SymptomCheckerChat(
                        user_id=current_user.id,
                        message=f"AI: {raw_response}",
                        timestamp=datetime.now(IST)
                    )
                    db.session.add(ai_chat)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving AI response: {e}")
        except Exception as e:
            response = f"⚠️ Error: {str(e)}"
    # Fetch chat history after saving both user and AI messages
    chat_history = SymptomCheckerChat.query.filter_by(user_id=current_user.id).order_by(SymptomCheckerChat.timestamp.asc()).all() if current_user.is_authenticated else []
    for chat in chat_history:
        if hasattr(chat.timestamp, 'astimezone'):
            chat.timestamp = chat.timestamp.astimezone(IST)
        else:
            chat.timestamp = chat.timestamp.replace(tzinfo=pytz.utc).astimezone(IST)
    return render_template("symptom_checker.html", response=response, chat_history=chat_history)

@app.route('/diet', methods=['GET', 'POST'])
@login_required
def diet_tips():
    response = ""
    plan_fallback = '''
**Sample Diet Plan**
- Breakfast: 3 eggs, 1 toast, 1 glass of milk
- Lunch: Grilled chicken, brown rice, salad
- Snack: 1 apple, handful of nuts
- Dinner: Fish curry, steamed vegetables
'''
    if request.method == 'POST':
        age = request.form.get('age', '')
        weight = request.form.get('weight', '')
        height = request.form.get('height', '')
        gender = request.form.get('gender', '')
        activity_level = request.form.get('activity_level', '')
        goal = request.form.get('goal', '')

        prompt = f"""
You are a highly personalized diet assistant. Only respond to health-related queries (e.g., weight loss, muscle gain, diabetes control, food for specific conditions, etc.).

If the user's goal is NOT health-related, reply exactly:
"❌ This assistant only answers diet-related health goals. Please enter a valid health-related goal."

If the goal IS health-related, generate a diet plan and advice based on the following user profile:
- Age: {age}
- Weight: {weight} kg
- Height: {height} cm
- Gender: {gender}
- Activity Level: {activity_level}
- Health Goal: {goal}

Instructions:
- Use clear, structured Markdown formatting.
- Use bold section headers (##) for each section: Overview, Foods to Include, Foods to Avoid, Sample Diet Plan, Important Considerations.
- Use bullet points for lists.
- For the sample meal plan, you MUST use a point-by-point format, with each meal and foods on a new line, like this:
  - Breakfast: 3 eggs, 1 toast, 1 glass of milk
  - Lunch: Grilled chicken, brown rice, salad
  - Snack: 1 apple, handful of nuts
  - Dinner: Fish curry, steamed vegetables
- Do NOT use a table for the sample meal plan.
- Place any additional notes (hydration, portion control, gradual changes, family involvement, professional guidance, etc.) in a clearly separated 'Important Considerations' section BELOW the plan, using bullet points.
- Ensure each section (Overview, Foods to Include, Foods to Avoid, Sample Diet Plan, Important Considerations) is clearly separated and formatted.
- Adjust calories, protein, and food types based on age, weight, height, activity, and goal.
- If the user is a child (age < 13) and low weight and sedentary, suggest a light, balanced diet.
- If the user is an adult (age 20-64) with high weight and active, suggest a protein-rich, higher-calorie diet.
- If the user is a senior (age 65+) with diabetes or similar goal, suggest low-sugar, diabetic-safe meals.
- Always provide a sample meal plan for a day.
- If you do not provide a plan in the correct format, the user will see a default plan instead.

## Overview
## Foods to Include
## Foods to Avoid
## Sample Diet Plan

- Breakfast: 
- Lunch: 
- Snack: 
- Dinner: 

## Important Considerations
- 

Be specific and do not repeat content.
"""

        try:
            raw_response = model.generate_content(prompt).text.strip()
            # Remove any tables from the response
            cleaned_response = re.sub(r'\|.*\|', '', raw_response)
            # Ensure at least one meal plan in the correct format is present
            if not re.search(r'Breakfast:|Lunch:|Snack:|Dinner:', cleaned_response):
                cleaned_response += "\n\n" + plan_fallback
            response = Markup(markdown2.markdown(cleaned_response))
            # Save user input and AI response to DietTipsChat only after successful AI response
            if current_user.is_authenticated:
                try:
                    user_input = f"User: Age: {age}, Weight: {weight}kg, Height: {height}cm, Gender: {gender}, Activity: {activity_level}, Goal: {goal}"
                    user_chat = DietTipsChat(
                        user_id=current_user.id,
                        message=user_input,
                        timestamp=datetime.now(IST)
                    )
                    db.session.add(user_chat)
                    ai_chat = DietTipsChat(
                        user_id=current_user.id,
                        message=f"AI: {cleaned_response}",
                        timestamp=datetime.now(IST)
                    )
                    db.session.add(ai_chat)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving chat messages: {e}")
        except Exception as e:
            response = f"⚠️ Error: {str(e)}"

    # Fetch chat history after saving both user and AI messages
    chat_history = DietTipsChat.query.filter_by(user_id=current_user.id).order_by(DietTipsChat.timestamp.asc()).all() if current_user.is_authenticated else []
    for chat in chat_history:
        if hasattr(chat.timestamp, 'astimezone'):
            chat.timestamp = chat.timestamp.astimezone(IST)
        else:
            chat.timestamp = chat.timestamp.replace(tzinfo=pytz.utc).astimezone(IST)
    return render_template("diet_tips.html", response=response, chat_history=chat_history)

@app.route('/chat', methods=['GET', 'POST'])
@login_required
def health_chat():
    response = ""
    error = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if not question:
            error = "❌ Please enter a health-related question."
        else:
            # Save user's question to GeneralHealthChat if user is logged in
            if current_user.is_authenticated:
                try:
                    user_chat = GeneralHealthChat(
                        user_id=current_user.id,
                        message=f"User: {question}",
                        timestamp=datetime.now(IST)
                    )
                    db.session.add(user_chat)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving user message: {e}")

            # Detect if the question is about symptoms, treatment, recommended actions, or a definition/general info.
            symptoms_pattern = re.compile(r"(symptoms?\s+of|what\s+are\s+the\s+symptoms|list\s+symptoms|show\s+symptoms|tell\s+me\s+symptoms|signs?\s+of|what\s+are\s+the\s+signs|symptoms\s*[:?]|signs\s*[:?])", re.IGNORECASE)
            treatment_pattern = re.compile(r"(treatment\s+for|how\s+to\s+treat|treat\s+\w+|cure\s+\w+|remedy\s+for|how\s+can\s+i\s+treat|how\s+do\s+i\s+treat)", re.IGNORECASE)
            action_pattern = re.compile(r"(what\s+should\s+i\s+do|what\s+can\s+i\s+take|i\s+have\s+|i'm\s+having|i\s+am\s+having|i\s+feel\s+|i\s+got\s+)", re.IGNORECASE)
            definition_pattern = re.compile(r"(what\s+is|describe|tell\s+me\s+about|explain|definition\s+of)", re.IGNORECASE)

            prompt = ""
            postprocess_type = None
            if symptoms_pattern.search(question):
                # SYMPTOMS
                postprocess_type = 'symptoms'
                prompt = f'''
You are a health assistant. The user asked: "{question}"
Instructions:
- Respond ONLY with a clean, concise, bulleted list of symptoms for the condition or disease mentioned.
- Start with a header: 'Symptoms of <Condition>:'
- Do NOT include any extra explanation, causes, treatments, or images.
- Example:
Symptoms of Jaundice:
- Yellowing of the skin and eyes
- Dark urine
- Fatigue
- Abdominal pain
'''
            elif treatment_pattern.search(question):
                # TREATMENT
                postprocess_type = 'treatment'
                prompt = f'''
You are a health assistant. The user asked: "{question}"
Instructions:
- Respond ONLY with a clean, concise, bulleted list of treatment methods for the condition or disease mentioned.
- Start with a header: 'Treatment for <Condition>:'
- Do NOT include any extra explanation, causes, symptoms, or images.
- Example:
Treatment for Fever:
- Stay hydrated
- Take rest
- Use antipyretics like paracetamol
- Monitor temperature
'''
            elif action_pattern.search(question):
                # ACTION/RECOMMENDATION
                postprocess_type = 'action'
                prompt = f'''
You are a health assistant. The user asked: "{question}"
Instructions:
- Respond ONLY with a clean, concise, bulleted list of recommended actions for the user's situation.
- Start with a header: 'If you have <Condition>:'
- Do NOT include any extra explanation, causes, symptoms, or images.
- Example:
If you have fever:
- Drink plenty of fluids
- Take rest
- Take paracetamol if needed
- Consult a doctor if fever persists
'''
            else:
                # DEFINITION/GENERAL INFO
                postprocess_type = 'definition'
                prompt = f"""
You are a health-focused AI assistant. Only respond to health-related queries (definitions, symptoms, food, or health advice).
The user asked: "{question}"
Instructions:
- If the question is NOT health-related, reply exactly:
"❌ This assistant only answers health-related questions. Please ask something related to health."
- If the question IS health-related:
    - For definition-based health questions (e.g., "What is fever?", "Explain jaundice", "What is diabetes?"), respond using Markdown format with these sections:
      ## Overview
      ## Possible Causes (if applicable)
      ## Symptoms (if applicable)
      ## Treatments or Home Tips
      ## When to See a Doctor
    - For advice or action-based questions, use bullet points and clear formatting.
    - For all, do not merge sections or add extra commentary outside the specified sections.
- Never reply with generic statements like 'I'm ready to answer your health-related questions.' Always provide a direct, informative answer or the refusal message above.
"""
            try:
                raw_response = model.generate_content(prompt).text
                print("RAW RESPONSE:", raw_response)  # For debugging
                clean_response = raw_response.strip()
                def extract_bullets_after_symptoms(text):
                    # Find the heading containing 'Symptoms' (case-insensitive)
                    heading_match = re.search(r'(Symptoms[\w\s]*:?\n)([\s\S]+)', text, re.IGNORECASE)
                    if heading_match:
                        after_heading = heading_match.group(2)
                        bullets = re.findall(r"[-•] .+", after_heading)
                        if bullets:
                            return '\n'.join(bullets)
                    # Fallback: first bulleted list in the whole response
                    bullets = re.findall(r"[-•] .+", text)
                    return '\n'.join(bullets) if bullets else None
                def extract_bullets(text):
                    bullets = re.findall(r"[-•] .+", text)
                    return '\n'.join(bullets) if bullets else None
                if postprocess_type == 'symptoms':
                    bullets = extract_bullets_after_symptoms(raw_response)
                    if bullets:
                        clean_response = bullets
                    else:
                        clean_response = "❌ Sorry, I could not extract a clean list of symptoms."
                elif postprocess_type == 'treatment':
                    bullets = extract_bullets(raw_response)
                    if bullets:
                        clean_response = bullets
                    else:
                        clean_response = "❌ Sorry, I could not extract a clean list of treatments."
                elif postprocess_type == 'action':
                    bullets = extract_bullets(raw_response)
                    if bullets:
                        clean_response = bullets
                    else:
                        clean_response = "❌ Sorry, I could not extract a clean list of actions."
                # else: definition/general info, show as-is
                response = Markup(markdown2.markdown(clean_response))
                # Save AI's response to GeneralHealthChat if user is logged in
                if current_user.is_authenticated:
                    try:
                        ai_chat = GeneralHealthChat(
                            user_id=current_user.id,
                            message=f"AI: {raw_response}",
                            timestamp=datetime.now(IST)
                        )
                        db.session.add(ai_chat)
                        db.session.commit()
                    except Exception as e:
                        print(f"Error saving AI response: {e}")
            except Exception as e:
                error = f"⚠️ Error: {str(e)}"

    # Get chat history for the current user
    chat_history = GeneralHealthChat.query.filter_by(user_id=current_user.id).order_by(GeneralHealthChat.timestamp).all() if current_user.is_authenticated else []
    for chat in chat_history:
        if hasattr(chat.timestamp, 'astimezone'):
            chat.timestamp = chat.timestamp.astimezone(IST)
        else:
            chat.timestamp = chat.timestamp.replace(tzinfo=pytz.utc).astimezone(IST)

    return render_template("health_chat.html", response=response, error=error, chat_history=chat_history)

@app.route('/emergency')
def emergency():
    return render_template("emergency.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        if not name or not email or not password:
            flash('Invalid Input', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        user = User(name=name, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            if user.is_blocked:
                flash('Your account has been blocked. Please contact support.', 'danger')
                return redirect(url_for('login'))
            login_user(user, remember=True)
            # Record login history
            login_event = LoginHistory(user_id=user.id, timestamp=datetime.now(IST))
            db.session.add(login_event)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # Only update if email is not taken by another user
        if email != current_user.email and User.query.filter_by(email=email).first():
            flash('Email already in use.', 'danger')
            return redirect(url_for('edit_profile'))
        current_user.name = name
        current_user.email = email
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=current_user)

@app.route('/bmi', methods=['GET', 'POST'])
@login_required
def bmi_calculator():
    response = ""
    if request.method == 'POST':
        weight = request.form.get('weight', '')
        height = request.form.get('height', '')
        age = request.form.get('age', '')
        gender = request.form.get('gender', '')

        # Save user's input to BMICalculatorChat if user is logged in
        if current_user.is_authenticated:
            try:
                user_input = f"User: Weight: {weight}kg, Height: {height}cm, Age: {age}, Gender: {gender}"
                user_chat = BMICalculatorChat(
                    user_id=current_user.id,
                    message=user_input,
                    timestamp=datetime.now(IST)
                )
                db.session.add(user_chat)
                db.session.commit()
            except Exception as e:
                print(f"Error saving user message: {e}")

        try:
            weight = float(weight)
            height = float(height) / 100  # Convert cm to m
            bmi = weight / (height * height)
            bmi = round(bmi, 1)

            # Determine BMI category
            if bmi < 18.5:
                category = "Underweight"
                advice = "Consider consulting a healthcare provider about healthy ways to gain weight."
            elif bmi < 25:
                category = "Normal weight"
                advice = "Maintain your current healthy lifestyle."
            elif bmi < 30:
                category = "Overweight"
                advice = "Consider consulting a healthcare provider about healthy ways to lose weight."
            else:
                category = "Obese"
                advice = "It's recommended to consult a healthcare provider about weight management."

            # Only show the BMI result, not categories or notes
            response = f"""
## Your BMI Results
- BMI: {bmi}
- Category: {category}
- Advice: {advice}
"""
            # Save AI response to BMICalculatorChat
            if current_user.is_authenticated:
                try:
                    ai_chat = BMICalculatorChat(
                        user_id=current_user.id,
                        message=f"AI: {response}",
                        timestamp=datetime.now(IST)
                    )
                    db.session.add(ai_chat)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving AI response: {e}")
        except ValueError:
            response = "❌ Please enter valid numbers for weight and height."
        except ZeroDivisionError:
            response = "❌ Height cannot be zero."
    # Fetch chat history after saving both user and AI messages
    chat_history = BMICalculatorChat.query.filter_by(user_id=current_user.id).order_by(BMICalculatorChat.timestamp.asc()).all() if current_user.is_authenticated else []
    for chat in chat_history:
        if hasattr(chat.timestamp, 'astimezone'):
            chat.timestamp = chat.timestamp.astimezone(IST)
        else:
            chat.timestamp = chat.timestamp.replace(tzinfo=pytz.utc).astimezone(IST)
    return render_template("bmi_calculator.html", response=response, chat_history=chat_history)

@app.route('/medicine', methods=['GET', 'POST'])
@login_required
def medicine_identifier():
    response = ""
    medicine_name = usage = dosage = side_effects = None
    filename = None
    debug_info = ""
    if request.method == 'POST':
        if 'photo' not in request.files:
            response = "❌ No file part."
        else:
            file = request.files['photo']
            if file.filename == '':
                response = "❌ No selected file."
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                try:
                    with open(filepath, 'rb') as img_file:
                        img_bytes = img_file.read()
                    mime_type, _ = mimetypes.guess_type(filepath)
                    if not mime_type:
                        mime_type = 'image/jpeg'
                    vision_prompt = (
                        "You are a medical assistant. Analyze the following image of a medicine package or strip. "
                        "Read any visible text or label. If you can identify the medicine, provide the following sections in Markdown (with headings):\n"
                        "## Name\n## Usage\n## Dosage\n## Common Side Effects\n"
                        "If you cannot identify, reply exactly with: '❌ Unable to identify the medicine from the photo.'\n"
                        "Always use clear Markdown formatting."
                    )
                    gemini_input = [
                        {"text": vision_prompt},
                        {"mime_type": mime_type, "data": img_bytes}
                    ]
                    try:
                        vision_response = model.generate_content(gemini_input).text.strip()
                    except Exception as e:
                        vision_response = ''
                        debug_info += f"<div style='color:red'><b>Gemini error:</b> {str(e)}</div>"
                    debug_info += f"<div style='color:gray'><b>Gemini Response:</b> {vision_response if vision_response else '[None]'}</div>"
                    if vision_response and vision_response.strip() != '❌ Unable to identify the medicine from the photo.':
                        # Remove 'Gemini Response:' prefix if present
                        vision_response = re.sub(r'^Gemini Response:\s*', '', vision_response, flags=re.IGNORECASE)
                        # Extract sections using regex
                        def extract_section(section):
                            m = re.search(rf'## {section}(.+?)(?=## |$)', vision_response, re.DOTALL | re.IGNORECASE)
                            return m.group(1).strip() if m else 'Not available'
                        medicine_name = extract_section('Name')
                        usage = extract_section('Usage')
                        dosage = extract_section('Dosage')
                        side_effects = extract_section('Common Side Effects')
                    else:
                        response = Markup(debug_info + '<div class="text-danger fw-bold">❌ Unable to identify the medicine from the photo.</div>')
                except Exception as e:
                    response = f"⚠️ Error: {str(e)}"
            else:
                response = "❌ Invalid file type. Only PNG, JPG, JPEG allowed."
    return render_template('medicine_upload.html', response=response, filename=filename, medicine_name=medicine_name, usage=usage, dosage=dosage, side_effects=side_effects)

@app.route('/exercise')
@login_required
def exercise_page():
    # Updated exercise data with structured levels
    exercises = [
        # Common Exercises
        {
            'title': 'Jumping Jacks',
            'category': 'common',
            'level': 'Beginner',
            'duration': 30,
            'rest': 10,
            'image': 'https://example.com/jumping_jacks.jpg',
            'video': 'https://www.youtube.com/embed/2W4ZNSwoW_4',
            'explanation': 'Jumping jacks are a classic full-body warm-up. They increase your heart rate, boost circulation, and improve coordination. Great for getting your body ready for exercise.',
            'purpose': 'Cardio and coordination'
        },
        {
            'title': 'Push-ups',
            'category': 'common',
            'level': 'Beginner',
            'duration': 45,
            'rest': 15,
            'image': 'https://example.com/push_ups.jpg',
            'video': 'https://www.youtube.com/embed/_l3ySVKYVJ8',
            'explanation': 'Push-ups strengthen your chest, shoulders, and triceps. They help build upper body strength and improve core stability. Maintain a straight line from head to heels.',
            'purpose': 'Upper body strength'
        },
        {
            'title': 'Squats',
            'category': 'common',
            'level': 'Beginner',
            'duration': 40,
            'rest': 20,
            'image': 'https://example.com/squats.jpg',
            'video': 'https://www.youtube.com/embed/aclHkVaku9U',
            'explanation': 'Squats target your thighs, hips, and glutes. They help build lower body strength and improve balance. Keep your chest up and knees behind your toes.',
            'purpose': 'Lower body strength'
        },
        {
            'title': 'Plank',
            'category': 'common',
            'level': 'Intermediate',
            'duration': 60,
            'rest': 30,
            'image': 'https://example.com/plank.jpg',
            'video': 'https://www.youtube.com/embed/pSHjTRCQxIw',
            'explanation': 'The plank is a core-strengthening exercise. It improves posture and stability. Hold your body in a straight line, engaging your abs and glutes.',
            'purpose': 'Core stability'
        },
        {
            'title': 'Lunges',
            'category': 'common',
            'level': 'Intermediate',
            'duration': 50,
            'rest': 25,
            'image': 'https://example.com/lunges.jpg',
            'video': 'https://www.youtube.com/embed/QOVaHwm-Q6U',
            'explanation': 'Lunges work your legs and glutes while improving balance. Step forward and lower your hips until both knees are bent at 90 degrees. Alternate legs for each rep.',
            'purpose': 'Lower body strength'
        },
        {
            'title': 'Mountain Climbers',
            'category': 'common',
            'level': 'Advanced',
            'duration': 55,
            'rest': 20,
            'image': 'https://example.com/mountain_climbers.jpg',
            'video': 'https://www.youtube.com/embed/cnyTQDSE884',
            'explanation': 'Mountain climbers are a dynamic, high-intensity move. They target your core, shoulders, and legs. Perform quickly for a cardio and strength challenge.',
            'purpose': 'Cardio and core'
        },
        {
            'title': 'Burpees',
            'category': 'common',
            'level': 'Advanced',
            'duration': 70,
            'rest': 40,
            'image': 'https://example.com/burpees.jpg',
            'video': 'https://www.youtube.com/embed/dZgVxmf6jkA',
            'explanation': 'Burpees combine a squat, push-up, and jump. They provide a full-body workout, boosting strength and endurance. Perform with control for best results.',
            'purpose': 'Full body workout'
        },
        # Muscle Building Exercises
        {
            'title': 'Knee Push-ups',
            'category': 'muscle',
            'level': 'Beginner',
            'duration': 45,
            'rest': 20,
            'image': 'https://example.com/knee_push_ups.jpg',
            'video': 'https://www.youtube.com/embed/WcHtt6zT3Go',
            'explanation': 'Knee push-ups are a beginner-friendly push-up variation. They help build upper body strength while reducing strain. Keep your core tight and back straight.',
            'purpose': 'Upper body strength'
        },
        {
            'title': 'Push-ups',
            'category': 'muscle',
            'level': 'Beginner',
            'duration': 50,
            'rest': 25,
            'image': 'https://example.com/push_ups.jpg',
            'video': 'https://www.youtube.com/embed/WDIpL0pjun0',
            'explanation': 'Push-ups are a classic bodyweight exercise for the chest, shoulders, and triceps. Maintain a plank position and lower your body with control. Great for building upper body strength.',
            'purpose': 'Upper body strength'
        },
        {
            'title': 'Deadlifts',
            'category': 'muscle',
            'level': 'Beginner',
            'duration': 50,
            'rest': 25,
            'image': 'https://example.com/deadlifts.jpg',
            'video': 'https://www.youtube.com/embed/op9kVnSso6Q',
            'explanation': 'Deadlifts target your back, glutes, and legs. They build total-body strength and improve posture. Use proper form to protect your lower back.',
            'purpose': 'Full body strength'
        },
        {
            'title': 'Leg Press',
            'category': 'muscle',
            'level': 'Beginner',
            'duration': 40,
            'rest': 15,
            'image': 'https://example.com/leg_press.jpg',
            'video': 'https://www.youtube.com/embed/IZxyjW7MPJQ',
            'explanation': 'The leg press isolates your quadriceps and hamstrings. It helps build lower body strength safely. Adjust the seat and foot position for comfort.',
            'purpose': 'Lower body strength'
        },
        {
            'title': 'Overhead Press',
            'category': 'muscle',
            'level': 'Intermediate',
            'duration': 55,
            'rest': 30,
            'image': 'https://example.com/overhead_press.jpg',
            'video': 'https://www.youtube.com/embed/B-aVuyhvLHU',
            'explanation': 'The overhead press targets your shoulders and triceps. Press the weight overhead while keeping your core engaged. Improves upper body power and stability.',
            'purpose': 'Upper body strength'
        },
        {
            'title': 'Barbell Rows',
            'category': 'muscle',
            'level': 'Intermediate',
            'duration': 60,
            'rest': 35,
            'image': 'https://example.com/barbell_rows.jpg',
            'video': 'https://www.youtube.com/embed/vT2GjY_Umpw',
            'explanation': 'Barbell rows strengthen your back and biceps. Pull the bar toward your torso while keeping your back flat. Great for building a strong upper back.',
            'purpose': 'Upper body strength'
        },
        {
            'title': 'Pull-ups',
            'category': 'muscle',
            'level': 'Advanced',
            'duration': 70,
            'rest': 45,
            'image': 'https://example.com/pull_ups.jpg',
            'video': 'https://www.youtube.com/embed/eGo4IYlbE5g',
            'explanation': 'Pull-ups are a challenging upper body exercise. They target your back, biceps, and shoulders. Use a full range of motion for best results.',
            'purpose': 'Upper body strength'
        },
        {
            'title': 'Diamond Push-ups',
            'category': 'muscle',
            'level': 'Advanced',
            'duration': 75,
            'rest': 45,
            'image': 'https://example.com/diamond_push_ups.jpg',
            'video': 'https://www.youtube.com/embed/J0DnG1_S92I',
            'explanation': 'Diamond push-ups emphasize your triceps and inner chest. Place your hands close together under your chest. Maintain a straight body line throughout.',
            'purpose': 'Upper body strength'
        },
        # Yoga Exercises (7 home-based, all working videos)
        {
            'title': "Child's Pose",
            'category': 'yoga',
            'level': 'Beginner',
            'duration': 30,
            'rest': 10,
            'image': 'https://example.com/childs_pose.jpg',
            'video': 'https://www.youtube.com/embed/4ZpkRAcgws4',
            'explanation': "Child's Pose is a gentle resting posture. It stretches the back and hips while calming the mind. Use it to relax between more active poses.",
            'purpose': 'Flexibility and relaxation'
        },
        {
            'title': 'Downward Dog',
            'category': 'yoga',
            'level': 'Beginner',
            'duration': 45,
            'rest': 15,
            'image': 'https://example.com/downward_dog.jpg',
            'video': 'https://www.youtube.com/embed/v7AYKMP6rOE',
            'explanation': 'Downward Dog strengthens your arms and legs while stretching your back. It energizes the body and improves flexibility. Press your heels toward the floor.',
            'purpose': 'Strength and flexibility'
        },
        {
            'title': 'Cat-Cow',
            'category': 'yoga',
            'level': 'Beginner',
            'duration': 40,
            'rest': 15,
            'image': 'https://example.com/cat_cow.jpg',
            'video': 'https://www.youtube.com/embed/kqnua4rHVVA',
            'explanation': 'Cat-Cow is a gentle flow between two poses. It warms up the spine and relieves back tension. Move slowly and match your breath to the movement.',
            'purpose': 'Spinal flexibility'
        },
        {
            'title': 'Seated Forward Bend',
            'category': 'yoga',
            'level': 'Intermediate',
            'duration': 40,
            'rest': 15,
            'image': 'https://example.com/seated_forward_bend.jpg',
            'video': 'https://www.youtube.com/embed/8VwufJrUhic',
            'explanation': 'Seated Forward Bend stretches your spine and hamstrings. It calms the mind and relieves stress. Reach forward gently, keeping your back long.',
            'purpose': 'Flexibility and calm'
        },
        {
            'title': 'Standing Side Stretch',
            'category': 'yoga',
            'level': 'Intermediate',
            'duration': 50,
            'rest': 25,
            'image': 'https://example.com/standing_side_stretch.jpg',
            'video': 'https://www.youtube.com/embed/4pKly2JojMw',
            'explanation': 'Standing Side Stretch lengthens the sides of your body. It wakes up the spine and improves flexibility. Breathe deeply as you reach overhead.',
            'purpose': 'Flexibility and energy'
        },
        {
            'title': 'Reclined Butterfly Pose',
            'category': 'yoga',
            'level': 'Intermediate',
            'duration': 45,
            'rest': 20,
            'image': 'https://example.com/reclined_butterfly_pose.jpg',
            'video': 'https://www.youtube.com/embed/4ZpkRAcgws4',
            'explanation': 'Reclined Butterfly Pose opens the hips and relaxes the body. Let your knees fall out to the sides and focus on deep breathing. Perfect for winding down.',
            'purpose': 'Relaxation and hip opening'
        },
        {
            'title': 'Savasana (Corpse Pose)',
            'category': 'yoga',
            'level': 'Advanced',
            'duration': 40,
            'rest': 20,
            'image': 'https://example.com/savasana.jpg',
            'video': 'https://www.youtube.com/embed/8VwufJrUhic',
            'explanation': 'Savasana is a restorative pose for deep relaxation. Lie flat, close your eyes, and let your body absorb the benefits of your practice. Stay still and breathe naturally.',
            'purpose': 'Relaxation and integration'
        },
        # END OF YOGA EXERCISES - REMOVE ANY FURTHER YOGA ENTRIES
    ]
    return render_template('exercise.html', exercises=exercises)

@app.route('/diet_tips_chat', methods=['GET', 'POST'])
@login_required
def diet_tips_chat():
    response = ""
    error = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if not question:
            error = "❌ Please enter a question."
        else:
            # Save user's question to chat history if user is logged in
            if current_user.is_authenticated:
                try:
                    user_chat = ChatHistory(
                        user_id=current_user.id,
                        section='diet_tips',
                        message=f"User: {question}",
                        timestamp=datetime.now(IST)
                    )
                    db.session.add(user_chat)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving user message: {e}")

            prompt = f"""
You are a diet-focused AI assistant. Only respond to diet-related queries (nutrition, meal planning, dietary advice).

The user asked: "{question}"

Instructions:
- Use clear, structured Markdown formatting.
- Use bold section headers (##) for each section: Overview, Foods to Include, Foods to Avoid, Sample Diet Plan, Important Considerations.
- Use bullet points for lists.
- For the sample meal plan, you MUST use a point-by-point format, with each meal and foods on a new line, like this:
  - Breakfast: 3 eggs, 1 toast, 1 glass of milk
  - Lunch: Grilled chicken, brown rice, salad
  - Snack: 1 apple, handful of nuts
  - Dinner: Fish curry, steamed vegetables
- Do NOT use a table for the sample meal plan.
- Place any additional notes (hydration, portion control, gradual changes, family involvement, professional guidance, etc.) in a clearly separated 'Important Considerations' section BELOW the plan, using bullet points.
- Ensure each section (Overview, Foods to Include, Foods to Avoid, Sample Diet Plan, Important Considerations) is clearly separated and formatted.
- Adjust calories, protein, and food types based on age, weight, height, activity, and goal.
- Respect dietary preference (e.g., vegan, vegetarian, etc.) in all food suggestions.
- If the user is a child (age < 13) and low weight and sedentary, suggest a light, balanced diet.
- If the user is an adult (age 20-64) with high weight and active, suggest a protein-rich, higher-calorie diet.
- If the user is a senior (age 65+) with diabetes or similar goal, suggest low-sugar, diabetic-safe meals.
- Always provide a sample meal plan for a day, using only foods that fit the dietary preference.
- If you do not provide a plan in the correct format, the user will see a default plan instead.

## Overview
## Foods to Include
## Foods to Avoid
## Sample Diet Plan

- Breakfast: 
- Lunch: 
- Snack: 
- Dinner: 

## Important Considerations
- 

Be specific and do not repeat content.
"""

            try:
                raw_response = model.generate_content(prompt).text
                response = Markup(markdown2.markdown(raw_response))
            except Exception as e:
                response = f"⚠️ Error: {str(e)}"
    # Fetch only Diet Tips chat history for this user
    chat_history = ChatHistory.query.filter_by(user_id=current_user.id, section='diet_tips').order_by(ChatHistory.timestamp.asc()).all()
    return render_template('section_chat.html', user=current_user, chat_history=chat_history, section_title='Diet Tips')

@app.route('/symptoms_chat', methods=['GET', 'POST'])
@login_required
def symptoms_chat():
    response = ""
    error = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if not question:
            error = "❌ Please enter a question."
        else:
            if current_user.is_authenticated:
                try:
                    user_chat = ChatHistory(
                        user_id=current_user.id,
                        section='symptoms',
                        message=f"User: {question}",
                        timestamp=datetime.now(IST)
                    )
                    db.session.add(user_chat)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving user message: {e}")

            prompt = f"""
You are a symptom-focused AI assistant. Only respond to symptom-related queries (disease symptoms, health conditions).

The user asked: "{question}"

Instructions:
- Use clear, structured Markdown formatting.
- Use bold section headers (##) for each section: Overview, Possible Causes, Symptoms, Treatments or Home Tips, When to See a Doctor.
- Use bullet points for lists.
- For all, do not merge sections or add extra commentary outside the specified sections.
- Ensure each section is clearly separated and formatted.
- If symptoms are mild, short duration, and user is young, suggest home remedies and rest.
- If symptoms are severe, long duration, or user is elderly, suggest urgent medical attention.
- If the user is female and has a headache for many days, analyze for migraines, stress, or other causes.
- Always start with a disclaimer that this is informational only.

## Disclaimer
## Possible Causes
## Symptoms
## Treatments or Home Tips
## When to See a Doctor

Be specific and do not repeat content.
"""

            try:
                raw_response = model.generate_content(prompt).text
                response = Markup(markdown2.markdown(raw_response))
            except Exception as e:
                response = f"⚠️ Error: {str(e)}"
    # Fetch only Symptoms chat history for this user
    chat_history = ChatHistory.query.filter_by(user_id=current_user.id, section='symptoms').order_by(ChatHistory.timestamp.asc()).all()
    return render_template('section_chat.html', user=current_user, chat_history=chat_history, section_title='Symptoms')

@app.route('/general_health_chat', methods=['GET', 'POST'])
@login_required
def general_health_chat():
    response = ""
    error = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if not question:
            error = "❌ Please enter a question."
        else:
            if current_user.is_authenticated:
                try:
                    user_chat = ChatHistory(
                        user_id=current_user.id,
                        section='general_health',
                        message=f"User: {question}",
                        timestamp=datetime.now(IST)
                    )
                    db.session.add(user_chat)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving user message: {e}")

            prompt = f"""
You are a general health-focused AI assistant. Only respond to general health-related queries.

The user asked: "{question}"

Instructions:
- Use clear, structured Markdown formatting.
- Use bold section headers (##) for each section: Overview, Possible Causes, Symptoms, Treatments or Home Tips, When to See a Doctor.
- Use bullet points for lists.
- For all, do not merge sections or add extra commentary outside the specified sections.
- Ensure each section is clearly separated and formatted.
- If symptoms are mild, short duration, and user is young, suggest home remedies and rest.
- If symptoms are severe, long duration, or user is elderly, suggest urgent medical attention.
- If the user is female and has a headache for many days, analyze for migraines, stress, or other causes.
- Always start with a disclaimer that this is informational only.

## Disclaimer
## Possible Causes
## Symptoms
## Treatments or Home Tips
## When to See a Doctor

Be specific and do not repeat content.
"""

            try:
                raw_response = model.generate_content(prompt).text
                response = Markup(markdown2.markdown(raw_response))
            except Exception as e:
                response = f"⚠️ Error: {str(e)}"
    # Fetch only General Health chat history for this user
    chat_history = ChatHistory.query.filter_by(user_id=current_user.id, section='general_health').order_by(ChatHistory.timestamp.asc()).all()
    return render_template('section_chat.html', user=current_user, chat_history=chat_history, section_title='General Health')

@app.route('/bmi_chat', methods=['GET', 'POST'])
@login_required
def bmi_chat():
    response = ""
    error = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if not question:
            error = "❌ Please enter a question."
        else:
            if current_user.is_authenticated:
                try:
                    user_chat = ChatHistory(
                        user_id=current_user.id,
                        section='bmi',
                        message=f"User: {question}",
                        timestamp=datetime.now(IST)
                    )
                    db.session.add(user_chat)
                    db.session.commit()
                except Exception as e:
                    print(f"Error saving user message: {e}")

            prompt = f"""
You are a BMI-focused AI assistant. Only respond to BMI-related queries (weight management, body composition).

The user asked: "{question}"

Instructions:
- Use clear, structured Markdown formatting.
- Use bold section headers (##) for each section: Overview, BMI Calculation, BMI Status, Recommended Actions.
- Use bullet points for lists.
- For BMI Calculation, use the formula: BMI = weight (kg) / (height (m) ^ 2).
- For BMI Status, use the following categories:
  - Underweight: BMI < 18.5
  - Normal weight: 18.5 <= BMI < 25
  - Overweight: 25 <= BMI < 30
  - Obesity: BMI >= 30
- For Recommended Actions, suggest healthy lifestyle changes based on the BMI status.

## Disclaimer
## BMI Calculation
## BMI Status
## Recommended Actions

Be specific and do not repeat content.
"""

            try:
                raw_response = model.generate_content(prompt).text
                response = Markup(markdown2.markdown(raw_response))
            except Exception as e:
                response = f"⚠️ Error: {str(e)}"
    # Fetch only BMI chat history for this user
    chat_history = ChatHistory.query.filter_by(user_id=current_user.id, section='bmi').order_by(ChatHistory.timestamp.asc()).all()
    return render_template('section_chat.html', user=current_user, chat_history=chat_history, section_title='BMI')

@app.route('/clear_chat_history', methods=['POST'])
@login_required
def clear_chat_history():
    section = request.form.get('section')
    if section:
        try:
            if section == 'symptom_checker':
                SymptomCheckerChat.query.filter_by(user_id=current_user.id).delete()
                db.session.commit()
                flash(f"Chat history for Symptom Checker has been cleared.", "success")
                return redirect(url_for('symptom_checker'))
            elif section == 'diet_tips':
                DietTipsChat.query.filter_by(user_id=current_user.id).delete()
                db.session.commit()
                flash(f"Chat history for Diet Tips has been cleared.", "success")
                return redirect(url_for('diet_tips'))
            elif section == 'general_health':
                GeneralHealthChat.query.filter_by(user_id=current_user.id).delete()
                db.session.commit()
                flash(f"Chat history for General Health has been cleared.", "success")
                return redirect(url_for('health_chat'))
            elif section == 'bmi_calculator':
                BMICalculatorChat.query.filter_by(user_id=current_user.id).delete()
                db.session.commit()
                flash(f"Chat history for BMI Calculator has been cleared.", "success")
                return redirect(url_for('bmi_calculator'))
            # Add more elifs for other new tables if needed
        except Exception as e:
            db.session.rollback()
            flash("Failed to clear chat history. Please try again.", "danger")
    else:
        flash("Invalid section specified.", "danger")
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin_dashboard():
    print(f"🔍 Admin Dashboard Access - User: {current_user.email}, Is Admin: {current_user.is_admin}, Is Superuser: {current_user.is_superuser}")
    
    if not (current_user.is_admin or current_user.is_superuser):
        print(f"❌ Access denied - User {current_user.email} is not admin")
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('home'))
    
    try:
        users = User.query.all()
        total_users = User.query.count()
        print(f"📊 Found {total_users} users")
        
        chat_histories = {}
        exercise_histories = {}
        pill_reminders = {}
        for user in users:
            print(f"👤 Processing user: {user.name} (ID: {user.id})")
            
            # Get chat histories
            blood_donor_chats = BloodDonorChat.query.filter_by(user_id=user.id).order_by(BloodDonorChat.timestamp.asc()).all()
            chat_histories[user.id] = {
                'general_health': GeneralHealthChat.query.filter_by(user_id=user.id).order_by(GeneralHealthChat.timestamp.asc()).all(),
                'diet_tips': DietTipsChat.query.filter_by(user_id=user.id).order_by(DietTipsChat.timestamp.asc()).all(),
                'symptom_checker': SymptomCheckerChat.query.filter_by(user_id=user.id).order_by(SymptomCheckerChat.timestamp.asc()).all(),
                'bmi_calculator': BMICalculatorChat.query.filter_by(user_id=user.id).order_by(BMICalculatorChat.timestamp.asc()).all(),
                'blood_donor': blood_donor_chats,
            }
            
            # Get exercise history
            exercise_histories[user.id] = ExerciseHistory.query.filter_by(user_id=user.id).order_by(ExerciseHistory.timestamp.desc()).all()
            print(f"   📈 Exercise records: {len(exercise_histories[user.id])}")
            
            # Get pill reminders
            pill_reminders[user.id] = PillReminder.query.filter_by(user_id=user.id).order_by(PillReminder.created_at.desc()).all()
            print(f"   💊 Pill reminders: {len(pill_reminders[user.id])}")
        
        # Get login histories
        login_histories = {}
        for user in users:
            logins = LoginHistory.query.filter_by(user_id=user.id).order_by(LoginHistory.timestamp.asc()).all()
            login_histories[user.id] = logins
        
        # Get blood donors
        blood_donors = BloodDonor.query.all()
        blood_donor_registration = {user.id: BloodDonor.query.filter_by(name=user.name).first() for user in users}
        
        # Get all pill reminders for debug
        all_pill_reminders = PillReminder.query.order_by(PillReminder.created_at.desc()).all()
        
        print(f"✅ Admin dashboard data prepared successfully")
        print(f"   Users: {len(users)}")
        print(f"   Blood donors: {len(blood_donors)}")
        
        return render_template('admin_dashboard.html', 
                             users=users, 
                             total_users=total_users, 
                             chat_histories=chat_histories, 
                             login_histories=login_histories, 
                             blood_donors=blood_donors, 
                             blood_donor_registration=blood_donor_registration, 
                             exercise_histories=exercise_histories,
                             pill_reminders=pill_reminders,
                             all_pill_reminders=all_pill_reminders)
    
    except Exception as e:
        print(f"❌ Error in admin dashboard: {e}")
        flash(f'Error loading admin dashboard: {str(e)}', 'danger')
        return redirect(url_for('home'))

@app.route('/admin/block/<int:user_id>', methods=['POST'])
@login_required
def block_user(user_id):
    if not (current_user.is_admin or current_user.is_superuser):
        abort(403)
    if user_id == current_user.id:
        flash('You cannot block your own admin account.', 'danger')
        return redirect(url_for('admin_dashboard'))
    user = User.query.get_or_404(user_id)
    user.is_blocked = True
    db.session.commit()
    flash(f'User {user.name} has been blocked.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/unblock/<int:user_id>', methods=['POST'])
@login_required
def unblock_user(user_id):
    if not (current_user.is_admin or current_user.is_superuser):
        abort(403)
    user = User.query.get_or_404(user_id)
    user.is_blocked = False
    db.session.commit()
    flash(f'User {user.name} has been unblocked.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not (current_user.is_admin or current_user.is_superuser):
        abort(403)
    if user_id == current_user.id:
        flash('You cannot delete your own admin account.', 'danger')
        return redirect(url_for('admin_dashboard'))
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.name} has been deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_user', methods=['POST'])
@login_required
def add_user():
    if not (current_user.is_admin or current_user.is_superuser):
        abort(403)
    
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        is_admin = request.form.get('is_admin') == 'on'
        
        # Validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('A user with this email already exists.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        # Create new user
        new_user = User(
            name=name,
            email=email,
            is_admin=is_admin,
            is_superuser=False,  # Only superusers can create other superusers
            is_blocked=False
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        admin_status = "admin" if is_admin else "regular user"
        flash(f'User {name} has been created successfully as a {admin_status}.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating user: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/promote_user', methods=['POST'])
@login_required
def promote_user():
    if not (current_user.is_admin or current_user.is_superuser):
        abort(403)
    
    try:
        user_email = request.form.get('user_email', '').strip()
        
        if not user_email:
            flash('Please select a user to promote.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        # Find the user
        user = User.query.filter_by(email=user_email).first()
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        # Check if user is already an admin
        if user.is_admin:
            flash(f'User {user.name} is already an admin.', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        # Promote to admin
        user.is_admin = True
        db.session.commit()
        
        flash(f'User {user.name} has been promoted to admin successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error promoting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/promote_user_admin/<int:user_id>', methods=['POST'])
@login_required
def promote_user_admin(user_id):
    if not (current_user.is_admin or current_user.is_superuser):
        abort(403)
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Check if user is already an admin
        if user.is_admin:
            flash(f'User {user.name} is already an admin.', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        # Promote to admin
        user.is_admin = True
        db.session.commit()
        
        flash(f'User {user.name} has been promoted to admin successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error promoting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/demote_user/<int:user_id>', methods=['POST'])
@login_required
def demote_user(user_id):
    if not (current_user.is_admin or current_user.is_superuser):
        abort(403)
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Prevent demoting superusers
        if user.is_superuser:
            flash(f'Cannot demote superuser {user.name}.', 'danger')
            return redirect(url_for('admin_dashboard'))
        
        # Check if user is not an admin
        if not user.is_admin:
            flash(f'User {user.name} is not an admin.', 'warning')
            return redirect(url_for('admin_dashboard'))
        
        # Demote from admin
        user.is_admin = False
        db.session.commit()
        
        flash(f'User {user.name} has been demoted from admin successfully.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error demoting user: {str(e)}', 'danger')
    
    return redirect(url_for('admin_dashboard'))

@app.route('/blood_donor', methods=['GET', 'POST'])
@login_required
def blood_donor():
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    message = ''
    # Registration
    if request.method == 'POST' and 'register' in request.form:
        name = request.form.get('name', '').strip()
        blood_group = request.form.get('blood_group', '').strip()
        location = request.form.get('location', '').strip()
        contact = request.form.get('contact', '').strip()
        if name and blood_group and location and contact:
            donor = BloodDonor(name=name, blood_group=blood_group, location=location, contact=contact)
            db.session.add(donor)
            db.session.commit()
            message = 'Registration successful!'
        else:
            message = 'All fields are required.'
    elif request.method == 'POST' and 'donor_chat' in request.form and current_user.is_authenticated:
        chat_message = request.form.get('donor_chat_message', '').strip()
        if chat_message:
            from datetime import datetime
            try:
                print(f"Attempting to save BloodDonorChat: user_id={current_user.id}, message={chat_message}")
                chat = BloodDonorChat(
                    user_id=current_user.id,
                    message=f"User: {chat_message}",
                    timestamp=datetime.now(IST)
                )
                db.session.add(chat)
                db.session.commit()
                flash("Blood Donor chat message saved!", "success")
            except Exception as e:
                db.session.rollback()
                print(f"Error saving blood donor chat: {e}")
                flash(f"Error saving blood donor chat: {e}", "danger")
    # Search
    search_group = request.args.get('search_group', '')
    search_location = request.args.get('search_location', '')
    query = BloodDonor.query
    if search_group:
        query = query.filter_by(blood_group=search_group)
    if search_location:
        query = query.filter(BloodDonor.location.ilike(f'%{search_location}%'))
    donors = query.all() if (search_group or search_location) else []
    # Summary
    summary = {bg: BloodDonor.query.filter_by(blood_group=bg).count() for bg in blood_groups}
    # Blood Donor Chat History
    chat_history = BloodDonorChat.query.filter_by(user_id=current_user.id).order_by(BloodDonorChat.timestamp.asc()).all() if current_user.is_authenticated else []
    for chat in chat_history:
        if hasattr(chat.timestamp, 'astimezone'):
            chat.timestamp = chat.timestamp.astimezone(IST)
        else:
            chat.timestamp = chat.timestamp.replace(tzinfo=pytz.utc).astimezone(IST)
    return render_template('blood_donor.html', blood_groups=blood_groups, donors=donors, summary=summary, message=message, chat_history=chat_history)

@app.route('/pill_reminder', methods=['GET', 'POST'])
@login_required
def pill_reminder():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            pill_name = request.form.get('pill_name', '').strip()
            dosage = request.form.get('dosage', '').strip()
            frequency = request.form.get('frequency', '').strip()
            time_of_day = request.form.get('time_of_day', '').strip()
            exact_time_str = request.form.get('exact_time', '').strip()
            start_date_str = request.form.get('start_date', '').strip()
            end_date_str = request.form.get('end_date', '').strip()
            notes = request.form.get('notes', '').strip()
            
            exact_time = None
            if exact_time_str:
                try:
                    from datetime import time
                    h, m = map(int, exact_time_str.split(':'))
                    exact_time = time(h, m)
                except Exception:
                    exact_time = None
            
            # Only require one of time_of_day or exact_time
            if pill_name and dosage and frequency and start_date_str and (time_of_day or exact_time):
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = None
                    if end_date_str:
                        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    
                    reminder = PillReminder(
                        user_id=current_user.id,
                        pill_name=pill_name,
                        dosage=dosage,
                        frequency=frequency,
                        time_of_day=time_of_day if time_of_day else None,
                        exact_time=exact_time,
                        start_date=start_date,
                        end_date=end_date,
                        notes=notes,
                        is_active=True
                    )
                    db.session.add(reminder)
                    db.session.commit()
                    flash('Pill reminder added successfully!', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error adding reminder: {str(e)}', 'danger')
            else:
                flash('Please fill in all required fields, and set at least one time.', 'danger')
        
        elif action == 'delete':
            reminder_id = request.form.get('reminder_id')
            if reminder_id:
                try:
                    reminder = PillReminder.query.filter_by(id=reminder_id, user_id=current_user.id).first()
                    if reminder:
                        db.session.delete(reminder)
                        db.session.commit()
                        flash('Pill reminder deleted successfully!', 'success')
                    else:
                        flash('Reminder not found.', 'danger')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error deleting reminder: {str(e)}', 'danger')
        
        elif action == 'toggle':
            reminder_id = request.form.get('reminder_id')
            if reminder_id:
                try:
                    reminder = PillReminder.query.filter_by(id=reminder_id, user_id=current_user.id).first()
                    if reminder:
                        reminder.is_active = not reminder.is_active
                        db.session.commit()
                        status = 'activated' if reminder.is_active else 'deactivated'
                        flash(f'Pill reminder {status} successfully!', 'success')
                    else:
                        flash('Reminder not found.', 'danger')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Error updating reminder: {str(e)}', 'danger')
    
    # Get user's pill reminders
    reminders = PillReminder.query.filter_by(user_id=current_user.id).order_by(PillReminder.created_at.desc()).all()
    
    return render_template('pill_reminder.html', reminders=reminders)

@app.route('/log_exercise', methods=['POST'])
@login_required
def log_exercise():
    try:
        data = request.get_json(force=True)
        exercise_title = data.get('exercise_title', '').strip()
        duration = int(data.get('duration', 0))
        if exercise_title and duration > 0:
            exercise_history = ExerciseHistory(
                user_id=current_user.id,
                exercise_title=exercise_title,
                duration=duration,
                timestamp=datetime.now(IST)
            )
            db.session.add(exercise_history)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Exercise logged successfully!'})
        else:
            return jsonify({'success': False, 'error': 'Invalid exercise data'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Register markdown filter for Jinja2 using markdown2
@app.template_filter('markdown')
def markdown_filter(text):
    return Markup(markdown2.markdown(text))

if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
        app.run(debug=True)
    except Exception as e:
        print('ERROR: Unable to open or create the database file.')
        print('Details:', e)
        print('Suggestions:')
        print('- Make sure the instance directory exists and is writable.')
        print('- Make sure no other program is locking instance/users.db.')
        print('- Try deleting instance/users.db if it exists and is corrupted.')
        sys.exit(1)
