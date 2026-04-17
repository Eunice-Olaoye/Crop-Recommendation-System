<<<<<<< HEAD
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import os

# -------------------------------
# APP INITIALIZATION
# -------------------------------
app = Flask(__name__)

# -------------------------------
# MODEL LOADING (Centralized)
# -------------------------------
def load_artifacts():
    base_path = os.path.dirname(os.path.abspath(__file__))

    model = joblib.load(os.path.join(base_path, 'crop_model.pkl'))
    encoder = joblib.load(os.path.join(base_path, 'label_encoder.pkl'))
    scaler = joblib.load(os.path.join(base_path, 'scaler.pkl'))

    return model, encoder, scaler


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

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid input type. Please enter numeric values."
        }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500
    
    import smtplib
from email.mime.text import MIMEText

@app.route('/contact', methods=['POST'])
def contact():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Basic validation
        if not name or not email or not message:
            return "Missing required fields", 400

        full_message = f"""
Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""

        sender_email = "yourgmail@gmail.com"
        receiver_email = "cephasict@gmail.com"
        password = "your_app_password"

        msg = MIMEText(full_message)
        msg['Subject'] = subject if subject else "New Contact Message"
        msg['From'] = sender_email
        msg['To'] = receiver_email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, password)
            server.send_message(msg)

        return "Message sent successfully!"

    except Exception as e:
        return f"Error: {str(e)}", 500


# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
=======
from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import os

# -------------------------------
# APP INITIALIZATION
# -------------------------------
app = Flask(__name__)

# -------------------------------
# MODEL LOADING (Centralized)
# -------------------------------
def load_artifacts():
    base_path = os.path.dirname(os.path.abspath(__file__))

    model = joblib.load(os.path.join(base_path, 'crop_model.pkl'))
    encoder = joblib.load(os.path.join(base_path, 'label_encoder.pkl'))
    scaler = joblib.load(os.path.join(base_path, 'scaler.pkl'))

    return model, encoder, scaler


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

    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid input type. Please enter numeric values."
        }), 400

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }), 500


# -------------------------------
# RUN SERVER
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
>>>>>>> db0ad5c5e1558942e3ee9ec5284316850e5a7b3c
    app.run(debug=True, host='0.0.0.0', port=port)