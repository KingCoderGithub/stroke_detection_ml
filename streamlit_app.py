import streamlit as st
import requests
import streamlit.components.v1 as components
import time

# ------------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="🩺 Stroke Risk Predictor",
    page_icon="",
    layout="centered"
)

# ------------------- CUSTOM STYLING -------------------
st.markdown("""
    <style>
        /* Expand page width */
        .main .block-container {
            max-width: 95%;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        /* Set overall background */
        .stApp {
            background-color: #1f2e1e;
            font-family: 'Segoe UI', sans-serif;
        }

        /* General text colors */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown, .markdown-text-container, .stText, .stSelectbox, .stNumberInput {
            color: #fefae0;
        }

        /* Input labels */
        label, .stRadio label, .stSelectbox label, .stNumberInput label {
            font-weight: 600;
            color: #fefae0;
        }

        /* Buttons */
        .stButton>button {
            background-color: #4a5f4a;
            color: #fefae0;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5em 1em;
            transition: 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #3b4b3b;
            color: #fefae0;
        }

        /* Tabs styling */
        .stTabs [role="tab"] {
            background-color: #4a5f4a;
            color: #fefae0;
            font-weight: bold;
            border-radius: 0.5rem 0.5rem 0 0;
            padding: 8px 16px;
            margin-right: 4px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #6c8f6c !important;
            color: #1f2e1e !important;
        }

        /* Subheader in results */
        .stMarkdown h2 {
            color: #fefae0;
        }

        /* Status messages */
        .stAlert-success {
            background-color: #fefae0 !important;
            color: #1f2e1e !important;
            font-weight: bold;
        }
        .stAlert-error {
            background-color: #5c4033 !important;
            color: #fefae0 !important;
            font-weight: bold;
        }

        /* Fix for markdown text inside tabs */
        .stMarkdown p {
            color: #fefae0;
            line-height: 1.6;
        }

        /* Ensure responsiveness on smaller screens */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- NAVIGATION TABS -------------------
tab_home, tab_about, tab_how, tab_disclaimer, tab_references = st.tabs(
    ["🏠 Home", "📘 About", "🧠 How It Works", "⚠️ Disclaimer", "📚 References"]
)

# ------------------- HOME TAB -------------------
with tab_home:
    st.title("🩺 Stroke Risk Predictor")
    st.markdown("Enter your health details below to estimate your stroke risk. This tool is for awareness purposes only.")

    col1, col2 = st.columns(2)
    with col1:
        height_cm = st.number_input("📏 Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=1.0)
        weight_kg = st.number_input("⚖️ Weight (kg)", min_value=10.0, max_value=300.0, value=65.0, step=1.0)

    if height_cm > 0:
        bmi = weight_kg / ((height_cm / 100) ** 2)
        st.markdown(f"**💡 Calculated BMI:** `{bmi:.2f}`")
    else:
        bmi = 0

    st.divider()

    age = st.number_input("📆 Age", min_value=1, max_value=120, value=35)
    gender = st.selectbox("⚧ Gender", ["Male", "Female"])
    ever_married = st.selectbox("💍 Ever Married", ["Yes", "No"])
    Residence_type = st.selectbox("🏙️ Residence Type", ["Urban", "Rural"])
    work_type = st.selectbox("💼 Work Type", ["Kid", "Govt_job", "Never_worked", "Private", "Self-employed"])
    smoking_status = st.selectbox("🚬 Smoking Status", ["Formerly smoked", "Never smoked", "Smokes", "Unknown"])
    hypertension = st.selectbox("🩺 Hypertension (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
    heart_disease = st.selectbox("❤️ Heart Disease (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
    avg_glucose_level = st.number_input("🩸 Average Glucose Level (mg/dL)", min_value=40.0, max_value=400.0, value=100.0, step=1.0)

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
                        **🧮 Your estimated stroke risk:** **{prob_percent} / 100**  
                        _This means: Out of 100 people like you, around **{prob_percent} may experience a stroke**._

                        **🎯 Model threshold:** _{threshold_percent} / 100_  
                        {"If your score is **above** this threshold, you're considered **high risk**." if prob_percent >= threshold_percent else "Your score is **below** the threshold, so you're considered **low risk**."}
                        """)

                        if prob_percent >= threshold_percent:
                            st.error("🚨 High Risk — Please consider speaking with a healthcare provider.")
                        else:
                            st.success("✅ Low Risk — Keep up the good habits!")

                        st.markdown(f"⏱️ **Latency:** `{latency}` ms")
                else:
                    st.error("❌ API error. Please try again.")

            except Exception as e:
                st.error(f"Request failed: {e}")



# ------------------- TAB: ABOUT -------------------
with tab_about:
    st.header("📘 About This App")
    st.markdown("""
    This stroke risk predictor was built to **raise public awareness** about stroke risk factors through an easy-to-use tool.  
    You can enter basic health and lifestyle details, and the model will give an **estimated stroke risk**, based on a machine learning analysis of thousands of health records.

    ---
    **🎯 Goals:**
    - Make health education accessible
    - Encourage early preventive care
    - Showcase real-world ML applications in healthcare

    **🧑‍🎓 Ideal for:**
    - General public
    - Students & educators
    - Health-conscious individuals

    This tool **does not replace professional medical advice**, but it can help spark meaningful discussions and awareness.
    """)

# ------------------- TAB: HOW IT WORKS -------------------
with tab_how:
    st.header("🧠 How It Works")
    st.markdown("""
    ### 🧮 Input Data
    - **Demographics**: Age, Gender, Residence
    - **Health Metrics**: BMI (auto-calculated), Glucose, Hypertension, Heart disease
    - **Lifestyle**: Smoking status, Work type, Marital status

    ### ⚙️ Behind the Scenes
    - A calibrated **XGBoost model** trained on stroke prediction data
    - Custom **feature engineering**:
        - BMI to Glucose ratios
        - Smoker flag + Age interaction
        - Cardio flags and logic overrides (e.g., very high BMI adds risk)
    - Balanced with **SMOTE** to improve prediction on rare events
    - Final output based on **threshold optimization for recall** (safety-first)

    ### 🔎 Explainability
    - Uses SHAP values to understand feature impact (not exposed here)
    - Transparent thresholds shown to build trust
    - Custom logic applied to override clearly unrealistic outputs

    ---
    _Built using Python, Streamlit, FastAPI, and XGBoost._
    """)

# ------------------- TAB: DISCLAIMER -------------------
with tab_disclaimer:
    st.header("⚠️ Disclaimer")
    st.markdown("""
    This app is intended for **educational and awareness** purposes only.

    - It is **not a medical device**.
    - It does **not provide a diagnosis** or treatment recommendation.
    - Always consult with a **qualified healthcare professional** for health concerns.

    The model is based on patterns from anonymized public datasets and may not reflect individual clinical reality.
    """)

# ------------------- TAB: REFERENCES -------------------
with tab_references:
    st.header("📚 References")
    st.markdown("""
    **📂 Dataset**  
    - [Kaggle Stroke Prediction Dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset)

    **🔬 ML & Libraries**  
    - XGBoost, Scikit-learn, SHAP  
    - Streamlit (Frontend)  
    - FastAPI (Backend)

    **📜 Authorship & License**  
    - Created by [KingCoderGithub](https://github.com/KingCoderGithub)  
    - Open-sourced under MIT License  
    - Educational project, not for commercial use

    _If using this for teaching, citation is appreciated._  
    """)
