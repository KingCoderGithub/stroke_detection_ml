# metrics_report.py
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from sklearn.metrics import (
    precision_recall_curve,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.calibration import calibration_curve

# ---------- CONFIG ----------
MODEL_PATH = "xgb_pipe.joblib"          # your trained pipeline
DATA_PATH = "stroke_data.csv"           # dataset with 'stroke' target
OUTPUT_DIR = Path("reports")            # where plots + summary will be saved
TARGET_COLS = ["stroke", "target", "label"]  # possible target names
THRESHOLD = 0.34  # 🔧 set this to the same threshold you use in your FastAPI backend
# -----------------------------

OUTPUT_DIR.mkdir(exist_ok=True)

print("Loading model...")
model = joblib.load(MODEL_PATH)

print("Loading data...")
df = pd.read_csv(DATA_PATH)

# Detect target column
target_col = None
for col in TARGET_COLS:
    if col in df.columns:
        target_col = col
        break

if target_col is None:
    raise RuntimeError(
        f"Could not find target column. Checked: {TARGET_COLS}. "
        "Update TARGET_COLS or your CSV."
    )

print(f"Using target column: {target_col}")

y = df[target_col].values
X = df.drop(columns=[target_col])

print(f"Data shape: X={X.shape}, y={y.shape}")

print("Getting model predictions...")
# Pipeline will handle feature engineering + preprocessing internally
y_proba = model.predict_proba(X)[:, 1]
y_pred = (y_proba >= THRESHOLD).astype(int)

# ---------- METRICS ----------
print("Computing metrics...")
precision, recall, _ = precision_recall_curve(y, y_proba)
pr_auc = average_precision_score(y, y_proba)

f1 = f1_score(y, y_pred)
prec_bin = precision_score(y, y_pred)
recall_bin = recall_score(y, y_pred)
cm = confusion_matrix(y, y_pred)

# Calibration curve
frac_pos, mean_pred = calibration_curve(y, y_proba, n_bins=10)

# ---------- SAVE METRICS SUMMARY ----------
summary_lines = [
    "MODEL VALIDATION METRICS",
    "========================",
    f"Threshold used: {THRESHOLD:.2f}",
    "",
    f"PR AUC (average precision): {pr_auc:.4f}",
    f"F1 score:                   {f1:.4f}",
    f"Precision (binary):         {prec_bin:.4f}",
    f"Recall (binary):            {recall_bin:.4f}",
    "",
    "Confusion matrix (rows=true, cols=pred):",
    f"TN: {cm[0,0]}   FP: {cm[0,1]}",
    f"FN: {cm[1,0]}   TP: {cm[1,1]}",
]

summary_text = "\n".join(summary_lines)
summary_path = OUTPUT_DIR / "metrics_summary.txt"
with open(summary_path, "w") as f:
    f.write(summary_text)

print("\n" + summary_text)
print(f"\nSaved metrics summary to: {summary_path}")

# ---------- PLOTS ----------

# 1) Precision–Recall curve
print("Saving precision–recall curve...")
plt.figure()
plt.plot(recall, precision, linewidth=2)
plt.xlabel("Recall")
plt.ylabel("Precision")
plt.title(f"Precision–Recall Curve (AP = {pr_auc:.3f})")
plt.grid(True, linestyle="--", alpha=0.5)
pr_path = OUTPUT_DIR / "pr_curve.png"
plt.tight_layout()
plt.savefig(pr_path, dpi=200)
plt.close()

# 2) Confusion matrix heatmap
print("Saving confusion matrix heatmap...")
plt.figure()
im = plt.imshow(cm, interpolation="nearest")
plt.title("Confusion Matrix")
plt.colorbar(im, fraction=0.046, pad=0.04)
classes = ["No stroke", "Stroke"]

tick_marks = np.arange(len(classes))
plt.xticks(tick_marks, ["Pred 0", "Pred 1"])
plt.yticks(tick_marks, ["True 0", "True 1"])

thresh = cm.max() / 2.0
for i in range(cm.shape[0]):
    for j in range(cm.shape[1]):
        plt.text(
            j, i, format(cm[i, j], "d"),
            horizontalalignment="center",
            verticalalignment="center",
            color="white" if cm[i, j] > thresh else "black",
        )

plt.ylabel("True label")
plt.xlabel("Predicted label")
cm_path = OUTPUT_DIR / "confusion_matrix.png"
plt.tight_layout()
plt.savefig(cm_path, dpi=200)
plt.close()

# 3) Calibration curve
print("Saving calibration curve...")
plt.figure()
plt.plot([0, 1], [0, 1], "k--", linewidth=1)
plt.plot(mean_pred, frac_pos, marker="o", linewidth=2)
plt.xlabel("Mean predicted probability")
plt.ylabel("Fraction of positives")
plt.title("Calibration Curve")
plt.grid(True, linestyle="--", alpha=0.5)
cal_path = OUTPUT_DIR / "calibration_curve.png"
plt.tight_layout()
plt.savefig(cal_path, dpi=200)
plt.close()

print("\nSaved plots:")
print(f" - {pr_path}")
print(f" - {cm_path}")
print(f" - {cal_path}")
print("\nAll done ✅")
