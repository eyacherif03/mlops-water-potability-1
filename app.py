from flask import Flask, request, jsonify
import joblib
import numpy as np
import mlflow.sklearn
import dagshub
import os

app = Flask(__name__)

dagshub.init(repo_owner='eyacherif03', repo_name='mlops-water-potability-1', mlflow=True)

# Charger le modèle depuis MLflow
model = mlflow.sklearn.load_model("models:/RandomForest/latest") \
    if os.getenv("LOAD_FROM_MLFLOW") else None

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    features = np.array(data["features"]).reshape(1, -1)
    prediction = model.predict(features)[0]
    return jsonify({"potable": int(prediction)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)