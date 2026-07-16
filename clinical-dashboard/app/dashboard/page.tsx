'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { useAuth } from '@/components/AuthProvider'
import PatientForm from '@/components/PatientForm'
import RiskDisplay from '@/components/RiskDisplay'
import ExplanationPanel from '@/components/ExplanationPanel'
import { supabase } from '@/lib/supabase'

interface RiskResult {
  immediateRisk: number
  risk2Year: number
  risk5Year: number
  risk10Year: number
  shapImportance: { feature: string; value: number }[]
}

export default function DashboardPage() {
  const { user, signOut, loading } = useAuth()
  const router = useRouter()
  const [riskResult, setRiskResult] = useState<RiskResult | null>(null)
  const [patientData, setPatientData] = useState<any>(null)
  const [history, setHistory] = useState<any[]>([])
  const [saveSuccess, setSaveSuccess] = useState(false)

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login')
    } else if (user) {
      fetchHistory()
    }
  }, [user, loading, router])

  const fetchHistory = async () => {
    const { data } = await supabase
      .from('assessments')
      .select('*')
      .eq('user_id', user?.id)
      .order('created_at', { ascending: false })
      .limit(10)
    if (data) setHistory(data)
  }

  const handleResult = (result: RiskResult, data: any) => {
    setRiskResult(result)
    setPatientData(data)
  }

  const handleSaveToHistory = async () => {
    if (!user || !riskResult || !patientData) return
    
    const { error } = await supabase.from('assessments').insert({
      user_id: user.id,
      patient_data: patientData,
      risk_results: riskResult
    })

    if (!error) {
      setSaveSuccess(true)
      fetchHistory()
      setTimeout(() => setSaveSuccess(false), 3000)
    }
  }

  const handleSignOut = async () => {
    await signOut()
    router.push('/')
  }

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>
  }

  if (!user) return null

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <Link href="/dashboard" className="text-xl font-bold text-red-600">
                🫀 Heart Risk Tracker
              </Link>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-600">{user.email}</span>
              <button
                onClick={handleSignOut}
                className="text-sm text-gray-500 hover:text-gray-700"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">New Assessment</h2>
              <PatientForm onResult={handleResult} />
              {riskResult && (
                <button
                  onClick={handleSaveToHistory}
                  className="mt-4 w-full py-2 px-4 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  {saveSuccess ? 'Saved!' : 'Save to My History'}
                </button>
              )}
            </div>
          </div>

          <div>
            {riskResult ? (
              <>
                <RiskDisplay result={riskResult} patientData={patientData} />
                <ExplanationPanel shapImportance={riskResult.shapImportance} />
              </>
            ) : (
              <div className="bg-white rounded-lg shadow p-6 text-center text-gray-500">
                Enter patient data to see risk assessment
              </div>
            )}
          </div>
        </div>

        {history.length > 0 && (
          <div className="mt-8 bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Your Assessment History</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th className="text-left text-xs font-medium text-gray-500 uppercase">10-Year Risk</th>
                    <th className="text-left text-xs font-medium text-gray-500 uppercase">Top Factor</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {history.map((item) => {
                    const results = item.risk_results as RiskResult
                    const topFactor = results?.shapImportance?.[0]
                    return (
                      <tr key={item.id} className="hover:bg-gray-50">
                        <td className="py-3 text-sm text-gray-900">
                          {new Date(item.created_at).toLocaleDateString()}
                        </td>
                        <td className="py-3 text-sm text-gray-900">
                          {results ? (results.risk10Year * 100).toFixed(1) : '-'}%
                        </td>
                        <td className="py-3 text-sm text-gray-600">
                          {topFactor?.feature || '-'}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}