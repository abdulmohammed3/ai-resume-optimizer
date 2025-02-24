export async function GET() {
  try {
    const response = await fetch('http://localhost:3001/api/v1/health');
    const data = await response.json();
    return Response.json(data);
  } catch (error) {
    console.error('Health check error:', error);
    return Response.json(
      { 
        success: false, 
        error: 'Could not connect to backend server' 
      }, 
      { 
        status: 500 
      }
    );
  }
}