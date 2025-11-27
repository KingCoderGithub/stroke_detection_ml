import streamlit as st
import requests
import time

# ------------------- PAGE CONFIG -------------------
st.set_page_config(
    page_title="Stroke Risk Predictor",
    page_icon="🩺",
    layout="wide"
)

# ------------------- CUSTOM STYLING FOR SIDEBAR & PAGE -------------------
st.markdown("""
    <style>
        /* Make the sidebar toggle arrow more visible (black) */
        button[kind="icon"] svg, button[kind="header"] svg {
            stroke: black !important;
            fill: black !important;
        }

        /* 🔹 Force ALL headings (main app) to black */
        h1, h2, h3, h4, h5, h6 {
            color: #000000 !important;
        }

        /* 🔹 Sidebar text color (desktop + mobile) */
        section[data-testid="stSidebar"] {
            background-color: #1d1d1f;
            padding: 2rem 1rem;
        }
        section[data-testid="stSidebar"] * {
            color: #ffffff !important;   /* force all sidebar text white */
        }

        /* 🔹 Sidebar hover + selected state */
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
            background-color: #3a3a3c;
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-selected="true"] {
            background-color: #007aff;
            color: #ffffff !important;
        }

        /* Sidebar radio group as Notion-style cards */
        .stRadio > div {
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
        }
        .stRadio div[role="radiogroup"] > label {
            background-color: #2c2c2e;
            padding: 1rem 1.2rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1.1rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.15);
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease;
        }
        .stRadio div[role="radiogroup"] > label:hover {
            background-color: #3a3a3c;
            transform: translateX(6px);
        }
        .stRadio div[role="radiogroup"] > label[data-selected="true"] {
            background-color: #007aff;
            transform: scale(1.02);
        }

        /* Main app container */
        .block-container {
            padding: 2rem 4rem;
            max-width: 100%;
        }

        /* Global app background and font */
        .stApp {
            background-color: #f5f5f7;
            color: #1d1d1f;
            font-family: -apple-system, BlinkMacSystemFont, "San Francisco", "Helvetica Neue", sans-serif;
        }

        /* Inputs and labels */
        label, .stNumberInput label, .stSelectbox label {
            font-weight: 500;
            color: #1d1d1f;
            font-size: 1.05rem;
        }

        .stNumberInput, .stSelectbox {
            margin-bottom: 1rem;
        }

        /* Button styling */
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

        /* Alert styling */
        .stAlert-success {
            background-color: #d1f2e4 !important;
            color: #0a3d62 !important;
        }
        .stAlert-error {
            background-color: #fdecea !important;
            color: #6a0a0a !important;
        }

        /* Smooth scroll */
        html {
            scroll-behavior: smooth;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------- SIDEBAR NAVIGATION -------------------
st.markdown("""
    <style>
    [data-testid="stSidebar"] h1 {
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to", ["🏠 Home", "📘 About", "🧠 How It Works", "⚠️ Disclaimer", "📚 References"])

# ------------------- HOME -------------------
if page.startswith("🏠"):
    st.markdown("## Stroke Risk Predictor")
    st.markdown("🩺 **Know Your Risk. Act Early.** A simple tool to **estimate your stroke risk** using everyday health info.")
    st.markdown("---")

    # --- PERSONAL + HEALTH INFO ---
    st.subheader("👤 Personal & Health Information")
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("🎂 Age", min_value=0, max_value=120, value=30, step=1)
        gender = st.selectbox("🚻 Gender", ["Male", "Female"])
        ever_married = st.selectbox("💍 Ever Married", ["Yes", "No"])
        Residence_type = st.selectbox("🏠 Residence Type", ["Urban", "Rural"])
        work_type = st.selectbox("💼 Work Type", ["Kid", "Govt_job", "Never_worked", "Private", "Self-employed"])

    with col2:
        smoking_status = st.selectbox("🚬 Smoking Status", ["Formerly smoked", "Never smoked", "Smokes", "Unknown"])
        hypertension = st.selectbox("💢 Hypertension (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        heart_disease = st.selectbox("❤️ Heart Disease (Diagnosed)", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        avg_glucose_level = st.number_input("🩸 Avg. Glucose Level (mg/dL)", min_value=40.0, max_value=400.0, value=100.0, step=1.0)

    st.markdown("")

    # --- HEIGHT, WEIGHT, BMI block ---
    st.subheader("📏 Height, Weight & BMI")
    col3, col4, col5 = st.columns([1.2, 1.2, 0.8])

    with col3:
        height_cm = st.number_input("📏 Height (cm)", min_value=50.0, max_value=250.0, value=170.0, step=1.0)

    with col4:
        weight_kg = st.number_input("⚖️ Weight (kg)", min_value=10.0, max_value=300.0, value=65.0, step=1.0)

    with col5:
        if height_cm > 0:
            bmi = weight_kg / ((height_cm / 100) ** 2)
            st.markdown(f"**💡 BMI:** `{bmi:.2f}`")
        else:
            bmi = 0

    # --- Predict Button ---
    st.markdown("")
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

                        st.subheader(f" Stroke Risk Level: **{risk_level}**")

                        st.markdown(f"""
                        **🧮 Estimated stroke risk:** **{prob_percent} / 100**  
                        _Out of 100 people like you, around **{prob_percent} may experience a stroke**._

                        **🎯 Model threshold:** _{threshold_percent} / 100_  
                        {"If your score is **above** this threshold, you're considered **high risk**." if prob_percent >= threshold_percent else "Your score is **below** the threshold, so you're considered **low risk**."}
                        """)

                        if prob_percent >= threshold_percent:
                            st.markdown(
                                "<p style='color: black; font-weight: bold; font-size: 18px;'>🚨 High Risk — Please consider speaking with a healthcare provider.</p>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown("""
                                <div style='background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; color: black; font-size: 1.1rem;'>
                                    ✅ <b>Low Risk</b> — Keep up the good habits!
                                </div>
                            """, unsafe_allow_html=True)

                        st.markdown(f"⏱️ **Prediction latency:** `{latency}` ms")
                        st.markdown('<script>document.getElementById("results").scrollIntoView({behavior: "smooth"});</script>', unsafe_allow_html=True)
                else:
                    st.markdown("""
                                <div style='background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; color: black; font-size: 1.1rem;'>
                                    ❌ <b>API ERROR</b> — Please try again.
                                </div>
                            """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Request failed: {e}")



# ------------------- HOW IT WORKS -------------------
elif page.startswith("🧠"):
    st.markdown("<h2 style='color: white;'>🧠 How It Works</h2>", unsafe_allow_html=True)
    st.markdown("""
    ### 🧮 Inputs
    The model uses a combination of everyday health and lifestyle information:
    - **Demographics**: Age, Gender, Residence type
    - **Health**: BMI, Average glucose level, Hypertension, Heart disease
    - **Lifestyle**: Smoking status, Work type, Marital history

    ### ⚙️ Model Pipeline
    - Calibrated **XGBoost** classifier
    - Rich engineered features (e.g. BMI/Glucose ratio, cardio flags, interaction terms like age×BMI, age×glucose)
    - Training-time balancing with **SMOTE** so the model sees more stroke cases during training
    - Decision threshold tuned for **high recall**, prioritising catching more high-risk users (safety-first)

    ### 🔎 Explainability (SHAP)
    We use **SHAP (SHapley Additive exPlanations)** to understand which features
    are pushing the prediction higher or lower for each person.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.image(
            "reports/shap_summary.png",
            caption="Global feature importance — which features most influence stroke risk overall",
            use_column_width=True,
        )

    with col2:
        st.image(
            "reports/shap_force_example_0.png",
            caption="Example SHAP explanation for one person’s prediction",
            use_column_width=True,
        )

    st.markdown("""
    These plots help make the model less of a “black box” by showing how inputs
    like age, BMI, glucose and smoking status contribute to the final risk score.
    """)

    # ------------------- MODEL PERFORMANCE SECTION -------------------
    st.markdown("### 📊 Model Performance (validation)")

    # Show metrics summary from the text file if it exists
    try:
        with open("reports/metrics_summary.txt", "r") as f:
            metrics_text = f.read()
        st.code(metrics_text, language="text")
    except FileNotFoundError:
        st.info("Run `python metrics_report.py` to generate validation metrics and plots.")

    col3, col4, col5 = st.columns(3)

    with col3:
        st.image(
            "reports/pr_curve.png",
            caption="Precision–Recall curve (focus on rare stroke cases)",
            use_column_width=True,
        )

    with col4:
        st.image(
            "reports/confusion_matrix.png",
            caption="Confusion matrix at the chosen decision threshold",
            use_column_width=True,
        )

    with col5:
        st.image(
            "reports/calibration_curve.png",
            caption="Calibration curve — how well predicted probabilities match reality",
            use_column_width=True,
        )


# ------------------- ABOUT -------------------
elif page.startswith("📘"):
    st.markdown("<h2 style='color: black;'>📘 About This Project</h2>", unsafe_allow_html=True)
    st.markdown("""
    Stroke remains one of the leading global causes of long-term disability, but early risk awareness can enable prevention and faster medical response.

    This project was created to explore how machine learning can be used in public health tools that are **fast, interpretable and responsible**.

    The system uses an **end-to-end ML pipeline powered by XGBoost**, connected to a lightweight API backend and an awareness-focused Streamlit interface.

    ### ⚙️ How It Works (Reader-Friendly)
    1. You enter basic demographic, health and lifestyle details (age, BMI, average glucose, smoking habits, residence type, occupation, etc.).
    2. The model processes these using engineered interactions and medical-sanity checks.
    3. It generates a **stroke risk probability and category (Low / High / Moderate)**.
    4. The prediction is supported by SHAP explainability graphs so you can understand *why* the model scored the way it did.

    ### 📊 Performance Snapshot (previous validation benchmarks)
    - During early development, the model reached **~80–90% overall accuracy** on hold-out validation, showing strong general reliability on mixed health inputs.
    - On more rigorous testing focused on rare high-risk stroke detection, it maintained balanced **precision (~57%) and recall (~51%)**, with **PR-AUC > 0.54**, indicating it performs meaningfully better than random for identifying stroke cases in an imbalanced dataset.

    ### 🎯 Project Goals
    - Increase **public stroke risk awareness**
    - Provide **fast predictions (targeting <500 ms)**
    - Keep outputs **medically realistic using logic-based guards**
    - Make model decisions **interpretable, transparent, and educationally trustworthy**
    - Encourage early discussion with a healthcare professional when necessary

    ### 🧠 What This Project Demonstrates About Me
    - Building a deployed ML inference system from start to finish
    - Understanding medical AI limitations and real validation metrics
    - Applying responsible logic instead of blindly trusting model outputs
    - Prioritising interpretability (SHAP) and rare-event evaluation (PR-AUC, F1, calibration)
    - Connecting backend APIs with a reliable, easiest-paths-that-work mindset

    > ⚠️ This tool is **not a diagnosis**, but a **stroke risk awareness estimator** for educational purposes.
    It does not replace professional advice from a licensed doctor.
    """)


# ------------------- DISCLAIMER -------------------
elif page.startswith("⚠️"):
    st.markdown("<h2 style='color: white;'>⚠️ Disclaimer!</h2>", unsafe_allow_html=True)
    st.markdown("""
    This app is intended for **educational and awareness** purposes only.

    - It is **not a medical device**
    - It does **not provide a diagnosis**
    - Always consult a **licensed doctor** for medical advice
    """)

# ------------------- REFERENCES -------------------
elif page.startswith("📚"):
    st.markdown("<h2 style='color: white;'>📚 References</h2>", unsafe_allow_html=True)
    st.markdown("""
    **📂 Dataset**  
    - [Kaggle Stroke Dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset)

    **🔬 Tech**  
    - XGBoost, Scikit-learn, SHAP  
    - Streamlit + FastAPI

    **🛠 Built by:** [KingCoderGithub](https://github.com/KingCoderGithub)  
    https://github.com/KingCoderGithub/stroke_detection_ml.git
    - MIT Licensed — Educational use only.
    """)
