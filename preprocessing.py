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

def feature_engineering(df):
    df = df.copy()
    
    df['age_group'] = pd.cut(
        df['age'],
        bins=[0, 18, 30, 45, 60, 80, 120],
        labels=['child', 'young_adult', 'adult', 'middle_aged', 'senior', 'elderly']
    )

    df["bmi"] = df["bmi"].astype(float)  # safety

    df["bmi_category"] = pd.cut(
        df["bmi"],
        bins=[-1, 18.5, 25, 30, 35, 40, 45, float("inf")],
        labels=["Underweight", "Normal", "Overweight", "Obese I", "Obese II", "Obese III", "Extreme"],
        duplicates="drop"
    )

    q1, q2, q3 = df['avg_glucose_level'].quantile([0.25, 0.5, 0.75])
    
    # Ensure uniqueness in glucose bins
    glucose_bins = sorted(set([-1, q1, q2, q3, np.inf]))
    if len(glucose_bins) - 1 != 4:
        glucose_labels = [f"Q{i+1}" for i in range(len(glucose_bins)-1)]
    else:
        glucose_labels = ['low', 'med_low', 'med_high', 'high']
    
    df['glucose_q'] = pd.cut(
        df['avg_glucose_level'],
        bins=glucose_bins,
        labels=glucose_labels
    )

    df['smoker_flag'] = df['smoking_status'].replace({
    'Smokes': 1, 'Formerly smoked': 1, 'Never smoked': 0, 'Unknown': 0
    }).astype("int64")


    df['senior_flag'] = (df['age'] >= 65).astype(int)
    df['bmi_high_flag'] = (df['bmi'] >= 30).astype(int)
    df['glucose_high_flag'] = (df['avg_glucose_level'] > q3).astype(int)
    df['cardio_flag'] = ((df['hypertension'] == 1) | (df['heart_disease'] == 1)).astype(int)

    df['age_squared'] = df['age'] ** 2

    # Cap BMI to reduce extreme influence
    bmi_capped = np.minimum(df['bmi'], 50)

    # Interaction terms
    df['bmi_age_ratio'] = bmi_capped / (df['age'] + 1)
    df['glucose_bmi_ratio'] = df['avg_glucose_level'] / (bmi_capped + 1)
    df['bmi_smoker_interaction'] = bmi_capped * df['smoker_flag']
    df['age_bmi_interaction'] = df['age'] * bmi_capped
    df['age_glucose_interaction'] = df['age'] * df['avg_glucose_level']
    df['age_smoker_interaction'] = df['age'] * df['smoker_flag']

    df['risk_score'] = (
        df['smoker_flag'] * 1.5 +
        df['bmi_high_flag'] * 1.2 +
        df['glucose_high_flag'] * 1.4 +
        df['cardio_flag'] * 1.7 +
        df['senior_flag'] * 1.3
    )

    return df
