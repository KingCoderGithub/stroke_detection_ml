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
st.markdown("""
    <style>
        /* Remove top black bar */
        header {visibility: hidden;}

        /* Sidebar styling */
        .css-1d391kg, .css-1d1d1f, .css-1lcbmhc {
            background-color: #1d1d1f !important;
        }

        section[data-testid="stSidebar"] > div:first-child {
            background-color: #1d1d1f;
            padding: 2rem 1rem;
        }

        /* Sidebar tab buttons */
        .sidebar-tabs .stRadio > div {
            display: flex;
            flex-direction: column;
        }
        .sidebar-tabs .stRadio div[role="radiogroup"] label {
            background-color: #2c2c2e;
            color: #fefefe;
            padding: 0.8rem 1rem;
            margin-bottom: 0.5rem;
            border-radius: 10px;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        .sidebar-tabs .stRadio div[role="radiogroup"] label:hover {
            background-color: #444;
        }
        .sidebar-tabs .stRadio div[role="radiogroup"] input:checked + div {
            background-color: #007aff !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧭 Navigation", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-tabs'>", unsafe_allow_html=True)
    page = st.radio("Go to", ["🏠 Home", "📘 About", "🧠 How It Works", "⚠️ Disclaimer", "📚 References"])
    st.markdown("</div>", unsafe_allow_html=True)

# ------------------- CUSTOM BODY STYLING -------------------
st.markdown("""
    <style>
        .block-container {
            padding: 2rem 4rem;
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
    st.markdown("Estimate your stroke risk. Results appear below after prediction.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        height_cm = st.number_input("📏 Height (cm)", 50.0, 250.0, 170.0)
        weight_kg = st.number_input("⚖️ Weight (kg)", 10.0, 300.0, 65.0)

    if height_cm > 0:
        bmi = weight_kg / ((height_cm / 100) ** 2)
        st.markdown(f"**💡 Calculated BMI:** `{bmi:.2f}`")
    else:
        bmi = 0

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("📆 Age", 1, 120, 35)
        gender = st.selectbox("⚧ Gender", ["Male", "Female"])
        ever_married = st.selectbox("💍 Ever Married", ["Yes", "No"])
        Residence_type = st.selectbox("🏙️ Residence Type", ["Urban", "Rural"])
        work_type = st.selectbox("💼 Work Type", ["Kid", "Govt_job", "Never_worked", "Private", "Self-employed"])

    with col2:
        smoking_status = st.selectbox("🚬 Smoking Status", ["Formerly smoked", "Never smoked", "Smokes", "Unknown"])
        hypertension = st.selectbox("🩺 Hypertension (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        heart_disease = st.selectbox("❤️ Heart Disease (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        avg_glucose_level = st.number_input("🩸 Average Glucose Level (mg/dL)", 40.0, 400.0, 100.0)

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
                        **🧮 Estimated risk:** **{prob_percent} / 100**  
                        _Out of 100 people like you, around **{prob_percent} may experience a stroke**._

                        **🎯 Model threshold:** _{threshold_percent} / 100_  
                        {"If your score is **above** this threshold, you're considered **high risk**." if prob_percent >= threshold_percent else "Your score is **below** the threshold, so you're considered **low risk**."}
                        """)

                        if prob_percent >= threshold_percent:
                            st.error("🚨 High Risk — Please consult a doctor.")
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
    This stroke risk predictor was built to raise awareness using real-world machine learning on health data.
    
    - ⚙️ Backend: FastAPI + XGBoost
    - 🎨 Frontend: Streamlit
    - 📂 Dataset: Kaggle Stroke Prediction
    """)

# ------------------- HOW IT WORKS -------------------
elif page.startswith("🧠"):
    st.header("🧠 How It Works")
    st.markdown("""
    - Inputs: Age, Gender, BMI, Smoking, Work, Marriage, Residence, Glucose, Heart, Hypertension
    - Model: Calibrated XGBoost with logic overrides and SHAP analysis
    - SMOTE used to handle rare events
    """)

# ------------------- DISCLAIMER -------------------
elif page.startswith("⚠️"):
    st.header("⚠️ Disclaimer")
    st.markdown("""
    This app is educational only. Not a diagnostic tool. Always consult a professional for medical advice.
    """)

# ------------------- REFERENCES -------------------
elif page.startswith("📚"):
    st.header("📚 References")
    st.markdown("""
    - Dataset: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset
    - XGBoost, SHAP, SMOTE
    - Built by KingCoderGithub | MIT License
    """)
