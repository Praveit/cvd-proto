'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { HelpCircle } from 'lucide-react'

interface ShapImportance {
  feature: string
  value: number
}

interface ExplanationPanelProps {
  shapImportance: ShapImportance[] | null
}

const featureLabels: Record<string, string> = {
  ap_hi: 'Systolic BP',
  ap_lo: 'Diastolic BP',
  cholesterol: 'Cholesterol',
  gluc: 'Glucose',
  age: 'Age',
  weight: 'Weight',
  smoke: 'Smoking',
  alco: 'Alcohol',
  active: 'Physical Activity'
}

export default function ExplanationPanel({ shapImportance }: ExplanationPanelProps) {
  if (!shapImportance || shapImportance.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center gap-2 mb-4">
          <HelpCircle className="h-5 w-5 text-blue-600" />
          <h2 className="text-lg font-semibold text-gray-900">SHAP Feature Importance</h2>
        </div>
        <p className="text-gray-500 text-center py-8">Calculate risk to see feature explanations</p>
      </div>
    )
  }

  const chartData = shapImportance.map(item => ({
    feature: featureLabels[item.feature] || item.feature,
    value: item.value,
    rawFeature: item.feature
  }))

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <div className="flex items-center gap-2 mb-4">
        <HelpCircle className="h-5 w-5 text-blue-600" />
        <h2 className="text-lg font-semibold text-gray-900">SHAP Feature Importance</h2>
      </div>
      
      <p className="text-sm text-gray-600 mb-4">
        The following shows how each feature contributes to the risk prediction for this patient. 
        Red bars increase risk, blue bars decrease risk.
      </p>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 80, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" horizontal={true} vertical={false} />
            <XAxis 
              type="number" 
              stroke="#6b7280" 
              fontSize={12}
              tickFormatter={(v) => v > 0 ? `+${v.toFixed(2)}` : v.toFixed(2)}
            />
            <YAxis 
              type="category" 
              dataKey="feature" 
              stroke="#6b7280" 
              fontSize={11}
              width={80}
            />
            <Tooltip 
              formatter={(value: number) => [
                `${value > 0 ? '+' : ''}${value.toFixed(4)}`,
                'SHAP Value'
              ]}
              labelFormatter={() => ''}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
            />
            <Bar dataKey="value" radius={[0, 4, 4, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={index} fill={entry.value > 0 ? '#ef4444' : '#3b82f6'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">Clinical Interpretation</h3>
        <p className="text-sm text-blue-800">
          {shapImportance[0]?.feature && (
            <>
              <strong>{featureLabels[shapImportance[0].feature] || shapImportance[0].feature}</strong> 
              {' '}is the most significant contributor to this patient's CVD risk.
              {shapImportance[0].value > 0 ? ' Recommend monitoring and lifestyle modifications.' : ' This factor is protective.'}
            </>
          )}
        </p>
      </div>
    </div>
  )
}