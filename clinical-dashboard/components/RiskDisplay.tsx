'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart as AreaChartType } from 'recharts'
import { AlertTriangle, AlertCircle, CheckCircle2, Heart, TrendingUp } from 'lucide-react'

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

const riskGradientId = 'riskGradient'

export default function RiskDisplay({ result }: RiskDisplayProps) {
  if (!result || typeof result.immediateRisk !== 'number' || isNaN(result.immediateRisk)) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="text-center py-12">
          <Heart className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Cardiovascular Risk Assessment</h3>
          <p className="text-gray-500">Complete the patient form to calculate CVD risk</p>
        </div>
      </div>
    )
  }

  // Determine risk category and color
  const risk10YearPct = result.risk10Year * 100
  let riskCategory = 'Low'
  let riskColor = 'text-green-600'
  let riskBg = 'bg-green-50'
  let riskBorder = 'border-green-200'

  if (risk10YearPct >= 20) {
    riskCategory = 'High'
    riskColor = 'text-red-600'
    riskBg = 'bg-red-50'
    riskBorder = 'border-red-200'
  } else if (risk10YearPct >= 10) {
    riskCategory = 'Moderate'
    riskColor = 'text-amber-600'
    riskBg = 'bg-amber-50'
    riskBorder = 'border-amber-200'
  } else {
    riskCategory = 'Low'
    riskColor = 'text-green-600'
    riskBg = 'bg-green-50'
    riskBorder = 'border-green-200'
  }

  // Risk icon based on category
  const RiskIcon = risk10YearPct >= 20 ? AlertCircle : risk10YearPct >= 10 ? AlertTriangle : CheckCircle2

  // Get top risk factors from SHAP
  const shapImportance = result.shapImportance || []
  const topRiskFactors = shapImportance
    .filter(f => f.value > 0)
    .sort((a, b) => b.value - a.value)
    .slice(0, 3)

  const topProtectiveFactors = shapImportance
    .filter(f => f.value < 0)
    .sort((a, b) => a.value - b.value)
    .slice(0, 2)

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

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      {/* Risk Category Header */}
      <div className={`flex items-center gap-3 p-4 rounded-lg ${riskBg} border ${riskBorder} mb-6`}>
        <RiskIcon className={`h-6 w-6 ${riskColor} flex-shrink-0`} />
        <div>
          <p className="text-sm text-gray-500">10-Year CVD Risk Category</p>
          <p className={`text-2xl font-bold ${riskColor}`}>{riskCategory} Risk ({risk10YearPct.toFixed(1)}%)</p>
        </div>
      </div>

      {/* Risk Trajectory Chart */}
      <div className="h-64 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChartType
            data={[
              { time: 'Immediate', risk: result.immediateRisk * 100 },
              { time: '2 Years', risk: result.risk2Year * 100 },
              { time: '5 Years', risk: result.risk5Year * 100 },
              { time: '10 Years', risk: result.risk10Year * 100 },
            ]}
          >
            <defs>
              <linearGradient id={riskGradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="time" 
              stroke="#6b7280" 
              fontSize={12}
              tick={{ fill: '#6b7280' }}
            />
            <YAxis 
              stroke="#6b7280" 
              fontSize={12}
              tickFormatter={(v) => `${v.toFixed(0)}%`}
              domain={[0, 'auto']}
              tick={{ fill: '#6b7280' }}
            />
            <Tooltip 
              formatter={(value: number) => [`${value.toFixed(1)}%`, 'CVD Risk']}
              contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
              labelFormatter={(label) => <span className="font-medium">{label}</span>}
            />
            <Area 
              type="monotone" 
              dataKey="risk" 
              stroke="#ef4444" 
              fill="url(#riskGradientId)" 
              strokeWidth={2}
            />
          </AreaChartType>
        </ResponsiveContainer>
      </div>

      {/* Risk Timeline Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Immediate Risk</p>
          <p className="text-2xl font-bold text-gray-900">{(result.immediateRisk * 100).toFixed(1)}%</p>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 uppercase tracking-wide">2-Year Risk</p>
          <p className="text-2xl font-bold text-gray-900">{(result.risk2Year * 100).toFixed(1)}%</p>
        </div>
        <div className="text-center p-4 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 uppercase tracking-wide">5-Year Risk</p>
          <p className="text-2xl font-bold text-gray-900">{(result.risk5Year * 100).toFixed(1)}%</p>
        </div>
      </div>

      {/* 10-Year Risk Card */}
      <div className="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg mb-6">
        <p className="text-xs text-blue-600 uppercase tracking-wide">10-Year Risk (Primary)</p>
        <p className="text-3xl font-bold text-blue-700">{(result.risk10Year * 100).toFixed(1)}%</p>
      </div>

      {/* Dynamic Risk Factors */}
      {(topRiskFactors.length > 0 || topProtectiveFactors.length > 0) && (
        <div className="space-y-4">
          {topRiskFactors.length > 0 && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <h3 className="font-medium text-red-900">Key Risk Factors</h3>
              </div>
              <ul className="text-sm text-red-800 space-y-1">
                {topRiskFactors.map((factor, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-red-500 rounded-full flex-shrink-0 mt-1.5" />
                    <span className="font-medium">{featureLabels[factor.feature] || factor.feature}</span>
                    <span className="text-red-600 font-mono ml-auto">+{factor.value.toFixed(4)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {topProtectiveFactors.length > 0 && (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-2 mb-3">
                <Shield className="h-4 w-4 text-blue-600" />
                <h3 className="font-medium text-blue-900">Protective Factors</h3>
              </div>
              <ul className="text-sm text-blue-800 space-y-1">
                {topProtectiveFactors.map((factor, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0 mt-1.5" />
                    <span className="font-medium">{featureLabels[factor.feature] || factor.feature}</span>
                    <span className="text-blue-600 font-mono ml-auto">{factor.value.toFixed(4)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Clinical Recommendations based on actual risk factors */}
      <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
        <h3 className="font-medium text-gray-900 mb-3 flex items-center gap-2">
          <TrendingUp className="h-4 w-4 text-gray-600" />
          Clinical Recommendations
        </h3>
        <div className="text-sm text-gray-700 space-y-2">
          {topRiskFactors.length > 0 && (
            <div>
              <p className="font-medium text-red-700 mb-1">Address modifiable risk factors:</p>
              <ul className="list-disc list-inside space-y-1">
                {topRiskFactors.map((factor, i) => (
                  <li key={i}>
                    <strong>{featureLabels[factor.feature] || factor.feature}</strong>
                    {factor.feature === 'ap_hi' && ': Target SBP < 130 mmHg through lifestyle and/or medication'}
                    {factor.feature === 'ap_lo' && ': Target DBP < 80 mmHg'}
                    {factor.feature === 'cholesterol' && ': Consider lipid-lowering therapy if indicated'}
                    {factor.feature === 'gluc' && ': Optimize glycemic control'}
                    {factor.feature === 'smoke' && ': Strongly recommend smoking cessation program'}
                    {factor.feature === 'weight' && ': Weight management through diet and exercise'}
                    {factor.feature === 'alco' && ': Limit alcohol consumption'}
                    {factor.feature === 'active' && ': Increase physical activity to 150+ min/week moderate intensity'}
                    {factor.feature === 'age' && ': Age-appropriate screening and preventive care'}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {topProtectiveFactors.length > 0 && (
            <div>
              <p className="font-medium text-blue-700 mb-1">Maintain protective factors:</p>
              <ul className="list-disc list-inside space-y-1">
                {topProtectiveFactors.map((factor, i) => (
                  <li key={i}>
                    <strong>{featureLabels[factor.feature] || factor.feature}</strong>
                    {factor.feature === 'active' && ': Continue regular physical activity'}
                    {factor.feature === 'smoke' && ': Maintain smoke-free status'}
                    {factor.feature === 'cholesterol' && ': Continue healthy diet'}
                    {factor.feature === 'ap_hi' && ': Maintain blood pressure control'}
                    {factor.feature === 'gluc' && ': Maintain normal glucose levels'}
                    {factor.feature === 'alco' && ': Continue moderate/no alcohol'}
                    {factor.feature === 'weight' && ': Maintain healthy weight'}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {topRiskFactors.length === 0 && topProtectiveFactors.length === 0 && (
            <p className="text-gray-600">No significant modifiable risk factors identified. Continue healthy lifestyle.</p>
          )}
        </div>
      </div>
    </div>
  )
}