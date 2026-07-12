import sys
import json
import numpy as np

def calculate_clinical_risk(patient):
    """Calculate 10-year CVD risk with proper clinical weighting"""
    age_years = patient['age'] / 365.25 if patient['age'] > 100 else patient['age']
    systolic_bp = patient['ap_hi']
    diastolic_bp = patient['ap_lo']
    cholesterol = patient['cholesterol']
    glucose = patient['gluc']
    bmi = patient['weight'] / ((patient['height']/100) ** 2)
    smoker = patient['smoke']
    alco = patient['alco']
    active = patient['active']
    gender = patient['gender']
    
    points = 0
    feature_contributions = {
        'age': 0, 'ap_hi': 0, 'ap_lo': 0, 'cholesterol': 0, 
        'gluc': 0, 'weight': 0, 'smoke': 0, 'alco': 0, 'active': 0, 'gender': 0
    }
    
    # Age points - more aggressive for older patients
    if gender == 1:  # Male
        if age_years >= 65: points += 10; feature_contributions['age'] = 10
        elif age_years >= 60: points += 8; feature_contributions['age'] = 8
        elif age_years >= 55: points += 6; feature_contributions['age'] = 6
        elif age_years >= 50: points += 4; feature_contributions['age'] = 4
        elif age_years >= 45: points += 2; feature_contributions['age'] = 2
        elif age_years >= 40: points += 1; feature_contributions['age'] = 1
    else:  # Female
        if age_years >= 65: points += 8; feature_contributions['age'] = 8
        elif age_years >= 60: points += 6; feature_contributions['age'] = 6
        elif age_years >= 55: points += 4; feature_contributions['age'] = 4
        elif age_years >= 50: points += 2; feature_contributions['age'] = 2
        elif age_years >= 45: points += 1; feature_contributions['age'] = 1
    
    # Blood pressure points - VERY aggressive for hypertensive crisis
    if systolic_bp >= 180:
        points += 10; feature_contributions['ap_hi'] = 10  # Hypertensive crisis
    elif systolic_bp >= 160:
        points += 7; feature_contributions['ap_hi'] = 7   # Stage 2 hypertension
    elif systolic_bp >= 140:
        points += 4; feature_contributions['ap_hi'] = 4   # Stage 1 hypertension
    elif systolic_bp >= 130:
        points += 2; feature_contributions['ap_hi'] = 2   # Elevated
    elif systolic_bp < 120:
        points -= 1; feature_contributions['ap_hi'] = -1  # Normal (protective)
    
    # Diastolic BP penalty
    if diastolic_bp >= 120:
        points += 5; feature_contributions['ap_lo'] = 5   # Hypertensive crisis
    elif diastolic_bp >= 100:
        points += 3; feature_contributions['ap_lo'] = 3
    
    # Cholesterol - well above normal is very high risk
    if cholesterol == 3:
        points += 5; feature_contributions['cholesterol'] = 5   # Well above normal
    elif cholesterol == 2:
        points += 2; feature_contributions['cholesterol'] = 2   # Above normal
    
    # Glucose/diabetes risk
    if glucose == 3:
        points += 4; feature_contributions['gluc'] = 4   # Diabetic
    elif glucose == 2:
        points += 2; feature_contributions['gluc'] = 2   # Pre-diabetic
    
    # BMI - extreme obesity is a major risk factor
    if bmi >= 40:
        points += 6; feature_contributions['weight'] = 6   # Extreme obesity (class III)
    elif bmi >= 35:
        points += 4; feature_contributions['weight'] = 4   # Class II
    elif bmi >= 30:
        points += 3; feature_contributions['weight'] = 3   # Class I
    elif bmi >= 25:
        points += 1; feature_contributions['weight'] = 1   # Overweight
    
    # Smoking - MAJOR risk factor
    if smoker:
        points += 5; feature_contributions['smoke'] = 5
    else:
        feature_contributions['smoke'] = 0
    
    # Alcohol
    if alco:
        points += 2; feature_contributions['alco'] = 2
    else:
        feature_contributions['alco'] = 0
    
    # Physical activity (protective)
    if not active:
        points += 2; feature_contributions['active'] = 2
    else:
        feature_contributions['active'] = -1  # protective
    
    # Gender (protective for females)
    if gender == 2:  # Female
        feature_contributions['gender'] = -1
    else:
        feature_contributions['gender'] = 0
    
    # Convert points to risk probability
    risk = 0.05 + (points / 35.0) * 0.45
    risk = np.clip(risk, 0.02, 0.75)
    
    return risk, feature_contributions


def compute_shap_importance(feature_contributions, risk_score):
    """Convert feature contributions to SHAP-like values that sum to risk deviation from baseline"""
    baseline_risk = 0.15  # approximate baseline
    risk_deviation = risk_score - baseline_risk
    
    total_abs_contrib = sum(abs(v) for v in feature_contributions.values())
    if total_abs_contrib == 0:
        return [{'feature': k, 'value': 0.0} for k in feature_contributions.keys()]
    
    # Normalize contributions to match risk deviation
    shap_values = []
    for feature, contrib in feature_contributions.items():
        # Scale contribution to match the actual risk deviation
        shap_val = (contrib / total_abs_contrib) * risk_deviation if total_abs_contrib > 0 else 0
        shap_values.append({'feature': feature, 'value': float(shap_val)})
    
    # Sort by absolute value descending
    shap_values.sort(key=lambda x: abs(x['value']), reverse=True)
    return shap_values[:6]  # Top 6 features

def main():
    patient_data = sys.stdin.read()
    patient = json.loads(patient_data)
    
    risk_10yr, feature_contributions = calculate_clinical_risk(patient)
    
    # Risk increases over time: baseline < 2yr < 5yr < 10yr
    risk_baseline = risk_10yr * 0.15
    risk_2yr = risk_10yr * 0.35
    risk_5yr = risk_10yr * 0.70
    
    risk_baseline = np.clip(risk_baseline, 0.01, 0.50)
    risk_2yr = np.clip(risk_2yr, 0.05, 0.60)
    risk_5yr = np.clip(risk_5yr, 0.10, 0.70)
    risk_10yr = np.clip(risk_10yr, 0.15, 0.75)
    
    shap_importance = compute_shap_importance(feature_contributions, risk_10yr)
    
    result = {
        'immediateRisk': float(risk_baseline),
        'risk2Year': float(risk_2yr),
        'risk5Year': float(risk_5yr),
        'risk10Year': float(risk_10yr),
        'shapImportance': shap_importance
    }
    
    print(json.dumps(result))

if __name__ == "__main__":
    main()