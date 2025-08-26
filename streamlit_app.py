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

# ------------------- TAB: HOME (Improved Layout) -------------------
with tab_home:
    st.markdown("""
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }
        .stAlert-success {
            background-color: #d1fae5 !important;
            color: #065f46 !important;
        }
        label {
            font-weight: 500 !important;
        }
        header { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("## 🧠 Predict Your Stroke Risk")
    st.write("Please enter your information below. Predictions are for educational use only.")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("📅 Age", min_value=1, max_value=120, value=35)
        hypertension = st.selectbox("💉 Hypertension (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        heart_disease = st.selectbox("❤️ Heart Disease (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        avg_glucose_level = st.number_input("🍬 Avg Glucose Level (mg/dL)", min_value=40.0, max_value=400.0, value=100.0, step=1.0)
        smoking_status = st.selectbox("🚬 Smoking Status", ["Formerly smoked", "Never smoked", "Smokes", "Unknown"])

    with col2:
        height_cm = st.number_input("📏 Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=1.0)
        weight_kg = st.number_input("⚖️ Weight (kg)", min_value=10.0, max_value=300.0, value=65.0, step=1.0)

        bmi = weight_kg / ((height_cm / 100) ** 2) if height_cm > 0 else 0
        st.markdown(f"📊 **Calculated BMI:** `{bmi:.2f}`")

        gender = st.selectbox("👤 Gender", ["Male", "Female"])
        ever_married = st.selectbox("💍 Ever Married", ["Yes", "No"])
        Residence_type = st.selectbox("🏠 Residence Type", ["Urban", "Rural"])
        work_type = st.selectbox("💼 Work Type", ["Kid", "Govt_job", "Never_worked", "Private", "Self-employed"])

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

        import time
        start_time = time.time()

        with st.spinner("Predicting..."):
            try:
                response = requests.post("https://stroke-detection-ml.onrender.com/predict", json=payload)
                latency = time.time() - start_time

                if response.status_code == 200:
                    result = response.json()
                    if "error" in result:
                        st.error(f"🚨 Server error: {result['error']}")
                    else:
                        probability = result.get("probability")
                        percent = result.get("percent", probability * 100 if probability else 0)
                        threshold = result.get("threshold")
                        risk_level = result.get("risk_level", "Unknown").upper()

                        prob_percent = round(percent)
                        threshold_percent = round(threshold * 100)

                        st.subheader(f"🧠 Stroke Risk Level: **{risk_level}**")
                        st.markdown(f"**Estimated stroke risk:** `{prob_percent}/100`")
                        st.markdown(f"**Model threshold:** `{threshold_percent}/100`")

                        if prob_percent >= threshold_percent:
                            st.error("🛑 High Risk — Please consider speaking with a doctor.")
                        else:
                            st.success("✅ Low Risk — Keep up the good habits!")

                        st.caption(f"⏱ Prediction completed in {latency:.2f} seconds")
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
