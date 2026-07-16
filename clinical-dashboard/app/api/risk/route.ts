import { NextResponse } from 'next/server'
import { calculateRisk } from './clinicalRisk'
import { createClient } from '@supabase/supabase-js'
import { headers } from 'next/headers'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
const supabase = createClient(supabaseUrl, supabaseAnonKey)

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const patientData = await request.json()
    const result = calculateRisk(patientData)

    // Try to get user from auth header
    const headersList = headers()
    const authHeader = headersList.get('authorization')
    
    if (authHeader) {
      try {
        const token = authHeader.replace('Bearer ', '')
        const { data: { user }, error: authError } = await supabase.auth.getUser(token)
        
        if (!authError && user) {
          // Save assessment to database
          await supabase.from('assessments').insert({
            user_id: user.id,
            patient_data: patientData,
            risk_results: result
          })
        }
      } catch (e) {
        // Silent fail - don't break the main flow if auth fails
        console.log('[API] Could not save to user history (not authenticated)')
      }
    }

    return NextResponse.json(result)
  } catch (error) {
    console.error('[API] Server error:', error)
    return NextResponse.json({ error: 'Server error: ' + String(error) }, { status: 500 })
  }
}