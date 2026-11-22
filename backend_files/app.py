"""Flask API that serves the serialized SuperKart sales pipeline."""

import joblib
import pandas as pd
from flask import Blueprint, Flask, jsonify, request

app = Flask(__name__)
superkart_api = Blueprint("superkart_api", __name__)

# The saved object is the full preprocessing + model pipeline
model = joblib.load("superkart_model.joblib")

# Names and order must match the columns the pipeline was trained on
FEATURE_COLUMNS = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


def _frame_from_records(records):
    """Build a one-or-many-row frame and reject a payload that omits a feature."""
    frame = pd.DataFrame(records)
    missing = [column for column in FEATURE_COLUMNS if column not in frame.columns]
    if missing:
        return None, missing
    return frame[FEATURE_COLUMNS], None


@superkart_api.post("/v1/predict")
def predict():
    """Online inference: one JSON object in, one sales prediction out."""
    payload = request.get_json(force=True)
    frame, missing = _frame_from_records([payload])
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400
    prediction = float(model.predict(frame)[0])
    return jsonify({"predicted_sales": round(prediction, 2)})


@superkart_api.post("/v1/predictbatch")
def predict_batch():
    """Batch inference: a CSV upload whose rows match the feature contract."""
    upload = request.files["file"]
    frame = pd.read_csv(upload)
    missing = [column for column in FEATURE_COLUMNS if column not in frame.columns]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400
    predictions = model.predict(frame[FEATURE_COLUMNS])
    # Keys are row indexes so the caller can line predictions up with the file
    body = {str(index): round(float(value), 2) for index, value in enumerate(predictions)}
    return jsonify(body)


app.register_blueprint(superkart_api)

if __name__ == "__main__":
    # 7860 is the port the Codespace forwards for the backend container
    app.run(host="0.0.0.0", port=7860)
