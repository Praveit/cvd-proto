'use client'

import { useState } from 'react'
import PatientForm from '@/components/PatientForm'
import RiskDisplay from '@/components/RiskDisplay'
import ExplanationPanel from '@/components/ExplanationPanel'
import { Activity, Users, TrendingUp, Shield } from 'lucide-react'

interface RiskResult {
  immediateRisk: number
  risk2Year: number
  risk5Year: number
  risk10Year: number
  shapImportance: { feature: string; value: number }[]
}

export default function Home() {
  const [riskResult, setRiskResult] = useState<RiskResult | null>(null)

  return (
    <div className="min-h-screen">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Activity className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">CVD Risk Assessment</h1>
                <p className="text-xs text-gray-500">Explainable AI-Powered</p>
              </div>
            </div>
            <div className="flex items-center gap-6 text-sm text-gray-600">
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                <span>Clinician Portal</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1">
            <PatientForm onResult={setRiskResult} />
          </div>
          
          <div className="lg:col-span-2 space-y-6">
            <RiskDisplay result={riskResult} />
            <ExplanationPanel shapImportance={riskResult?.shapImportance || null} />
          </div>
        </div>

        <section className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-50 rounded-lg">
                <TrendingUp className="h-5 w-5 text-blue-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Risk Trajectories</h3>
            </div>
            <p className="text-sm text-gray-600">
              Predict CVD risk over 2, 5, and 10-year horizons using DeepSurv survival analysis.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-green-50 rounded-lg">
                <Shield className="h-5 w-5 text-green-600" />
              </div>
              <h3 className="font-semibold text-gray-900">SHAP Explanations</h3>
            </div>
            <p className="text-sm text-gray-600">
              Understand why the model predicts each risk level using SHapley Additive explanations.
            </p>
          </div>

          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-purple-50 rounded-lg">
                <Activity className="h-5 w-5 text-purple-600" />
              </div>
              <h3 className="font-semibold text-gray-900">Clinical Decision Support</h3>
            </div>
            <p className="text-sm text-gray-600">
              Evidence-based risk assessment to support clinical decision-making workflows.
            </p>
          </div>
        </section>
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            CVD Risk Assessment Tool — For Clinical Decision Support Only — Not a Medical Device
          </p>
        </div>
      </footer>
    </div>
  )
}