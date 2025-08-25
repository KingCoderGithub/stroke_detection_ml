import streamlit as st
import requests

# Set page metadata
st.set_page_config(page_title="Stroke Risk Predictor", page_icon="🩺")

st.title("🩺 Stroke Risk Predictor")
st.markdown("Enter your health details below to estimate your stroke risk. This tool is for awareness purposes only.")

# --- User Input ---
age = st.number_input("Age", min_value=1, max_value=120, value=35)
hypertension = st.selectbox("Hypertension (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
heart_disease = st.selectbox("Heart Disease (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
avg_glucose_level = st.number_input(
    "Average Glucose Level (mg/dL)",
    min_value=40.0,
    max_value=400.0,
    value=100.0,
    step=1.0
)

height_cm = st.number_input(
    "Height (cm)",
    min_value=50.0,
    max_value=250.0,
    value=170.0,
    step=1.0
)

weight_kg = st.number_input(
    "Weight (kg)",
    min_value=10.0,
    max_value=300.0,
    value=65.0,
    step=1.0
)

# BMI = weight (kg) / [height (m)]²
if height_cm > 0:
    bmi = weight_kg / ((height_cm / 100) ** 2)
    st.markdown(f"**Calculated BMI:** `{bmi:.2f}`")
else:
    bmi = 0

gender = st.selectbox("Gender", ["Male", "Female"])
ever_married = st.selectbox("Ever Married", ["Yes", "No"])
Residence_type = st.selectbox("Residence Type", ["Urban", "Rural"])
smoking_status = st.selectbox("Smoking Status", ["Formerly smoked", "Never smoked", "Smokes", "Unknown"])
work_type = st.selectbox("Work Type", [
    "Kid", "Govt_job", "Never_worked", "Private", "Self-employed"
])

# --- Predict Button ---
if st.button("🔍 Predict Stroke Risk"):
    payload = {
        "age": age,
        "hypertension": hypertension,
        "heart_disease": heart_disease,
        "avg_glucose_level": avg_glucose_level,
        "bmi": bmi,
        "gender": gender,
        "ever_married": ever_married,
        "Residence_type": Residence_type,
        "smoking_status": smoking_status,
        "work_type": work_type
    }

    with st.spinner("Predicting..."):
        try:
            # 🔁 Connect to your FastAPI backend on Render
            response = requests.post("https://stroke-detection-ml.onrender.com/predict", json=payload)
            if response.status_code == 200:
                result = response.json()

                if "error" in result:
                    st.error(f"🚨 Server error: {result['error']}")
                else:
                    probability = result.get("probability")
                    percent = result.get("percent", result.get("probability", 0) * 100)
                    threshold = result.get("threshold")
                    risk_level = result.get("risk_level", "Unknown").upper()

                    prob_percent = round(percent)
                    threshold_percent = round(threshold * 100)

                    st.subheader(f"🩺 Stroke Risk Level: {risk_level}")
                    st.markdown(
                        f"""
                        **Your estimated stroke risk:** **{prob_percent} out of 100**  
                        This means: _Out of 100 people like you, around **{prob_percent} may experience a stroke**._

                        **Model threshold:** _{threshold_percent} out of 100_  
                        {"If your score is **above** this threshold, you're considered **high risk**." if prob_percent >= threshold_percent else "Your score is **below** the threshold, so you're considered **low risk**."}
                        """
                    )

                    if prob_percent >= threshold_percent:
                        st.error("⚠️ Please consider speaking with a healthcare provider.")
                    else:
                        st.success("✅ Keep taking care of your health!")

            else:
                st.error("❌ API error. Please try again.")
        except Exception as e:
            st.error(f"Request failed: {e}")
