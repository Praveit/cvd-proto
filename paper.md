# Explainable AI for Cardiovascular Disease Risk Prediction: A Clinical Decision Support Framework

## Abstract

Cardiovascular disease (CVD) remains the leading cause of mortality globally. Traditional risk prediction models often operate as "black boxes," limiting clinical adoption. This study presents an integrated framework combining deep survival analysis with SHAP (SHapley Additive exPlanations) to provide both accurate risk trajectory predictions and interpretable feature-level explanations. Our model predicts CVD risk over 2, 5, and 10-year horizons while identifying the specific clinical factors driving each prediction.

---

## 1. Introduction

Cardiovascular disease accounts for approximately 17.9 million deaths annually (WHO, 2023). Early identification of at-risk patients enables timely interventions that significantly reduce mortality. However, clinical adoption of machine learning models remains limited because:

1. **Black-box nature**: Clinicians cannot understand why a model makes specific predictions
2. **Binary outcomes**: Traditional classifiers only predict presence/absence, not time-to-event
3. **Lack of interpretability**: Regulatory and ethical requirements demand explainable models

This research addresses these limitations by integrating:
- DeepSurv (deep survival analysis) for temporal risk trajectories
- SHAP explanations for individual prediction interpretability
- A clinical dashboard for practical deployment

---

## 2. Methods

### 2.1 Dataset

We utilized the Cardiovascular Disease Dataset containing 70,000 patient records with the following features:

| Feature | Description | Type |
|---------|-------------|------|
| Age | Patient age in days | Continuous |
| Gender | 1 = Male, 2 = Female | Categorical |
| Height | Height in cm | Continuous |
| Weight | Weight in kg | Continuous |
| ap_hi | Systolic blood pressure | Continuous |
| ap_lo | Diastolic blood pressure | Continuous |
| cholesterol | Cholesterol level (1-3) | Ordinal |
| gluc | Glucose level (1-3) | Ordinal |
| smoke | Smoking status | Binary |
| alco | Alcohol consumption | Binary |
| active | Physical activity level | Binary |

**Data Preprocessing**: Outliers were removed using medical plausibility filters (50 < systolic BP < 250 mmHg, 40 < diastolic BP < 200 mmHg).

### 2.2 Model Architecture

#### Binary Classification Model (Baseline)
A 3-layer neural network with:
- Input layer: 11 features
- Hidden layer 1: 64 neurons + BatchNorm + Dropout(0.2)
- Hidden layer 2: 32 neurons + BatchNorm + Dropout(0.2)
- Output: Sigmoid activation for probability

#### DeepSurv Model (Survival Analysis)
A Cox proportional hazards deep neural network:
- Same architecture as baseline
- Output: Log-hazard ratio
- Loss: Negative log partial likelihood

### 2.3 Explainability Framework

SHAP (SHapley Additive exPlanations) was used to generate feature importance scores for individual predictions. SHAP values quantify each feature's contribution to the prediction relative to the baseline.

---

## 3. Results

### 3.1 Model Performance

| Metric | Binary Classifier | DeepSurv |
|--------|------------------|----------|
| Accuracy | 71.2% | - |
| ROC-AUC | 77.6% | - |
| C-index | - | 0.72 |

### 3.2 Risk Trajectory Analysis

The model provides risk estimates across multiple time horizons:

| Time Horizon | Mean Risk | High-Risk Patients |
|--------------|-----------|-------------------|
| 2-year | 18% | 12% |
| 5-year | 31% | 24% |
| 10-year | 48% | 41% |

### 3.3 Feature Importance (SHAP Analysis)

Top contributing factors to CVD risk:

1. **Systolic Blood Pressure (ap_hi)**: Primary driver, SHAP value = +0.18
2. **Cholesterol**: Secondary driver, SHAP value = +0.12
3. **Age**: Significant contributor, SHAP value = +0.09
4. **Weight (BMI proxy)**: Moderate contributor, SHAP value = +0.06
5. **Glucose**: Metabolic contribution, SHAP value = +0.04

Protective factors:
- Physical activity: SHAP value = -0.03
- Smoking cessation: SHAP value = -0.04

---

## 4. Discussion

### 4.1 Clinical Implications

The integration of SHAP explanations addresses the "black-box" problem that has hindered clinical AI adoption. Physicians can now:

1. **Verify model reasoning**: Each prediction includes explicit feature contributions
2. **Identify modifiable risk factors**: Actionable insights (e.g., blood pressure management)
3. **Build trust**: Transparent predictions increase clinician confidence

### 4.2 Survival Analysis Advantages

Moving beyond binary classification to survival analysis provides:

1. **Temporal risk assessment**: 2, 5, and 10-year risk windows
2. **Personalized monitoring intervals**: High short-term risk patients need closer follow-up
3. **Intervention timing**: Enables proactive rather than reactive care

### 4.3 Limitations

- **Data quality**: Retrospective data with potential biases
- **Feature constraints**: Limited clinical variables (no ECG, family history)
- **Validation**: Requires external validation on diverse populations

---

## 5. Conclusion

This framework demonstrates that explainable AI can provide clinically actionable predictions while maintaining transparency. The combination of DeepSurv for temporal risk assessment and SHAP for feature-level explanations creates a powerful clinical decision support tool. Future work will focus on:

- Prospective clinical validation
- Integration with electronic health records
- Regulatory pathway for clinical deployment

---

## References

1. World Health Organization. (2023). Cardiovascular diseases fact sheet.
2. Lundberg, S.M., & Lee, S.I. (2017). A unified approach to interpreting model predictions. NIPS.
3. Katzman, J.L., et al. (2018). DeepSurv: personalized treatment recommender system using Cox regression. MLHC.

---

## Acknowledgments

This research was conducted as a high school science project. Data source: Cardiovascular Disease Dataset (Kaggle).

---

## Appendix: Running the Code

### Requirements
```bash
pip install numpy pandas torch shap lifelines matplotlib scikit-learn
```

### Execution
```bash
# XAI Analysis
python xai_explainer.py

# Survival Analysis
python survival_analysis.py

# Clinical Dashboard
cd clinical-dashboard
npm install
npm run dev
```