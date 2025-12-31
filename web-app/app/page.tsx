'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Download, CheckCircle, XCircle, Loader2 } from 'lucide-react';

// API URL - uses environment variable in production, localhost in development
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'converting' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string>('');
  const [downloadUrl, setDownloadUrl] = useState<string>('');
  const [pdfFilename, setPdfFilename] = useState<string>('');

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setStatus('idle');
      setError('');
      setDownloadUrl('');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc']
    },
    maxFiles: 1,
    multiple: false
  });

  const handleConvert = async () => {
    if (!file) return;

    setStatus('uploading');
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      setStatus('converting');

      const response = await fetch(`${API_URL}/api/convert`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Conversion failed');
      }

      setStatus('success');
      setDownloadUrl(`${API_URL}${data.download_url}`);
      setPdfFilename(data.filename);
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  const handleDownload = () => {
    if (downloadUrl) {
      window.location.href = downloadUrl;
    }
  };

  const reset = () => {
    setFile(null);
    setStatus('idle');
    setError('');
    setDownloadUrl('');
    setPdfFilename('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 backdrop-blur-sm bg-white/5">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">Word to PDF Agent</h1>
              <p className="text-purple-300 text-sm">by Vector Systems</p>
            </div>
            <div className="text-right">
              <p className="text-white/60 text-sm">AI-Powered Conversion</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-3xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h2 className="text-5xl font-bold text-white mb-4">
              Convert Word to PDF
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-400">
                Instantly
              </span>
            </h2>
            <p className="text-xl text-white/70">
              Upload your .docx file and get a perfect PDF in seconds
            </p>
          </div>

          {/* Upload Area */}
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 shadow-2xl">
            {status === 'idle' || status === 'error' ? (
              <>
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300 ${isDragActive
                    ? 'border-purple-400 bg-purple-500/20'
                    : 'border-white/30 hover:border-purple-400 hover:bg-white/5'
                    }`}
                >
                  <input {...getInputProps()} />
                  <Upload className="w-16 h-16 mx-auto mb-4 text-purple-400" />
                  {isDragActive ? (
                    <p className="text-white text-lg">Drop your file here...</p>
                  ) : (
                    <>
                      <p className="text-white text-lg mb-2">
                        Drag & drop your Word document here
                      </p>
                      <p className="text-white/60">or click to browse</p>
                      <p className="text-white/40 text-sm mt-4">Supports .docx and .doc files</p>
                    </>
                  )}
                </div>

                {file && (
                  <div className="mt-6 p-4 bg-white/5 rounded-lg border border-white/10">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <FileText className="w-8 h-8 text-purple-400" />
                        <div>
                          <p className="text-white font-medium">{file.name}</p>
                          <p className="text-white/60 text-sm">
                            {(file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={handleConvert}
                        className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-pink-600 transition-all duration-300 shadow-lg hover:shadow-purple-500/50"
                      >
                        Convert to PDF
                      </button>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="mt-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg flex items-center gap-3">
                    <XCircle className="w-6 h-6 text-red-400" />
                    <p className="text-red-200">{error}</p>
                  </div>
                )}
              </>
            ) : status === 'uploading' || status === 'converting' ? (
              <div className="text-center py-12">
                <Loader2 className="w-16 h-16 mx-auto mb-4 text-purple-400 animate-spin" />
                <p className="text-white text-xl mb-2">
                  {status === 'uploading' ? 'Uploading...' : 'Converting to PDF...'}
                </p>
                <p className="text-white/60">This will only take a moment</p>
              </div>
            ) : status === 'success' ? (
              <div className="text-center py-12">
                <CheckCircle className="w-16 h-16 mx-auto mb-4 text-green-400" />
                <p className="text-white text-2xl font-bold mb-2">Conversion Successful!</p>
                <p className="text-white/70 mb-6">Your PDF is ready to download</p>

                <div className="flex gap-4 justify-center">
                  <button
                    onClick={handleDownload}
                    className="px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg font-medium hover:from-green-600 hover:to-emerald-600 transition-all duration-300 shadow-lg hover:shadow-green-500/50 flex items-center gap-2"
                  >
                    <Download className="w-5 h-5" />
                    Download PDF
                  </button>
                  <button
                    onClick={reset}
                    className="px-8 py-4 bg-white/10 text-white rounded-lg font-medium hover:bg-white/20 transition-all duration-300 border border-white/20"
                  >
                    Convert Another
                  </button>
                </div>

                {pdfFilename && (
                  <p className="text-white/60 text-sm mt-4">
                    File: {pdfFilename}
                  </p>
                )}
              </div>
            ) : null}
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-6 mt-12">
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
                <FileText className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">High Fidelity</h3>
              <p className="text-white/60 text-sm">
                Preserves all formatting, images, and layout from your original document
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
                <Loader2 className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Lightning Fast</h3>
              <p className="text-white/60 text-sm">
                AI-powered conversion completes in seconds, not minutes
              </p>
            </div>

            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
                <CheckCircle className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">Secure & Private</h3>
              <p className="text-white/60 text-sm">
                Files are automatically deleted after download for your privacy
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center text-white/60 text-sm">
            <p>© 2025 Vector Systems. All rights reserved.</p>
            <p className="mt-2">Powered by AI • Built with Next.js</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
