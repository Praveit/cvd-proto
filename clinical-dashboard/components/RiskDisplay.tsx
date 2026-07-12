'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import { AlertTriangle } from 'lucide-react'

interface RiskResult {
  immediateRisk: number
  risk2Year: number
  risk5Year: number
  risk10Year: number
  shapImportance: { feature: string; value: number }[]
}

interface RiskDisplayProps {
  result: RiskResult | null
}

const featureLabels: Record<string, string> = {
  ap_hi: 'Systolic BP',
  ap_lo: 'Diastolic BP',
  cholesterol: 'Cholesterol',
  gluc: 'Glucose',
  age: 'Age',
  weight: 'Weight',
  smoke: 'Smoking',
  active: 'Physical Activity'
}

export default function RiskDisplay({ result }: RiskDisplayProps) {
  if (!result) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Trajectory Analysis</h2>
        <p className="text-gray-500 text-center py-8">Enter patient data and click "Calculate Risk Assessment"</p>
      </div>
    )
  }

  const riskData = [
    { year: 'Baseline', risk: result.immediateRisk * 100 },
    { year: '2 Years', risk: result.risk2Year * 100 },
    { year: '5 Years', risk: result.risk5Year * 100 },
    { year: '10 Years', risk: result.risk10Year * 100 },
  ]

  const getRiskLevel = (risk10yr: number) => {
    // Clinical guidelines: 10-year CVD risk thresholds
    // Low: <10%, Moderate: 10-20%, High: >20%
    if (risk10yr < 0.10) return { label: 'Low Risk', color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200' }
    if (risk10yr < 0.20) return { label: 'Moderate Risk', color: 'text-yellow-600', bg: 'bg-yellow-50', border: 'border-yellow-200' }
    return { label: 'High Risk', color: 'text-red-600', bg: 'bg-red-50', border: 'border-red-200' }
  }

  // Use 10-year risk for clinical classification
  const currentRisk = result.risk10Year * 100
  const riskLevel = getRiskLevel(result.risk10Year)

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">Risk Trajectory Analysis</h2>
        <div className={`px-3 py-1 rounded-full text-sm font-medium ${riskLevel.bg} ${riskLevel.color} ${riskLevel.border} border`}>
          {riskLevel.label}
        </div>
      </div>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={riskData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="year" stroke="#6b7280" fontSize={12} />
            <YAxis stroke="#6b7280" fontSize={12} domain={[0, 100]} tickFormatter={(v) => `${v.toFixed(0)}%`} />
            <Tooltip 
              formatter={(value: number) => [`${value.toFixed(1)}%`, 'CVD Risk']}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
            <Area type="monotone" dataKey="risk" stroke="#ef4444" fill="url(#riskGradient)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-6 grid grid-cols-3 gap-4">
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 uppercase tracking-wide">2-Year Risk</p>
          <p className="text-2xl font-bold text-gray-900">{(result.risk2Year * 100).toFixed(0)}%</p>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 uppercase tracking-wide">5-Year Risk</p>
          <p className="text-2xl font-bold text-gray-900">{(result.risk5Year * 100).toFixed(0)}%</p>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 uppercase tracking-wide">10-Year Risk</p>
          <p className="text-2xl font-bold text-gray-900">{(result.risk10Year * 100).toFixed(0)}%</p>
        </div>
      </div>

      <div className="mt-4 flex items-start gap-2 p-3 bg-amber-50 border border-amber-200 rounded-lg">
        <AlertTriangle className="h-4 w-4 text-amber-600 mt-0.5" />
        <p className="text-sm text-amber-800">
          High blood pressure and elevated cholesterol are the primary risk drivers. Consider lifestyle modifications and monitoring.
        </p>
      </div>
    </div>
  )
}