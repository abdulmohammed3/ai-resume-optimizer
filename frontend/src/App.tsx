import { useState } from 'react'
import './App.css'

interface Resume {
  file: File | null;
  optimizedContent?: string;
}

function App() {
  const [resume, setResume] = useState<Resume>({ file: null });
  const [jobDescription, setJobDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      setResume({ file });
    } else {
      alert('Please upload a valid DOCX file');
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!resume.file || !jobDescription) {
      alert('Please upload a resume and enter a job description');
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append('resume', resume.file);
      formData.append('job_description', JSON.stringify({
        job_description: jobDescription
      }));

      const response = await fetch('http://localhost:5000/optimize-resume', {
        method: 'POST',
        headers: {
          'Accept': 'application/json'
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to optimize resume');
      }

      const data = await response.json();
      setResume(prev => ({ ...prev, optimizedContent: data.optimized_resume }));
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to optimize resume. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-gray-900">AI Resume Optimizer</h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="bg-white rounded-lg shadow px-5 py-6 sm:px-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* File Upload Section */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Upload Your Resume (DOCX)
                </label>
                <div className="mt-1">
                  <input
                    type="file"
                    accept=".docx"
                    onChange={handleFileUpload}
                    className="input"
                  />
                </div>
              </div>

              {/* Job Description Section */}
              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Job Description
                </label>
                <div className="mt-1">
                  <textarea
                    rows={4}
                    value={jobDescription}
                    onChange={(e) => setJobDescription(e.target.value)}
                    className="input"
                    placeholder="Paste the job description here..."
                  />
                </div>
              </div>

              {/* Submit Button */}
              <div>
                <button
                  type="submit"
                  disabled={isLoading || !resume.file || !jobDescription}
                  className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isLoading ? 'Optimizing...' : 'Optimize Resume'}
                </button>
              </div>
            </form>

            {/* Results Section */}
            {resume.optimizedContent && (
              <div className="mt-8">
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  Optimized Resume
                </h2>
                <div className="bg-gray-50 p-4 rounded-md">
                  <pre className="whitespace-pre-wrap font-mono text-sm bg-white p-4 rounded-md shadow-sm">
                    {resume.optimizedContent}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
