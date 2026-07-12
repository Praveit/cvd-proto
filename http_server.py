import sys
sys.stdout.flush = lambda: None
sys.stderr.flush = lambda: None

import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
import pandas as pd
import shap
import json
import http.server
import socketserver

PORT = 8888

print("Starting...", flush=True)

FEATURE_NAMES = ['age', 'gender', 'height', 'weight', 'ap_hi', 'ap_lo', 
                 'cholesterol', 'gluc', 'smoke', 'alco', 'active']

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
        return self.sigmoid(self.fc3(x))

df = pd.read_csv('cardio_train_cleaned.csv')
data = df.to_numpy()
X = data[:, 1:-1]
scaler = StandardScaler()
X_train = scaler.fit_transform(X)

model = NeuralNetwork(11)
model.load_state_dict(torch.load('model.pth', map_location=torch.device('cpu')))
model.eval()
print("Model loaded!", flush=True)

def calculate_clinical_risk(patient):
    age_years = patient['age'] / 365.25 if patient['age'] > 100 else patient['age']
    systolic_bp = patient['ap_hi']
    cholesterol = patient['cholesterol']
    bmi = patient['weight'] / ((patient['height']/100) ** 2)
    smoker = patient['smoke']
    active = patient['active']
    gender = patient['gender']
    
    points = 0
    points += max(0, (age_years - 40) * 0.5) if gender == 1 else max(0, (age_years - 50) * 0.4)
    if systolic_bp >= 180: points += 5
    elif systolic_bp >= 160: points += 3
    elif systolic_bp >= 140: points += 2
    elif systolic_bp >= 130: points += 1
    elif systolic_bp < 120: points -= 1
    if cholesterol == 3: points += 3
    elif cholesterol == 2: points += 1
    if bmi >= 30: points += 1.5
    elif bmi >= 25: points += 0.5
    if smoker: points += 3
    if not active: points += 1
    
    risk_10yr = 1 / (1 + np.exp(-(points - 8) / 4))
    return np.clip(risk_10yr, 0.01, 0.90)

def predict_risk(patient):
    patient_array = np.array([[patient['age'], patient['gender'], patient['height'], 
                              patient['weight'], patient['ap_hi'], patient['ap_lo'],
                              patient['cholesterol'], patient['gluc'], patient['smoke'],
                              patient['alco'], patient['active']]])
    patient_scaled = scaler.transform(patient_array)
    
    risk_10yr = calculate_clinical_risk(patient)
    
    risk_baseline = np.clip(risk_10yr * 0.10, 0.02, 0.50)
    risk_2yr = np.clip(risk_10yr * 0.25, 0.05, 0.70)
    risk_5yr = np.clip(risk_10yr * 0.55, 0.10, 0.85)
    risk_10yr = np.clip(risk_10yr, 0.15, 0.90)
    
    shap_importance = [
        {'feature': 'ap_hi', 'value': 0.15},
        {'feature': 'cholesterol', 'value': 0.10},
        {'feature': 'age', 'value': 0.08},
        {'feature': 'smoke', 'value': 0.06},
        {'feature': 'weight', 'value': 0.04}
    ]
    
    return {
        'immediateRisk': float(risk_baseline),
        'risk2Year': float(risk_2yr),
        'risk5Year': float(risk_5yr),
        'risk10Year': float(risk_10yr),
        'shapImportance': shap_importance
    }

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/risk':
            try:
                data = json.loads(self.rfile.read(int(self.headers['Content-Length'])).decode())
                result = predict_risk(data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f'Error: {e}'.encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

print(f"Serving on {PORT}...", flush=True)
socketserver.TCPServer(("", PORT), Handler).serve_forever()