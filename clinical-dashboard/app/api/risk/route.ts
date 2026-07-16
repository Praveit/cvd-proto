import { NextResponse } from 'next/server'
import { calculateRisk } from './clinicalRisk'
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
const supabase = createClient(supabaseUrl, supabaseAnonKey)

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const patientData = await request.json()
    const result = calculateRisk(patientData)

    // Try to get user from cookie header
    const authHeader = request.headers.get('authorization')
    
    if (authHeader) {
      try {
        const token = authHeader.replace('Bearer ', '')
        const { data: { user } } = await supabase.auth.getUser(token)
        
        if (!user?.id) {
          throw new Error('No user ID')
        }

        // Save assessment to database
        await supabase.from('assessments').insert({
          user_id: user.id,
          patient_data: patientData,
          risk_results: result
        })
      } catch (e) {
        console.log('[API] Could not save to user history')
      }
    }

    return NextResponse.json(result)
  } catch (error) {
    console.error('[API] Server error:', error)
    return NextResponse.json({ error: 'Server error: ' + String(error) }, { status: 500 })
  }
}