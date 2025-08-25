# main.py

import joblib
import json
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Extra

app = FastAPI()

# Load trained model + metadata
model = joblib.load("xgb_pipe.joblib")
meta = json.load(open("model_meta.json"))
THRESHOLD = meta.get("threshold", 0.5)

# Input schema
class StrokeInput(BaseModel):
    gender: str
    age: float
    hypertension: int
    heart_disease: int
    ever_married: str
    Residence_type: str
    avg_glucose_level: float
    bmi: float
    smoking_status: str
    work_type: str

    class Config:
        extra = Extra.ignore

# Root
@app.get("/")
def home():
    return {"message": "Stroke API is working!"}

# Prediction endpoint
@app.post("/predict")
def predict(data: StrokeInput):
    try:
        # Convert input to DataFrame
        X_raw = pd.DataFrame([data.dict()])

        # Model prediction (pipeline includes feature engineering)
        prob = model.predict_proba(X_raw)[0][1]

        # === Logic-based overrides ===
        bmi = X_raw["bmi"].iloc[0]
        smoking_status = X_raw["smoking_status"].iloc[0]
        residence = X_raw["Residence_type"].iloc[0]
        glucose = X_raw["avg_glucose_level"].iloc[0]
        
        if residence == "Rural":
            prob -= 0.02  # slight decrease if it over-inflates risk
        elif residence == "Urban":
            prob += 0.00  # no change


        if smoking_status == "smokes":
            prob += 0.06
        elif smoking_status == "formerly smoked":
            prob += 0.02
        elif smoking_status == "never smoked":
            prob += 0.00
        elif smoking_status == "Unknown":
            prob += 0.01

        # 📌 BMI logic (more granular)
        if bmi < 16:
            prob += 0.05  # severe underweight
        elif bmi < 18.5:
         prob += 0.03  # underweight
        elif 30 <= bmi < 35:
            prob += 0.02  # obese I
        elif 35 <= bmi < 40:
            prob += 0.05  # obese II
        elif 40 <= bmi < 50:
            prob += 0.08  # obese III
        elif 50 <= bmi < 60:
            prob += 0.12  # obese III
        elif 70 <= bmi < 80:
            prob += 0.15  # obese III
        elif 80 <= bmi < 90:
            prob += 0.20  # obese III
        elif bmi >= 90:
            prob += 0.28
        

        if glucose < 70:
            prob += 0.03  # hypoglycemia
        elif 100 <= glucose < 126:
            prob += 0.02  # prediabetic
        elif 126 <= glucose < 200:
            prob += 0.05  # diabetic
        elif 200 <= glucose < 300:
            prob += 0.10  # high diabetic
        elif glucose >= 300:
            prob += 0.15  # extreme hyperglycemia



        # Clip to valid range
        prob = min(max(float(prob), 0), 1)

        # Risk label
        label = "high" if prob >= THRESHOLD else ("medium" if prob >= 0.15 else "low")
        print("✔️ Raw input:", X_raw.to_dict(orient="records"))
        print("✔️ Probability:", prob)
        
        if prob is None:
            raise ValueError("❌ Model returned None for probability. Check input format or pipeline.")



        return {
            "probability": round(prob, 3),
            "percent": round(prob * 100),
            "risk_level": label.upper(),    # <-- optional: match Streamlit expectation
            "threshold": float(THRESHOLD)
        }

    except Exception as e:
        return {"error": str(e)}
