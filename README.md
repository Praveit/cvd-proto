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

## Live Demo

**Live URL:** https://clinical-dashboard-woad.vercel.app/

Try entering patient data to see:
- 10-year CVD risk prediction
- 2-year, 5-year, and 10-year risk horizons
- SHAP feature importance showing what drives each prediction

## Features

- **Clinical Risk Calculation**: 10-year CVD risk based on Framingham-style scoring
- **SHAP Explanations**: Feature importance visualization showing what drives each prediction
- **Multi-horizon Predictions**: Immediate, 2-year, 5-year, and 10-year risk estimates
- **Real-time API**: Next.js API route with sub-100ms response times

## Architecture

The application now runs entirely on Vercel's serverless platform - no separate backend needed.

```
┌─────────────────────────────────────────────────────────────┐
│                    Vercel (Serverless)                     │
│  ┌──────────────┐    ┌──────────────────────────────────┐  │
│  │  Next.js UI   │    │  /api/risk (Serverless Function) │  │
│  │  (Frontend)  │───▶│  (TypeScript Risk Calculation)   │  │
│  └──────────────┘    └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard UI |
| `/api/risk` | POST | Calculate CVD risk with SHAP values |

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
    {"feature": "smoke", "value": 0.078},
    {"feature": "age", "value": 0.063},
    {"feature": "ap_hi", "value": 0.063},
    {"feature": "cholesterol", "value": 0.031}
  ]
}
```

## Host on Vercel (Recommended)

The easiest way to deploy - free hobby tier available.

### Option 1: Deploy from GitHub (Recommended)

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) and sign up with GitHub
3. Click "Add New..." → "Project"
4. Select the `clinical-dashboard` repository
5. Click "Deploy"

Your app will be live at `https://your-project.vercel.app`

### Option 2: Deploy from CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login or sign up
vercel login

# Deploy
vercel --prod
```

## Host Locally

### Prerequisites
- Node.js 18+
- npm or yarn

### Steps

```bash
# Clone the repository
git clone https://github.com/Praveit/cvd-risk-dashboard.git
cd cvd-risk-dashboard/clinical-dashboard

# Install dependencies
npm install

# Start development server
npm run dev
```

Open http://localhost:3000 to see the dashboard.

### Build for Production

```bash
npm run build
npm start
```

## Model Details

- **Risk Algorithm**: Clinical point-based scoring (Framingham-inspired)
- **Features**: 11 clinical variables (age, gender, BP, cholesterol, glucose, BMI, lifestyle)
- **SHAP Approximation**: Proportional contribution scaling from clinical points
- **Performance**: ~50ms per prediction on serverless

## Technology Stack

- **Frontend**: Next.js 16, React, Tailwind CSS, Recharts
- **API**: Next.js Serverless Functions (TypeScript)
- **Hosting**: Vercel (free hobby tier)
- **Risk Calculation**: Native TypeScript port of clinical algorithms

## License

MIT License - See LICENSE file for details.