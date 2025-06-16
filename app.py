from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import google.generativeai as genai
import markdown2
from markupsafe import Markup
from geopy.geocoders import Nominatim

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash-latest")

# Initialize Flask
app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/symptom', methods=['GET', 'POST'])
def symptom_checker():
    response = ""
    if request.method == 'POST':
        symptoms = request.form.get('symptoms', '')
        prompt = f"""
          
I have the following symptoms: {symptoms}.
Give possible causes using **Markdown** formatting.
Required structure:
## Disclaimer  
## Possible Causes  
### Viral Infections  
- Example  
### Bacterial Infections  
- Example  
## When to Seek Medical Help  
- Bullet points  
## Final Note  
Keep formatting clean and easy to read.
"""
        try:
            raw_response = model.generate_content(prompt).text
            response = Markup(markdown2.markdown(raw_response))
        except Exception as e:
            response = f"⚠️ Error: {str(e)}"
    return render_template("symptom_checker.html", response=response)

@app.route('/diet', methods=['GET', 'POST'])
def diet_tips():
    response = ""
    if request.method == 'POST':
        goal = request.form.get('goal', '')
        prompt = f"""
A user wants to improve their diet to achieve the goal: "{goal}".

Provide detailed, clear advice using this strict **Markdown** structure:
## Overview  
Briefly describe how diet helps with {goal}.

## Foods to Include  
- List healthy food categories and examples.

## Foods to Avoid  
- Mention food types to avoid and why.

## Sample Diet Plan  
- A full day's meal plan:  
  - Breakfast:  
  - Mid-morning Snack:  
  - Lunch:  
  - Evening Snack:  
  - Dinner:

Ensure consistency, use bullet points, and keep it beginner-friendly.
"""
        try:
            raw_response = model.generate_content(prompt).text
            response = Markup(markdown2.markdown(raw_response))
        except Exception as e:
            response = f"⚠️ Error: {str(e)}"
    return render_template("diet_tips.html", response=response)

@app.route('/chat', methods=['GET', 'POST'])
def health_chat():
    response = ""
    if request.method == 'POST':
        question = request.form.get('question', '').strip()

        # Keyword list (keep as is)
        health_keywords = [
            'health', 'medical', 'symptom', 'symptoms', 'disease', 'illness', 'pain',
            'doctor', 'hospital', 'medicine', 'medication', 'treatment', 'diagnosis',
            'prognosis', 'prescription', 'surgery', 'recovery', 'therapy',
            'vaccine', 'immunity', 'immune', 'prevention', 'rehabilitation',
            'diet', 'nutrition', 'food', 'fitness', 'exercise', 'weight', 'lifestyle',
            'fat', 'cholesterol', 'protein', 'carbs', 'calories',
            'mental', 'emotional', 'psychological', 'anxiety', 'depression', 'stress', 'sleep',
            'cold', 'fever', 'cough', 'headache', 'migraine', 'body pain', 'vomiting', 'nausea',
            'dizziness', 'chills', 'fatigue', 'sore throat', 'runny nose',
            'blood pressure', 'bp', 'diabetes', 'sugar', 'insulin', 'thyroid', 'heart',
            'asthma', 'breathing', 'lungs', 'liver', 'kidney', 'jaundice', 'skin',
            'rash', 'itching', 'acne', 'eczema', 'psoriasis',
            'infection', 'bacterial', 'viral', 'fungal', 'allergy', 'immune response',
            'cancer', 'tumor', 'ulcer', 'arthritis', 'bones', 'fracture', 'sprain', 'injury',
            'burn', 'wound', 'swelling', 'inflammation', 'constipation', 'diarrhea', 'gas',
            'acidity', 'indigestion', 'urine', 'stomach ache', 'menstrual', 'period', 'fertility',
            'pregnancy', 'reproductive', 'sexually', 'std', 'hormones', 'testosterone',
            'estrogen', 'puberty', 'aging', 'menopause',
            'checkup', 'lab', 'scan', 'report', 'result', 'x-ray', 'mri', 'ecg', 'ct scan'
        ]

        if not any(keyword in question.lower() for keyword in health_keywords):
            response = "❌ Sorry, I can only answer health-related questions. Please ask something related to health."
            return render_template("health_chat.html", response=response)

        # Choose prompt based on type of health query
        question_lower = question.lower()

        if any(phrase in question_lower for phrase in ["symptoms of", "what are the symptoms", "tell me the symptoms", "list symptoms"]):
            prompt = f"""
User asked: "{question}"
Provide only a list of symptoms using **Markdown** format.

## Symptoms  
- Bullet list of symptoms only.
- No extra content.
"""

        elif any(phrase in question_lower for phrase in ["treatment for", "how to treat", "remedy for", "cure for", "how can i treat"]):
            prompt = f"""
User asked: "{question}"
Provide only a list of treatments using **Markdown** format.

## Treatments  
- Bullet list of treatments only.
- No symptoms or explanations.
"""

        elif any(phrase in question_lower for phrase in ["i have", "i'm having", "what should i do", "i am experiencing", "i feel"]):
            prompt = f"""
The user asked: "{question}"

Act like a responsible and friendly medical assistant. Provide a clear, structured answer using **Markdown**.

Use this structure:
## Possible Causes  
- Bullet list  

## Immediate Home Care  
- Bullet list  

## When to See a Doctor  
- Bullet list

Ensure the tone is supportive and beginner-friendly. Avoid medical jargon.
"""

        else:
            prompt = f"""
Answer this general health question with a structured explanation using **Markdown**:

"{question}"

Use the following sections:
## Overview  
## Causes  
## Symptoms  
## Treatment  
## When to See a Doctor

Keep the language simple, helpful, and factual.
"""

        try:
            raw_response = model.generate_content(prompt).text
            response = Markup(markdown2.markdown(raw_response))
        except Exception as e:
            response = f"⚠️ Error: {str(e)}"

    return render_template("health_chat.html", response=response)

@app.route('/emergency')
def emergency():
    return render_template("emergency.html")

if __name__ == '__main__':
    app.run(debug=True)
