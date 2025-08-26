import streamlit as st
import requests
import time

# ------------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="🩺 Stroke Risk Predictor",
    page_icon="🧠",
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
            background-color: #f4f6fa;
            font-family: 'Segoe UI', sans-serif;
        }

        /* General text colors */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown, .markdown-text-container, .stText, .stSelectbox, .stNumberInput {
            color: #102a43;
        }

        /* Input labels */
        label, .stRadio label, .stSelectbox label, .stNumberInput label {
            font-weight: 600;
            color: #243b53;
        }

        /* Buttons */
        .stButton>button {
            background-color: #20639b;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5em 1em;
            transition: 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #173f5f;
            color: white;
        }

        /* Tabs styling */
        .stTabs [role="tab"] {
            background-color: #dbe9f4;
            color: #102a43;
            font-weight: bold;
            border-radius: 0.5rem 0.5rem 0 0;
            padding: 8px 16px;
            margin-right: 4px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #20639b !important;
            color: white !important;
        }

        /* Subheader in results */
        .stMarkdown h2 {
            color: #173f5f;
        }

        /* Status messages */
        .stAlert {
            border-radius: 10px;
        }

        /* Fix for markdown text inside tabs */
        .stMarkdown p {
            color: #102a43;
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
with tab_home:
    st.markdown(
        """
        <style>
            /* Set overall background */
            body, .stApp {
                background-color: #2c003e;
                color: #f4e29a;
            }

            /* Style all text input labels */
            label, div[role='radiogroup'], .st-b7, .st-b3 {
                color: #f4e29a !important;
            }

            /* Button */
            button {
                background-color: #f4e29a !important;
                color: #2c003e !important;
                border: none;
                font-weight: bold;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("🩺 Stroke Risk Predictor")
    st.markdown("Enter your health details below to estimate your stroke risk. This tool is for **awareness purposes only**.")

    age = st.number_input("📆 Age", min_value=1, max_value=120, value=35)
    hypertension = st.selectbox("❤️ Hypertension (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
    heart_disease = st.selectbox("💔 Heart Disease (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
    avg_glucose_level = st.number_input("🧪 Average Glucose Level (mg/dL)", min_value=40.0, max_value=400.0, value=100.0, step=1.0)
    height_cm = st.number_input("📏 Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=1.0)
    weight_kg = st.number_input("⚖️ Weight (kg)", min_value=10.0, max_value=300.0, value=65.0, step=1.0)

    # BMI calculation
    if height_cm > 0:
        bmi = weight_kg / ((height_cm / 100) ** 2)
        st.markdown(f"**🧮 Calculated BMI:** `{bmi:.2f}`")
    else:
        bmi = 0

    gender = st.selectbox("🚻 Gender", ["Male", "Female"])
    ever_married = st.selectbox("💍 Ever Married", ["Yes", "No"])
    Residence_type = st.selectbox("🏙️ Residence Type", ["Urban", "Rural"])
    smoking_status = st.selectbox("🚬 Smoking Status", ["Formerly smoked", "Never smoked", "Smokes", "Unknown"])
    work_type = st.selectbox("💼 Work Type", ["Kid", "Govt_job", "Never_worked", "Private", "Self-employed"])

    result_placeholder = st.empty()

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

        with st.spinner("⏳ Predicting..."):
            try:
                response = requests.post("https://stroke-detection-ml.onrender.com/predict", json=payload)
                if response.status_code == 200:
                    result = response.json()

                    if "error" in result:
                        result_placeholder.error(f"🚨 Server error: {result['error']}")
                    else:
                        probability = result.get("probability")
                        percent = result.get("percent", result.get("probability", 0) * 100)
                        threshold = result.get("threshold")
                        risk_level = result.get("risk_level", "Unknown").upper()

                        prob_percent = round(percent)
                        threshold_percent = round(threshold * 100)

                        is_high_risk = prob_percent >= threshold_percent

                        explanation = f"""
                        ## 🧠 Stroke Risk Level: **{risk_level}**

                        **Your estimated stroke risk:** **{prob_percent} out of 100**  
                        _This means out of 100 people like you, around **{prob_percent} may experience a stroke**._

                        **Model threshold:** _{threshold_percent} out of 100_  
                        {"⚠️ You are **above** this threshold and considered **high risk**." if is_high_risk else "✅ You are **below** the threshold and considered **low risk**."}
                        """

                        styled_box = """
                        <div style="background-color: %s; color: %s; padding: 12px 16px; border-radius: 8px; margin-top: 16px; font-weight: bold;">
                            %s
                        </div>
                        """ % (
                            "#8B0000" if is_high_risk else "#014421",
                            "#f4e29a",
                            "⚠️ High Risk — Please consult a healthcare provider." if is_high_risk else "✅ Low Risk — Keep up the good habits!"
                        )

                        result_placeholder.markdown(explanation, unsafe_allow_html=True)
                        result_placeholder.markdown(styled_box, unsafe_allow_html=True)
                else:
                    result_placeholder.error("❌ API error. Please try again.")
            except Exception as e:
                result_placeholder.error(f"Request failed: {e}")



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
