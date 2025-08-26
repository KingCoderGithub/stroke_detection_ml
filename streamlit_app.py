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
        /* Remove black bar from the top */
        header {visibility: hidden;}

        /* Sidebar style */
        section[data-testid="stSidebar"] {
            background-color: #1d1d1f;
            padding: 1.5rem 1rem;
        }

        /* Sidebar tab buttons */
        .stRadio > div {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .stRadio div[role="radiogroup"] > label {
            background-color: #2c2c2e;
            color: #fefefe;
            padding: 1rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1.05rem;
            cursor: pointer;
            transition: background-color 0.3s, transform 0.2s;
        }

        .stRadio div[role="radiogroup"] > label:hover {
            background-color: #3a3a3c;
            transform: translateX(4px);
        }

        .stRadio div[role="radiogroup"] > label[data-selected="true"] {
            background-color: #007aff;
            color: #ffffff;
            transform: scale(1.02);
        }

        /* Main app container */
        .block-container {
            padding: 2rem 5rem;
            max-width: 100%;
        }

        /* Background and text */
        .stApp {
            background-color: #f5f5f7;
            color: #1d1d1f;
            font-family: -apple-system, BlinkMacSystemFont, "San Francisco", "Helvetica Neue", sans-serif;
        }

        h1, h2, h3 {
            color: #1d1d1f;
        }

        /* Input fields */
        label, .stNumberInput label, .stSelectbox label {
            font-weight: 500;
            color: #1d1d1f;
            font-size: 1.05rem;
        }

        .stNumberInput, .stSelectbox {
            margin-bottom: 1rem;
        }

        /* Buttons */
        .stButton>button {
            background-color: #1d1d1f;
            color: #ffffff;
            border-radius: 10px;
            font-weight: 600;
            padding: 0.6rem 1.5rem;
            transition: background-color 0.2s ease;
        }

        .stButton>button:hover {
            background-color: #333333;
        }

        /* Alerts */
        .stAlert-success {
            background-color: #d1f2e4 !important;
            color: #0a3d62 !important;
        }

        .stAlert-error {
            background-color: #fdecea !important;
            color: #6a0a0a !important;
        }

        /* Smooth scrolling to result area */
        html {
            scroll-behavior: smooth;
        }
    </style>
""", unsafe_allow_html=True)

# Use after this:
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📘 About", "🧠 How It Works", "⚠️ Disclaimer", "📚 References"])

# ------------------- HOME -------------------
if page.startswith("🏠"):
    st.markdown("## 🧠 Stroke Risk Predictor")
    st.markdown("Estimate your risk of stroke based on your health and lifestyle. _This tool is for awareness only._")
    st.markdown("---")

    # --- HEIGHT, WEIGHT, BMI block ---
    col1, col2, col3 = st.columns([1.2, 1.2, 1])
    with col1:
        height_cm = st.number_input("📏 Height (cm)", min_value=50.0, max_value=250.0, value=170.0)
    with col2:
        weight_kg = st.number_input("⚖️ Weight (kg)", min_value=10.0, max_value=300.0, value=65.0)
    with col3:
        if height_cm > 0:
            bmi = weight_kg / ((height_cm / 100) ** 2)
            st.markdown(f"**💡 BMI:** `{bmi:.2f}`")
        else:
            bmi = 0

    st.divider()

    # --- Health + Lifestyle Inputs ---
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
        avg_glucose_level = st.number_input("🩸 Avg. Glucose Level (mg/dL)", min_value=40.0, max_value=400.0, value=100.0)

    st.markdown("")

    # --- Predict Button ---
    if st.button("🔍 Predict Stroke Risk"):
        st.markdown("⬇️ _Scroll down for your results..._")
        st.markdown('<div id="results"></div>', unsafe_allow_html=True)
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
                        st.markdown('<script>document.getElementById("results").scrollIntoView({behavior: "smooth"});</script>', unsafe_allow_html=True)
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
