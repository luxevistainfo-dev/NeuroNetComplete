"""
Minimal ML worker prototype.
- Attempts to load a sklearn/pickle model from model.pkl in the working directory.
- Exposes a tiny Flask app with a /predict endpoint.
- If no model is available, returns a deterministic mock prediction.

This is a lightweight prototype and should be adapted with proper ML infra
(inference server, batching, GPU handling, health checks) for production.
"""
import os
import json
from flask import Flask, request, jsonify

try:
    import pickle
    import numpy as np
except Exception:
    pickle = None
    np = None

MODEL_PATH = os.environ.get("ML_MODEL_PATH", "model.pkl")

app = Flask(__name__)
model = None

if pickle is not None and os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as fh:
            model = pickle.load(fh)
        app.logger.info("Loaded model from %s", MODEL_PATH)
    except Exception as e:
        app.logger.warning("Failed to load model: %s", e)
else:
    app.logger.info("No model found; using mock predictions")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json() or {}
    features = data.get("features")
    if features is None:
        return jsonify({"error": "`features` key required (array)"}), 400

    # Basic validation
    if model is not None:
        try:
            arr = np.array(features)
            preds = model.predict(arr).tolist()
            return jsonify({"predictions": preds})
        except Exception as e:
            return jsonify({"error": f"model inference failed: {e}"}), 500

    # Mock deterministic prediction: sum of features mod 2
    try:
        preds = [sum(f) % 2 if isinstance(f, list) else (f % 2) for f in features]
    except Exception:
        # fallback single value
        try:
            val = float(features)
            preds = [val % 2]
        except Exception:
            preds = [0]
    return jsonify({"predictions": preds})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("ML_WORKER_PORT", 5001)))
