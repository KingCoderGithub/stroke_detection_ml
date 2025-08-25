🧠 Stroke Risk Prediction Web App

A Machine Learning + Domain Logic Based Tool for Public Health Awareness

🩺 Overview

Stroke is one of the leading causes of death and disability worldwide, yet it is often preventable with timely lifestyle and clinical interventions. This project presents an interactive stroke risk prediction tool that combines advanced machine learning techniques with medically grounded heuristics to offer real-time stroke risk estimation for individuals based on demographic, clinical, and lifestyle attributes.

This tool is built to educate, inform, and encourage preventive care — not to replace professional medical advice.

🧪 Project Motivation

Predicting stroke risk from limited, anonymized population data (like the popular Kaggle stroke dataset
) presents several modeling challenges:

Highly imbalanced data (stroke events are rare)

Noisy or incomplete feature definitions (e.g., BMI or smoking status inconsistencies)

Need for realistic and intuitive outputs for non-expert users

This project aims to bridge the gap between statistical modeling and medical plausibility by combining:

🧠 A calibrated XGBoost classifier trained on engineered features

🧰 Logic-based override rules to correct counterintuitive predictions

🌐 A user-friendly Streamlit frontend

⚙️ A FastAPI backend for efficient API inference

🧬 Features & Functionality

🧮 Inputs:

Age, gender, hypertension, heart disease

Marital status, residence type, smoking status

Height, weight → auto-calculated BMI

Average glucose level

📊 Feature Engineering:

BMI category, age groups, glucose quantiles

Binary health flags (e.g., senior, smoker, high BMI)

Interaction terms (e.g., age × smoking, glucose ÷ BMI)

🧠 Model:

A stacked feature pipeline with SMOTE balancing and XGBoost

Optimized on PR AUC to prioritize rare event detection

🧩 Logic Overrides:
To avoid illogical results due to training data biases, several post-prediction adjustments are applied, such as:

Smoking status increases risk even if the raw model underweights it

Extremely high or low BMI gets adjusted upward for risk

High glucose levels (e.g., > 300 mg/dL) elevate risk score

"Unknown" values (e.g., in smoking) add a small penalty

🧾 Output:

Probability of stroke

Natural language interpretation: low, medium, or high risk

Color-coded, accessible display for users

🏗️ Architecture
flowchart LR
    subgraph User Interface
        A[Streamlit App]
    end

    subgraph Backend
        B[FastAPI API]
        C[Model Pipeline (XGBoost + SMOTE)]
        D[Logic-Based Overrides]
    end

    A --> B --> C --> D --> B --> A

⚠️ Disclaimer

This tool is designed for educational and awareness purposes only. It is not a medical device and should not be used for clinical decision-making. Always consult a licensed medical professional for actual diagnosis and treatment.

🛠️ Run the App Locally
# 1. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install requirements
pip install -r requirements.txt

# 3. Train model
python train_pipeline.py

# 4. Start backend
uvicorn main:app --reload

# 5. In a separate terminal, run frontend
streamlit run streamlit_app.py

📚 Acknowledgements

Dataset: Kaggle - Stroke Prediction Dataset

XGBoost, FastAPI, Streamlit, Imbalanced-learn

Public health researchers working to democratize stroke risk knowledge