import { NextResponse } from 'next/server'

// Local FastAPI endpoint (via nginx reverse proxy on same container)
const FASTAPI_URL = process.env.FASTAPI_URL || 'http://127.0.0.1:8000'

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const patientData = await request.json()

    const response = await fetch(`${FASTAPI_URL}/api/risk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patientData),
    })

    if (!response.ok) {
      const error = await response.text()
      console.error('[API] FastAPI error:', error)
      return NextResponse.json({ error: 'Risk calculation failed' }, { status: 500 })
    }

    const result = await response.json()
    return NextResponse.json(result)
  } catch (error) {
    console.error('[API] Server error:', error)
    return NextResponse.json({ error: 'Server error' }, { status: 500 })
  }
}