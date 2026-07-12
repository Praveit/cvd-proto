import http.server
import socketserver
import json
import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
import pandas as pd
import shap
import os
import webbrowser
from threading import Thread
import sys

PORT = 8000

print("Starting server...", file=sys.stderr)
print(f"Python: {sys.version}", file=sys.stderr)

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
        x = self.sigmoid(self.fc3(x))
        return x

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

print("Loading models...")
model = NeuralNetwork(11)
model.load_state_dict(torch.load('model.pth', map_location=torch.device('cpu')))
model.eval()

deepsurv = DeepSurv(11)
deepsurv.load_state_dict(torch.load('deepsurv_model.pth', map_location=torch.device('cpu')))
deepsurv.eval()

df = pd.read_csv('cardio_train_cleaned.csv')
data = df.to_numpy()
X = data[:, 1:-1]
scaler = StandardScaler()
X_train = scaler.fit_transform(X)

def predict_risk(patient):
    patient_array = np.array([[patient['age'], patient['gender'], patient['height'], 
                              patient['weight'], patient['ap_hi'], patient['ap_lo'],
                              patient['cholesterol'], patient['gluc'], patient['smoke'],
                              patient['alco'], patient['active']]])
    patient_scaled = scaler.transform(patient_array)
    
    with torch.no_grad():
        risk_prob = model(torch.tensor(patient_scaled, dtype=torch.float32)).item()
        hazard = deepsurv(torch.tensor(patient_scaled, dtype=torch.float32)).item()
    
    hazards = np.exp(hazard)
    risk_2yr = 1 - (0.95 ** (hazards * 2))
    risk_5yr = 1 - (0.95 ** (hazards * 5))
    risk_10yr = 1 - (0.95 ** (hazards * 10))
    
    def predict_wrapper(X):
        X_tensor = torch.tensor(X, dtype=torch.float32)
        with torch.no_grad():
            return model(X_tensor).numpy()
    
    background = shap.sample(X_train, 30, random_state=42)
    explainer = shap.KernelExplainer(predict_wrapper, background)
    shap_values = explainer.shap_values(patient_scaled)
    
    shap_importance = []
    for i, fname in enumerate(FEATURE_NAMES):
        val = shap_values[0][i] if shap_values[0].ndim == 0 else shap_values[0, i]
        shap_importance.append({'feature': fname, 'value': float(val)})
    
    shap_importance.sort(key=lambda x: abs(x['value']), reverse=True)
    
    return {
        'immediateRisk': float(risk_prob),
        'risk2Year': float(risk_2yr),
        'risk5Year': float(risk_5yr),
        'risk10Year': float(risk_10yr),
        'shapImportance': shap_importance[:5]
    }

class APIHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/risk':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            patient = json.loads(post_data.decode('utf-8'))
            
            result = predict_risk(patient)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

os.chdir('clinical-dashboard')
with socketserver.TCPServer(("", PORT), APIHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    print("Press Ctrl+C to stop")
    httpd.serve_forever()