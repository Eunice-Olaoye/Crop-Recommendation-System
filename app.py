from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------------------------------
# APP INITIALIZATION
# -------------------------------
app = Flask(__name__)

# Email configuration (use environment variables for security)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "yourgmail@gmail.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")  # Set this in environment
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "cephasict@gmail.com")

# -------------------------------
# MODEL LOADING (Centralized)
# -------------------------------
def load_artifacts():
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    try:
        model = joblib.load(os.path.join(base_path, 'crop_model.pkl'))
        encoder = joblib.load(os.path.join(base_path, 'label_encoder.pkl'))
        scaler = joblib.load(os.path.join(base_path, 'scaler.pkl'))
        return model, encoder, scaler
    except FileNotFoundError as e:
        print(f"Error loading model artifacts: {e}")
        raise

model, encoder, scaler = load_artifacts()

# -------------------------------
# ROUTES
# -------------------------------

@app.route('/')
def home():
    """
    Landing page – McKinsey-style solution overview
    """
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Handles crop prediction requests from frontend
    """
    try:
        # -------------------------------
        # 1. CAPTURE INPUT DATA
        # -------------------------------
        input_features = [
            float(request.form.get('N')),
            float(request.form.get('P')),
            float(request.form.get('K')),
            float(request.form.get('temperature')),
            float(request.form.get('humidity')),
            float(request.form.get('ph')),
            float(request.form.get('rainfall'))
        ]

        # -------------------------------
        # 2. VALIDATION CHECK
        # -------------------------------
        if None in input_features:
            return jsonify({
                "status": "error",
                "message": "Missing input values. Please fill all fields."
            }), 400

        # -------------------------------
        # 3. DATA PREPROCESSING
        # -------------------------------
        input_array = np.array([input_features])
        input_scaled = scaler.transform(input_array)

        # -------------------------------
        # 4. MODEL PREDICTION
        # -------------------------------
        prediction_encoded = model.predict(input_scaled)
        predicted_crop = encoder.inverse_transform(prediction_encoded)[0]

        # -------------------------------
        # 5. RESPONSE (Clean & Structured)
        # -------------------------------
        return jsonify({
            "status": "success",
            "prediction": str(predicted_crop).capitalize()
        })

    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": f"Invalid input type. Please enter numeric values. Error: {str(e)}"
        }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500

@app.route('/contact', methods=['POST'])
def contact():
    """
    Handles contact form submissions
    """
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Basic validation
        if not all([name, email, message]):
            return jsonify({
                "status": "error",
                "message": "Missing required fields (name, email, message)"
            }), 400

        # Check if email is configured
        if not SENDER_PASSWORD:
            return jsonify({
                "status": "error",
                "message": "Email service not configured. Please contact administrator."
            }), 500

        # Create HTML email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Crop Prediction Contact: {subject if subject else 'No Subject'}"
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        
        # Plain text version
        plain_text = f"""
Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""
        
        # HTML version (optional but nicer)
        html_text = f"""
        <html>
        <body>
            <h3>New Contact Form Submission</h3>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Subject:</strong> {subject or 'No Subject'}</p>
            <p><strong>Message:</strong></p>
            <p>{message}</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(plain_text, 'plain'))
        msg.attach(MIMEText(html_text, 'html'))

        # Send email
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        return jsonify({
            "status": "success",
            "message": "Message sent successfully!"
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to send message: {str(e)}"
        }), 500

# -------------------------------
# HEALTH CHECK ENDPOINT
# -------------------------------
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        "status": "healthy",
        "model_loaded": model is not None
    })

# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )