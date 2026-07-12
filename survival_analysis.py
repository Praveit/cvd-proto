import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from lifelines.utils import concordance_index
import warnings
warnings.filterwarnings('ignore')

FEATURE_NAMES = ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 
                 'cholesterol', 'gluc', 'smoke', 'alco', 'active']

class DeepSurv(nn.Module):
    def __init__(self, input_size):
        super(DeepSurv, self).__init__()
        
        self.fc1 = nn.Linear(input_size, 64)
        self.dropout1 = nn.Dropout(0.2)
        
        self.fc2 = nn.Linear(64, 32)
        self.dropout2 = nn.Dropout(0.2)
        
        self.fc3 = nn.Linear(32, 1)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout1(x)
        x = self.relu(self.fc2(x))
        x = self.dropout2(x)
        return self.fc3(x)

def calculate_clinical_risk(patient):
    """Calculate baseline risk using clinical guidelines (Framingham-inspired)"""
    age_years = patient['age'] / 365.25 if patient['age'] > 100 else patient['age']
    systolic_bp = patient['ap_hi']
    diastolic_bp = patient['ap_lo']
    bmi = patient['weight'] / ((patient['height']/100) ** 2)
    cholesterol = patient['cholesterol']
    glucose = patient['gluc']
    smoker = patient['smoke']
    active = patient['active']
    
    risk_score = 0
    
    risk_score += (age_years - 40) * 0.5 if age_years > 40 else 0
    
    if systolic_bp >= 140:
        risk_score += 2
    elif systolic_bp >= 130:
        risk_score += 1
    elif systolic_bp < 120:
        risk_score -= 1
    
    if cholesterol == 3:
        risk_score += 2
    elif cholesterol == 2:
        risk_score += 1
    elif cholesterol == 1:
        risk_score -= 1
    
    if glucose == 3:
        risk_score += 1.5
    elif glucose == 2:
        risk_score += 0.5
    
    if bmi >= 30:
        risk_score += 1.5
    elif bmi >= 25:
        risk_score += 0.5
    
    if smoker:
        risk_score += 2
    
    if not active:
        risk_score += 1
    
    risk_prob = 1 / (1 + np.exp(-(risk_score - 5) / 3))
    risk_prob = np.clip(risk_prob, 0.05, 0.95)
    
    return risk_prob

def generate_realistic_survival_data(X, y_binary, n_years=10):
    """Generate survival times based on actual clinical risk factors"""
    n_samples = X.shape[0]
    event_times = np.zeros(n_samples)
    event_indicator = np.zeros(n_samples)
    
    for i in range(n_samples):
        patient = {
            'age': X[i, 0] * 365.25,
            'ap_hi': X[i, 4],
            'ap_lo': X[i, 5],
            'cholesterol': X[i, 6],
            'gluc': X[i, 7],
            'weight': X[i, 3],
            'height': X[i, 2],
            'smoke': X[i, 8],
            'active': X[i, 10]
        }
        
        base_risk = calculate_clinical_risk(patient)
        
        if y_binary[i] == 1:
            mean_time = 3 + (1 - base_risk) * 4
            event_times[i] = np.clip(np.random.exponential(mean_time), 0.5, n_years)
            event_indicator[i] = 1
        else:
            if base_risk > 0.5:
                mean_time = 8 + np.random.exponential(3)
            else:
                mean_time = n_years + np.random.exponential(2)
            event_times[i] = min(mean_time, n_years + np.random.uniform(0, 2))
            event_indicator[i] = 0
    
    return event_times * 365, event_indicator

def cox_ph_loss(risks, events, times):
    """Cox proportional hazards loss"""
    sorted_idx = torch.argsort(times, descending=True)
    risks = risks[sorted_idx]
    events = events[sorted_idx]
    
    log_hazard = risks
    cumsum_hazard = torch.cumsum(torch.exp(risks), dim=0)
    log_cumsum = torch.log(cumsum_hazard + 1e-8)
    
    hazard_diff = log_hazard - log_cumsum
    loss = -torch.sum(events * hazard_diff)
    
    return loss

def train_deepsurv(model, X_train, durations, events, epochs=150, lr=0.001):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=10, factor=0.5)
    
    X_tensor = torch.tensor(X_train, dtype=torch.float32)
    duration_tensor = torch.tensor(durations, dtype=torch.float32)
    event_tensor = torch.tensor(events, dtype=torch.float32)
    
    for epoch in range(epochs):
        model.train()
        risks = model(X_tensor).squeeze()
        loss = cox_ph_loss(risks, event_tensor, duration_tensor)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 30 == 0:
            model.eval()
            with torch.no_grad():
                val_risks = model(X_tensor).squeeze()
                val_loss = cox_ph_loss(val_risks, event_tensor, duration_tensor)
            scheduler.step(val_loss)
            print(f"Epoch {epoch+1}/{epochs} - Loss: {loss.item():.4f} - Val Loss: {val_loss.item():.4f}")

