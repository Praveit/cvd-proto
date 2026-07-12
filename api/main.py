"""FastAPI application for CVD Risk Prediction API"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict
import numpy as np

from clinical_risk import calculate_clinical_risk, compute_shap_importance


app = FastAPI(
    title="CVD Risk Assessment API",
    description="10-year cardiovascular disease risk prediction with SHAP explanations",
    version="1.0.0"
)

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PatientData(BaseModel):
    """Patient vital signs and risk factors"""
    age: int = Field(..., ge=0, le=120, description="Age in years")
    gender: int = Field(..., ge=1, le=2, description="1=Male, 2=Female")
    height: int = Field(..., ge=50, le=250, description="Height in cm")
    weight: int = Field(..., ge=20, le=300, description="Weight in kg")
    ap_hi: int = Field(..., ge=50, le=300, description="Systolic blood pressure")
    ap_lo: int = Field(..., ge=30, le=200, description="Diastolic blood pressure")
    cholesterol: int = Field(..., ge=1, le=3, description="1=Normal, 2=Above normal, 3=Well above normal")
    gluc: int = Field(..., ge=1, le=3, description="1=Normal, 2=Above normal, 3=Well above normal")
    smoke: int = Field(..., ge=0, le=1, description="0=No, 1=Yes")
    alco: int = Field(..., ge=0, le=1, description="0=No, 1=Yes")
    active: int = Field(..., ge=0, le=1, description="0=No, 1=Yes")


class ShapFeature(BaseModel):
    feature: str
    value: float


class RiskResponse(BaseModel):
    immediateRisk: float
    risk2Year: float
    risk5Year: float
    risk10Year: float
    shapImportance: List[ShapFeature]


@app.post("/api/predict", response_model=RiskResponse)
def predict_risk(patient: PatientData):
    """Calculate CVD risk and SHAP feature importance for a patient"""
    try:
        patient_dict = patient.model_dump()
        
        # Calculate risk using clinical formula
        risk_10yr, feature_contributions = calculate_clinical_risk(patient_dict)
        
        # Time-horizon risk projections
        risk_baseline = risk_10yr * 0.15
        risk_2yr = risk_10yr * 0.35
        risk_5yr = risk_10yr * 0.70
        
        risk_baseline = float(np.clip(risk_baseline, 0.01, 0.50))
        risk_2yr = float(np.clip(risk_2yr, 0.05, 0.60))
        risk_5yr = float(np.clip(risk_5yr, 0.10, 0.70))
        risk_10yr = float(np.clip(risk_10yr, 0.15, 0.75))
        
        # Compute SHAP-like feature importance
        shap_importance = compute_shap_importance(feature_contributions, risk_10yr)
        
        return {
            "immediateRisk": risk_baseline,
            "risk2Year": risk_2yr,
            "risk5Year": risk_5yr,
            "risk10Year": risk_10yr,
            "shapImportance": shap_importance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "cvd-risk-api"}


@app.get("/")
def root():
    return {
        "service": "CVD Risk Assessment API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "predict": "/api/predict"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)