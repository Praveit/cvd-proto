import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class NeuralNetwork(nn.Module):
    def __init__(self, input_size):
        super(NeuralNetwork, self).__init__()
        
        self.fc1 = nn.Linear(input_size, 64)
        self.dropout1 = nn.Dropout(0.2)
        
        self.fc2 = nn.Linear(64, 32)
        self.dropout2 = nn.Dropout(0.2)
        
        self.fc3 = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout1(x)
        x = self.relu(self.fc2(x))
        x = self.dropout2(x)
        x = self.sigmoid(self.fc3(x))
        return x

FEATURE_NAMES = ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 
                 'cholesterol', 'gluc', 'smoke', 'alco', 'active']

def prepare_data():
    df = pd.read_csv('cardio_train_cleaned.csv')
    data = df.to_numpy()
    
    X = data[:, 1:-1]
    y = data[:, -1]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    return X_train, X_test, y_train, y_test, scaler

def load_model(input_size, model_path='model.pth'):
    model = NeuralNetwork(input_size)
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

def predict_wrapper(X):
    X_tensor = torch.tensor(X, dtype=torch.float32)
    with torch.no_grad():
        predictions = model(X_tensor)
    return predictions.numpy()

model, X_train, X_test, y_train, y_test, scaler = None, None, None, None, None, None

def main():
    global model, X_train, X_test, y_train, y_test, scaler
    
    print("Loading data...")
    X_train, X_test, y_train, y_test, scaler = prepare_data()
    
    print("Loading model...")
    input_size = X_train.shape[1]
    model = load_model(input_size)
    
    print("\n=== SHAP Explainability Analysis ===\n")
    
    X_train_df = pd.DataFrame(X_train, columns=FEATURE_NAMES)
    X_test_df = pd.DataFrame(X_test, columns=FEATURE_NAMES)
    
    background = shap.sample(X_train, 100, random_state=42)
    
    print("Computing SHAP values...")
    explainer = shap.KernelExplainer(predict_wrapper, background)
    
    X_sample = shap.sample(X_test, 50, random_state=42)
    shap_values = explainer.shap_values(X_sample)
    
    plt.figure(figsize=(12, 8))
    shap.summary_plot(shap_values, X_sample, feature_names=FEATURE_NAMES, show=False)
    plt.tight_layout()
    plt.savefig('shap_summary_plot.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: shap_summary_plot.png (global feature importance)")
    
    patient_idx = 0
    patient_data = X_test[patient_idx:patient_idx+1]
    patient_shap = shap_values[patient_idx]
    if patient_shap.ndim > 1:
        patient_shap = patient_shap.flatten()
    
    plt.figure(figsize=(10, 6))
    feature_importance = pd.DataFrame({
        'Feature': FEATURE_NAMES,
        'SHAP Value': patient_shap
    }).sort_values('SHAP Value', key=abs, ascending=True)
    
    colors = ['red' if x < 0 else 'blue' for x in feature_importance['SHAP Value']]
    plt.barh(feature_importance['Feature'], feature_importance['SHAP Value'], color=colors)
    plt.xlabel('SHAP Value (Impact on Prediction)')
    plt.title(f'Patient #{patient_idx} - Feature Contribution to CVD Risk\nPredicted Risk: {predict_wrapper(patient_data)[0][0]*100:.1f}%')
    plt.axvline(x=0, color='gray', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    plt.savefig('patient_shap_explanation.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: patient_shap_explanation.png (individual patient #{patient_idx})")
    
    patient_shap_flat = patient_shap.flatten() if patient_shap.ndim > 1 else patient_shap
    top_features = sorted(zip(FEATURE_NAMES, patient_shap_flat), key=lambda x: abs(x[1]), reverse=True)[:5]
    print("\nTop 5 Contributing Factors for Patient #0:")
    for feature, value in top_features:
        direction = "increases" if value > 0 else "decreases"
        print(f"  {feature}: {value:+.4f} - {direction} CVD risk")
    
    risk_prob = predict_wrapper(patient_data)
    if risk_prob.ndim > 1:
        risk_prob = risk_prob.flatten()
    risk_prob = risk_prob[0]
    print(f"\nPatient #0 Predicted CVD Risk: {risk_prob*100:.1f}%")
    print(f"Actual Outcome: {'Positive' if y_test[patient_idx] == 1 else 'Negative'}")

    print("\n=== Explanation Complete ===")
    print("Generated files:")
    print("  - shap_summary_plot.png (global feature importance)")
    print("  - patient_shap_explanation.png (individual patient explanation)")

if __name__ == "__main__":
    main()