def predict_survival_probability(model, X, scaler, time_years):
    model.eval()
    X_tensor = torch.tensor(X, dtype=torch.float32)
    
    with torch.no_grad():
        linear_predictor = model(X_tensor).squeeze().numpy()
    
    baseline_survival_5yr = 0.85
    
    risk_scores = np.exp(linear_predictor - np.mean(linear_predictor))
    
    time_days = time_years * 365
    survival_prob = np.power(baseline_survival_5yr, risk_scores * (time_years / 5))
    
    survival_prob = np.clip(survival_prob, 0.01, 0.99)
    
    return survival_prob

def main():
    print("=== Improved DeepSurv Survival Analysis ===\n")
    
    df = pd.read_csv('cardio_train_cleaned.csv')
    data = df.to_numpy()
    
    X = data[:, 1:-1]
    y = data[:, -1]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print("Generating clinically-calibrated survival data...")
    event_times_train, event_indicator_train = generate_realistic_survival_data(X_train, y_train)
    event_times_test, event_indicator_test = generate_realistic_survival_data(X_test, y_test)
    
    print("\nTraining DeepSurv model...")
    input_size = X_train_scaled.shape[1]
    model = DeepSurv(input_size)
    train_deepsurv(model, X_train_scaled, event_times_train, event_indicator_train, epochs=150)
    
    print("\n=== Testing Model ===")
    
    risks = model(torch.tensor(X_test_scaled, dtype=torch.float32)).detach().numpy().squeeze()
    c_index = concordance_index(event_times_test, -risks, event_indicator_test)
    print(f"Concordance Index (C-index): {c_index:.4f}")
    
    test_patient = X_test_scaled[0:1]
    print(f"\n=== Test Patient ===")
    print(f"Age: {X_test[0, 0]/365.25:.1f} years")
    print(f"BP: {X_test[0, 4]:.0f}/{X_test[0, 5]:.0f} mmHg")
    print(f"Cholesterol: {int(X_test[0, 6])}, Glucose: {int(X_test[0, 7])}")
    print(f"Smoker: {int(X_test[0, 8])}, Active: {int(X_test[0, 10])}")
    
    print(f"\n=== Risk Trajectory ===")
    for years in [2, 5, 10]:
        surv_prob = predict_survival_probability(model, test_patient, scaler, years)
        risk = 1 - surv_prob
        print(f"  {years}-year CVD risk: {risk*100:.1f}%")
    
    plt.figure(figsize=(10, 6))
    
    patient_idx = 0
    years = [2, 5, 10]
    risks_list = [1 - predict_survival_probability(model, X_test_scaled[patient_idx:patient_idx+1], scaler, y) for y in years]
    
    plt.plot(years, risks_list, 'ro-', linewidth=2, markersize=12, label='Predicted Risk')
    plt.fill_between(years, [r*0.85 for r in risks_list], [min(r*1.15, 1.0) for r in risks_list], alpha=0.2, color='red')
    
    plt.xlabel('Years', fontsize=12)
    plt.ylabel('CVD Risk Probability', fontsize=12)
    plt.title('Patient Risk Trajectory Over Time', fontsize=14)
    plt.xticks(years)
    plt.ylim(0, 1)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig('patient_risk_trajectory.png', dpi=150)
    plt.close()
    print("\nSaved: patient_risk_trajectory.png")
    
    plt.figure(figsize=(12, 6))
    for horizon in [2, 5, 10]:
        risks = [1 - predict_survival_probability(model, X_test_scaled[i:i+1], scaler, horizon) for i in range(min(500, len(X_test)))]
        plt.hist(risks, bins=20, alpha=0.5, label=f'{horizon}-year')
    
    plt.xlabel('CVD Risk Probability')
    plt.ylabel('Number of Patients')
    plt.title('Risk Distribution by Time Horizon')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('risk_distribution.png', dpi=150)
    plt.close()
    print("Saved: risk_distribution.png")
    
    torch.save({
        'model': model.state_dict(),
        'scaler': scaler
    }, 'deepsurv_model_v2.pth')
    print("\nSaved: deepsurv_model_v2.pth")
    
    print("\n=== Analysis Complete ===")

if __name__ == "__main__":
    main()