export const runtime = 'nodejs';

export async function POST(request: Request) {
  try {
    // Forward the request to the backend
    const formData = await request.formData();
    
    // Log the forwarding attempt
    console.log('Forwarding request to backend', {
      formData: Object.fromEntries(formData.entries())
    });

    const response = await fetch('http://localhost:3001/api/v1/test/optimize', {
      method: 'POST',
      body: formData
    });

    // Get the response data
    const data = await response.arrayBuffer();
    const headers = response.headers;

    // Return response with same headers
    return new Response(data, {
      status: response.status,
      headers: {
        'Content-Type': headers.get('Content-Type') || 'application/octet-stream',
        'Content-Disposition': headers.get('Content-Disposition') || 'attachment; filename="optimized-resume.docx"'
      }
    });
  } catch (error) {
    console.error('Error in API route:', error);
    return new Response(
      JSON.stringify({ 
        success: false, 
        error: 'Failed to optimize document'
      }), 
      { 
        status: 500,
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
  }
}