import streamlit as st
import requests
import time

# ------------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="Stroke Risk Predictor",
    page_icon="🩺",
    layout="wide"
)

# ------------------- SIDEBAR NAVIGATION -------------------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📘 About", "🧠 How It Works", "⚠️ Disclaimer", "📚 References"])

# ------------------- CUSTOM STYLING -------------------
st.markdown("""
    <style>
        .block-container {
            padding: 2rem 5rem;
        }

        .stApp {
            background-color: #f5f5f7;
            color: #1d1d1f;
            font-family: -apple-system, BlinkMacSystemFont, "San Francisco", "Helvetica Neue", sans-serif;
        }

        h1, h2, h3 {
            color: #1d1d1f;
        }

        label, .stNumberInput label, .stSelectbox label {
            font-weight: 500;
        }

        .stButton>button {
            background-color: #1d1d1f;
            color: #ffffff;
            border-radius: 8px;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #444;
        }

        .stAlert-success {
            background-color: #d1f2e4 !important;
            color: #0a3d62 !important;
        }
        .stAlert-error {
            background-color: #fdecea !important;
            color: #6a0a0a !important;
        }
    </style>
""", unsafe_allow_html=True)


# ------------------- HOME -------------------
if page.startswith("🏠"):
    st.title("🧠 Stroke Risk Predictor")
    st.markdown("Welcome! Estimate your stroke risk based on health and lifestyle inputs. For awareness only.")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        height_cm = st.number_input("📏 Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
        weight_kg = st.number_input("⚖️ Weight (kg)", min_value=10.0, max_value=300.0, value=65.0)

    if height_cm > 0:
        bmi = weight_kg / ((height_cm / 100) ** 2)
        st.markdown(f"**💡 Calculated BMI:** `{bmi:.2f}`")
    else:
        bmi = 0

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("📆 Age", min_value=1, max_value=120, value=35)
        gender = st.selectbox("⚧ Gender", ["Male", "Female"])
        ever_married = st.selectbox("💍 Ever Married", ["Yes", "No"])
        Residence_type = st.selectbox("🏙️ Residence Type", ["Urban", "Rural"])
        work_type = st.selectbox("💼 Work Type", ["Kid", "Govt_job", "Never_worked", "Private", "Self-employed"])

    with col2:
        smoking_status = st.selectbox("🚬 Smoking Status", ["Formerly smoked", "Never smoked", "Smokes", "Unknown"])
        hypertension = st.selectbox("🩺 Hypertension (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        heart_disease = st.selectbox("❤️ Heart Disease (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        avg_glucose_level = st.number_input("🩸 Average Glucose Level (mg/dL)", min_value=40.0, max_value=400.0, value=100.0)

    st.markdown("")

    if st.button("🔍 Predict Stroke Risk"):
        with st.spinner("⏳ Predicting..."):
            start = time.time()
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

            try:
                response = requests.post("https://stroke-detection-ml.onrender.com/predict", json=payload)
                latency = round((time.time() - start) * 1000)

                if response.status_code == 200:
                    result = response.json()
                    if "error" in result:
                        st.error(f"🚨 Server error: {result['error']}")
                    else:
                        probability = result.get("probability", 0)
                        percent = result.get("percent", probability * 100)
                        threshold = result.get("threshold", 0.5)
                        risk_level = result.get("risk_level", "Unknown").upper()

                        prob_percent = round(percent)
                        threshold_percent = round(threshold * 100)

                        st.subheader(f"🧠 Stroke Risk Level: **{risk_level}**")

                        st.markdown(f"""
                        **🧮 Estimated stroke risk:** **{prob_percent} / 100**  
                        _Out of 100 people like you, around **{prob_percent} may experience a stroke**._

                        **🎯 Model threshold:** _{threshold_percent} / 100_  
                        {"If your score is **above** this threshold, you're considered **high risk**." if prob_percent >= threshold_percent else "Your score is **below** the threshold, so you're considered **low risk**."}
                        """)

                        if prob_percent >= threshold_percent:
                            st.error("🚨 High Risk — Please consider speaking with a healthcare provider.")
                        else:
                            st.success("✅ Low Risk — Keep up the good habits!")

                        st.markdown(f"⏱️ **Prediction latency:** `{latency}` ms")
                else:
                    st.error("❌ API error. Please try again.")

            except Exception as e:
                st.error(f"Request failed: {e}")


# ------------------- ABOUT -------------------
elif page.startswith("📘"):
    st.header("📘 About This App")
    st.markdown("""
    This stroke risk predictor was built to **raise public awareness** about stroke risk factors.

    ---
    **🎯 Goals:**
    - Make health education accessible
    - Encourage early preventive care
    - Showcase real-world ML applications in healthcare

    **🧑‍🎓 Ideal for:**
    - General public
    - Students & educators
    - Health-conscious individuals

    _This tool does not replace professional medical advice._
    """)

# ------------------- HOW IT WORKS -------------------
elif page.startswith("🧠"):
    st.header("🧠 How It Works")
    st.markdown("""
    ### 🧮 Inputs
    - **Demographics**: Age, Gender, Residence
    - **Health**: BMI, Glucose, Hypertension, Heart disease
    - **Lifestyle**: Smoking, Work type, Marriage

    ### ⚙️ Model
    - Calibrated **XGBoost**
    - Engineered features (e.g. BMI/Glucose ratio, cardio flags)
    - Balanced with **SMOTE** for rare event prediction
    - Optimized threshold for **high recall** (safety-first)

    ### 🔎 Explainability
    - SHAP values used internally
    - Logic overrides ensure output sanity
    """)

# ------------------- DISCLAIMER -------------------
elif page.startswith("⚠️"):
    st.header("⚠️ Disclaimer")
    st.markdown("""
    This app is intended for **educational and awareness** purposes only.

    - It is **not a medical device**
    - It does **not provide a diagnosis**
    - Always consult a **licensed doctor** for medical advice
    """)

# ------------------- REFERENCES -------------------
elif page.startswith("📚"):
    st.header("📚 References")
    st.markdown("""
    **📂 Dataset**  
    - [Kaggle Stroke Dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset)

    **🔬 Tech**  
    - XGBoost, Scikit-learn, SHAP  
    - Streamlit + FastAPI

    **🛠 Built by:** [KingCoderGithub](https://github.com/KingCoderGithub)  
    MIT Licensed — Educational use only.
    """)
