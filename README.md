# 🩺 Stroke Risk Predictor  
### _Because awareness shouldn’t wait for symptoms_  

**A portfolio-focused ML project built for public health awareness and undergraduate CS/Data Science credibility (Fall 2026 cycle).**

Link - https://strokedetectionml.streamlit.app/#bf865f99

---

## 🧠 Smart Risk. Real Logic. Fast Inference.

This project is built to combine:

- ⚡ **FastAPI Backend** → cloud API inference with low latency  
- 🌍 **Sleek Streamlit Frontend** → accessible UI prioritising public trust  
- 🧪 **Calibrated XGBoost Classifier** → trained with medical feature engineering  
- 🧩 **Domain-Logic Safety Overrides** → ensures predictions remain medically realistic without retraining  
- 🔎 **SHAP Explainability** → reveals what drives each prediction  

> **Mission:** Use machine learning to detect stroke risk using medically meaningful patterns, explain the model’s reasoning, and provide outputs that humans can safely rely on for **awareness — not diagnosis**.

---

## 🩺 What This Project Does

It predicts **personal stroke-risk probability** using:

- **Demographics** → age, gender, residence type  
- **Clinical history** → diagnosed hypertension, heart disease  
- **Lifestyle indicators** → smoking status, occupation, marital history  
- **Core health markers** → BMI (calculated from height × weight), average glucose level  

---

## 🔍 Rare-Event Performance Snapshot (from real validation)

- **80–90% accuracy during early development** on hold-out testing  
- **~96% overall accuracy on extended validation** for healthy vs risk-elevated screening  
- **Precision: ~57%** (most high-risk flags correct, not noisy alerts)  
- **Recall: ~51%** (catches a meaningful portion of rare stroke cases)  
- **PR-AUC: ~0.54** (rare-event detection performs better than random)

> 💡 Why we include *these metrics* instead of only accuracy:
> Because **stroke cases are rare**, we optimise for **precision-recall behaviour** to ensure the model doesn’t look good on paper but fail the people it should care about.

---

## 🧪 Key ML Challenges Solved

| Challenge | How It Was Handled |
|---|---|
| Rare stroke events → **class imbalance** | **SMOTE** balancing during training |
| Mixed data + missing values | Imputation, scaling, one-hot encoding pipeline |
| “Black box” model decisions | Added **SHAP explainability plots + summaries** |
| Unrealistic predictions at inference | Logic-based overrides to fix impossible BMI/glucose/smoking conflicts |
| Fast, working deployment | Lightweight API design prioritising **easiest reliable method that works** |

---

## 🧬 What Users Provide vs What the Model Actually Uses

### 🧮 User Inputs (UI-level)
- 🎂 Age  
- 🚻 Gender  
- 🏠 Residence Type (Urban/Rural)  
- 💍 Ever Married (Yes/No)  
- 🚬 Smoking Status (Never/Former/Smokes/Unknown)  
- 💼 Work Type  
- ⚖️ Height + Weight → Auto-calculated *BMI*  
- 🩸 Average Glucose Level  
- ❤️ Hypertension, Heart Condition (diagnosed flags)  

### 🧬 What the model actually runs on (in pipeline)
- Engineered medical features + interactions like:
  - BMI ÷ age, glucose × BMI, age × BMI, glucose ÷ BMI
  - `senior_flag`, `smoker_flag`, `bmi_high_flag`, glucose quantiles  
- Final classifier: **XGBoost** with calibrated probabilities  
- Decision threshold optimised for **awareness-first, safety-first use**

---

## 🧩 Domain-Logic Safety (Layered after raw model predictions)

- 🚬 **Smoking increases risk score**, even if raw ML confidence is slightly low  
- ⚠ **Extreme BMI values are penalised upward** for sanity and responsibility  
- 🩸 **Very high glucose (e.g., >300 mg/dL) increases predicted risk**  
- ❔ **Unknown lifestyle/health inputs receive small risk buffers**  
- 🔁 Illogical or impossible medical combinations are corrected using rules, not retraining  

> The result is a model that is **strong overall, cautious on alerts, interpretable, and medically plausible even when trained on imperfect public data.**

---

## 🏗️ Architecture

```
User → Streamlit UI → FastAPI API → ML Pipeline → Domain Logic Safeguards → Back to UI
```

✔ **Fast**  
✔ **Interpretable**  
✔ **Medically sane**  
✔ **Honest about limits**  
✔ **Awareness-first, user-trust-first**

---

## 🛠️ Run Locally (Mac/Linux)

```bash
# 1. Clone the repository
git clone <YOUR_REPO_URL>

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start backend
uvicorn main:app --reload

# 5. Run frontend
streamlit run streamlit_app.py
```

---

## 📚 Dataset & Tools Used

- **Dataset:** Public stroke prediction data from Kaggle  
- **ML stack:** XGBoost, Scikit-Learn, SHAP, Imbalanced-Learn  
- **Deployment:** Render (API) + Streamlit Cloud (Frontend)  
- **Design standards considered:** WCAG AA contrast + <500ms latency goal  
- **Model focus:** Fastest reliable workflow instead of experimental over-engineering

---

## 🎓 Engineering Takeaways for College Reviewers

This project demonstrates:

✔ real ML pipeline building with class-imbalance handling  
✔ data preprocessing and inference-pipeline alignment  
✔ medically grounded reasoning layered over statistical modeling  
✔ model interpretability using SHAP (rare for high-school ML)  
✔ awareness of ethical limits, bias risks, and real-data limitations  
✔ ability to package, deploy, and document full-stack engineering systems

---

## 🌟 What I’ll Improve Next

- Support upgrade to **real clinical data** once accessible  
- Extend **recall** on rare-risk testing while keeping alerts precise  
- Maintain low prediction latency for batch input support

---

## ⚠ For Reviewers

This tool is:
- **Not a medical device**
- **Not a clinical diagnosis**

It **is**:
- A **rare-event ML inference system**
- A **public health awareness tool**
- A **CS/Data Science engineering portfolio artefact for admissions**

---

### Built with intent:  
**AI that helps humans *think earlier* about stroke risk, encourages real medical conversations, and shows that engineering systems can be both powerful and responsible — even when trained on imperfect open data.**
