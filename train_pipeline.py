# train_pipeline.py

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.impute import SimpleImputer
from preprocessing import feature_engineering

XGBClassifier
# Load data
df = pd.read_csv("stroke_data.csv")

# Drop unused or inconsistent columns
if "id" in df.columns:
    df = df.drop(columns=["id"])

# Recode rare work_type categories
df['work_type'] = df['work_type'].replace({
    'Never_worked': 'Other',
    'children': 'Other'
})


# Train-test split
X = df.drop("stroke", axis=1)
y = df["stroke"]

X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

def preprocess_pipe():
    engineered = feature_engineering(X_train)

    cat = engineered.select_dtypes(include=["object", "category"]).columns.tolist()
    num = engineered.select_dtypes(include=["int64", "float64"]).columns.tolist()

    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    return ColumnTransformer([
        ("num", num_pipeline, num),
        ("cat", cat_pipeline, cat)
    ])
    

# Full pipeline
pipe = ImbPipeline(steps=[
    ("feature_engineering", FunctionTransformer(feature_engineering)),
    ("preprocessing", preprocess_pipe()),
    ("smote", SMOTE(random_state=42)),
    ("model", XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    use_label_encoder=False,
    random_state=42,
    max_depth=3,              # reduce tree complexity
    min_child_weight=2,
    gamma=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,            # L1 regularization
    reg_lambda=1.0            # L2 regularization
    ))
    
])
drop_cols = ['id', 'work_type']  # any others you don’t need

drop_cols = ['id']
drop_cols = [col for col in drop_cols if col in df.columns]
X = df.drop(columns=['stroke'] + drop_cols)

y = df['stroke']




# Fit and save
pipe.fit(X_train, y_train)

joblib.dump(pipe, "xgb_pipe.joblib")

# Save threshold (optional)
import json
probs = pipe.predict_proba(X_test)[:, 1]
threshold = 0.3
json.dump({"threshold": threshold}, open("model_meta.json", "w"))

print("Incoming columns:", df.columns.tolist())

