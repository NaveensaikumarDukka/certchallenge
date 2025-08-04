import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const apiKeys = await request.json();
    console.log('Frontend API route received keys:', apiKeys);
    
    // Validate that at least one API key is provided
    const providedKeys = Object.keys(apiKeys).filter(key => apiKeys[key] && apiKeys[key].trim() !== '');
    console.log('Provided keys:', providedKeys);
    
    if (providedKeys.length === 0) {
      return NextResponse.json(
        { error: 'At least one API key must be provided' },
        { status: 400 }
      );
    }
    
    // Ensure all expected keys are present (even if empty)
    const expectedKeys = ['openai', 'tavily', 'langsmith', 'cohere'];
    const completeApiKeys = { ...apiKeys };
    expectedKeys.forEach(key => {
      if (!completeApiKeys[key]) {
        completeApiKeys[key] = '';
      }
    });
    
    console.log('Sending to backend:', completeApiKeys);

    // Send API keys to backend
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/v1/settings/update-keys`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(completeApiKeys),
    });

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`);
    }

    const result = await response.json();

    return NextResponse.json({
      success: true,
      message: 'API keys saved successfully',
      data: result,
    });

  } catch (error) {
    console.error('Error saving API keys:', error);
    
    return NextResponse.json(
      { 
        error: 'Failed to save API keys',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
} 