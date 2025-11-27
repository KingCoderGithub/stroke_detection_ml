# shap_report.py
import joblib
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# ---------- CONFIG ----------
MODEL_PATH = "xgb_pipe.joblib"      # your trained pipeline
DATA_PATH = "stroke_data.csv"       # your original dataset
OUTPUT_DIR = Path("reports")        # where plots will be saved
MAX_BACKGROUND = 500                # rows to use for SHAP background
TARGET_COLS = ["stroke", "target", "label"]  # possible target names
# -----------------------------

OUTPUT_DIR.mkdir(exist_ok=True)

print("Loading model...")
model = joblib.load(MODEL_PATH)

print("Loaded model type:", type(model))

if not (isinstance(model, Pipeline) or hasattr(model, "steps")):
    raise RuntimeError(
        "Loaded model is not a sklearn/imbalanced-learn Pipeline. "
        "This script assumes a Pipeline with a ColumnTransformer and a tree-based final model."
    )

print("\nPipeline steps:")
for name, step in model.steps:
    print(f" - {name}: {type(step)}")

print("\nLoading data...")
df = pd.read_csv(DATA_PATH)

# Drop target column if present
for col in TARGET_COLS:
    if col in df.columns:
        print(f"Dropping target column: {col}")
        df = df.drop(columns=[col])
        break

# Sample background data
X_raw = df.sample(min(len(df), MAX_BACKGROUND), random_state=42)
print(f"Using {X_raw.shape[0]} rows and {X_raw.shape[1]} raw features for background")

# ---------- Find the preprocessor (ColumnTransformer) and final model ----------
preprocessor = None
for name, step in model.steps:
    if isinstance(step, ColumnTransformer):
        preprocessor = step
        print(f"\nDetected ColumnTransformer as preprocessor: step '{name}'")
        break

if preprocessor is None:
    # Fallback: first step that has a transform method
    for name, step in model.steps:
        if hasattr(step, "transform"):
            preprocessor = step
            print(f"\nNo ColumnTransformer found; using first transform-capable step: '{name}'")
            break

if preprocessor is None:
    raise RuntimeError(
        "Could not find a preprocessing step with .transform() in the pipeline."
    )

# final model = last step (e.g., XGBClassifier)
final_step_name, final_model = model.steps[-1]
print(f"Detected final model step '{final_step_name}': {type(final_model)}")

# ---------- Transform data ----------
print("\nTransforming data through preprocessor...")
print("\nTransforming data through full pipeline (including feature engineering + SMOTE-safe path)…")
X_trans = model.named_steps["preprocessing"].transform(
    model.named_steps["feature_engineering"].transform(X_raw)
)

# Convert to dense array if sparse
if hasattr(X_trans, "toarray"):
    X_dense = X_trans.toarray()
else:
    X_dense = np.asarray(X_trans)

n_features = X_dense.shape[1]
print(f"Transformed data shape: {X_dense.shape}")

# Use generic feature names (we don't have the expanded one-hot names here)
feature_names = [f"feature_{i}" for i in range(n_features)]

# ---------- Build SHAP TreeExplainer on the final model ----------
print("\nBuilding SHAP TreeExplainer...")
explainer = shap.TreeExplainer(final_model)

print("Computing SHAP values (this may take a bit)...")
shap_values = explainer(X_dense)  # for binary classification: (n_samples, n_features)

# ---------- SUMMARY PLOT ----------
print("\nSaving SHAP summary plot...")
plt.figure(figsize=(8, 6))
shap.summary_plot(shap_values, X_dense, feature_names=feature_names, show=False)
plt.tight_layout()
summary_path = OUTPUT_DIR / "shap_summary.png"
plt.savefig(summary_path, dpi=200)
plt.close()

# ---------- FORCE PLOT FOR ONE EXAMPLE ----------
print("Saving SHAP force plot for one example...")
row_idx = 0
shap_row = shap_values[row_idx]
x_row = X_dense[row_idx]

shap.plots.force(shap_row, x_row, feature_names=feature_names, matplotlib=True, show=False)
plt.tight_layout()
force_path = OUTPUT_DIR / "shap_force_example_0.png"
plt.savefig(force_path, dpi=200)
plt.close()

print("\nDone!")
print(f"Summary plot: {summary_path}")
print(f"Force plot:   {force_path}")
