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
    app.run(debug=True, host='0.0.0.0', port=port)