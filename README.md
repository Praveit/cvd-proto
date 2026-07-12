---
title: CVD Risk Assessment
emoji: 🫀
colorFrom: red
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# CVD Risk Assessment Dashboard

Explainable AI-powered cardiovascular disease risk prediction with SHAP feature importance explanations.

## Features

- **Clinical Risk Calculation**: 10-year CVD risk based on Framingham-style scoring
- **SHAP Explanations**: Feature importance visualization showing what drives each prediction
- **Multi-horizon Predictions**: Immediate, 2-year, 5-year, and 10-year risk estimates
- **Real-time API**: FastAPI backend with sub-100ms response times

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HF Space (Port 7860)                 │
│  ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │    nginx     │───▶│   FastAPI    │    │  Next.js   │ │
│  │  (reverse    │    │  (port 8000) │    │  (port     │ │
│  │   proxy)     │    │              │    │   3000)    │ │
│  └──────────────┘    └──────────────┘    └────────────┘ │
│         ▲                    ▲                  ▲       │
│         │                    │                  │       │
│         └────────────────────┴──────────────────┘       │
│                            │                             │
│                     ┌──────────────┐                     │
│                     │  supervisord │                     │
│                     │  (process    │                     │
│                     │   manager)   │                     │
│                     └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/risk` | POST | Calculate CVD risk with SHAP values |
| `/docs` | GET | FastAPI auto-generated docs |

### POST /api/risk

**Request:**
```json
{
  "age": 55,
  "gender": 1,
  "height": 170,
  "weight": 85,
  "ap_hi": 145,
  "ap_lo": 90,
  "cholesterol": 2,
  "gluc": 1,
  "smoke": 1,
  "alco": 0,
  "active": 0
}
```

**Response:**
```json
{
  "immediateRisk": 0.046,
  "risk2Year": 0.107,
  "risk5Year": 0.215,
  "risk10Year": 0.307,
  "shapImportance": [
    {"feature": "age", "value": 0.047},
    {"feature": "smoke", "value": 0.039},
    {"feature": "ap_hi", "value": 0.031},
    {"feature": "cholesterol", "value": 0.016},
    {"feature": "active", "value": 0.016},
    {"feature": "weight", "value": 0.008}
  ]
}
```

## Model Details

- **Risk Algorithm**: Clinical point-based scoring (Framingham-inspired)
- **Features**: 11 clinical variables (age, gender, BP, cholesterol, glucose, BMI, lifestyle)
- **SHAP Approximation**: Proportional contribution scaling from clinical points
- **Performance**: ~50ms per prediction on CPU

## Deployment

This Space runs on Hugging Face Spaces using Docker SDK:
- **Base**: `python:3.11-slim` (~200MB base)
- **Runtime**: ~800MB total (Python deps + Node.js + nginx + supervisord)
- **Port**: 7860 (HF Spaces standard)
- **Processes**: nginx + FastAPI (uvicorn) + Next.js (standalone) managed by supervisord

## Local Development

```bash
# Build and run locally
docker build -t cvd-risk .
docker run -p 7860:7860 cvd-risk

# Or run services separately
# Terminal 1: FastAPI
cd api && uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 2: Next.js
cd clinical-dashboard && npm run dev
```

## License

MIT License - See LICENSE file for details.