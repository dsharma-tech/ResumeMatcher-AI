import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, FileText, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-react';
import axios from 'axios';
import { cn } from './lib/utils';

export default function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);


  // Dropzone Handler
  const onDrop = useCallback((acceptedFiles) => {
    setFile(acceptedFiles[0]);
    setError(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    multiple: false
  });

  const [progress, setProgress] = useState(0);

  // Analyze Handler
  const handleAnalyze = async () => {
    if (!file || !jobDescription) {
      setError("Please upload a resume and provide a job description.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setProgress(0);

    // Simulate progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval);
          return 90;
        }
        return prev + 10;
      });
    }, 500);

    const formData = new FormData();
    formData.append('resume', file);
    formData.append('job_description', jobDescription);

    try {
      // Assuming backend is on port 8000
      const backendUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${backendUrl}/api/analyze`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      clearInterval(interval);
      setProgress(100);
      // Small delay to show 100%
      setTimeout(() => {
        setResult(response.data);
        setLoading(false);
      }, 500);
    } catch (err) {
      clearInterval(interval);
      console.error(err);
      setError(err.response?.data?.detail || "An error occurred during analysis.");
      setLoading(false);
    }
  };

  return (
    <div className={cn("h-screen bg-gray-50 text-slate-900 font-sans flex flex-col overflow-hidden")}>

      {/* Navbar */}
      <nav className="w-full border-b border-gray-200 dark:border-slate-800 bg-white/80 dark:bg-slate-950/80 backdrop-blur-sm flex-shrink-0">
        <div className="w-full px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center shadow-md shadow-blue-500/20">
              <FileText className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
              Resume<span className="text-blue-600">Matcher</span> AI
            </h1>
          </div>
        </div>
      </nav>

      <main className="flex-1 p-4 md:p-6 overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-full overflow-hidden">

          {/* Left Column: Inputs */}
          <div className="lg:col-span-4 flex flex-col gap-4 h-full overflow-hidden">

            {/* 1. Resume Upload Card */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col flex-shrink-0">
              <div className="p-3 border-b border-gray-100 bg-gray-50/50">
                <h2 className="font-semibold text-xs uppercase tracking-wider text-gray-500">1. Upload Resume</h2>
              </div>
              <div className="p-4">
                <div {...getRootProps()}
                  className={cn(
                    "border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all duration-200 min-h-[120px] flex flex-col items-center justify-center",
                    isDragActive ? "border-blue-500 bg-blue-50/50" : "border-gray-200 hover:border-blue-400 hover:bg-gray-50",
                    file ? "bg-green-50/50 border-green-500" : ""
                  )}>
                  <input {...getInputProps()} />
                  {file ? (
                    <div className="flex flex-col items-center text-green-600 dark:text-green-400">
                      <CheckCircle className="w-8 h-8 mb-2" />
                      <p className="font-medium text-xs break-all px-2">{file.name}</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center text-gray-400 dark:text-gray-500">
                      <Upload className="w-8 h-8 mb-2" />
                      <p className="font-medium text-xs">PDF / DOCX</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 2. Job Description Card */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col flex-1 overflow-hidden">
              <div className="p-3 border-b border-gray-100 bg-gray-50/50">
                <h2 className="font-semibold text-xs uppercase tracking-wider text-gray-500">2. Job Description</h2>
              </div>
              <div className="flex-1 overflow-hidden p-2">
                <textarea
                  value={jobDescription}
                  onChange={(e) => setJobDescription(e.target.value)}
                  placeholder="Paste the Job Description here..."
                  className="w-full h-full p-3 rounded-lg border-0 bg-transparent focus:ring-0 resize-none text-sm leading-relaxed placeholder:text-gray-300"
                />
              </div>
            </div>

            {/* Analyize Button */}
            <div className="mt-auto flex-shrink-0 space-y-3">
              <button
                onClick={handleAnalyze}
                disabled={loading || !file || !jobDescription}
                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold tracking-wide shadow-lg shadow-blue-500/25 transition-all active:scale-[0.98] flex justify-center items-center group"
              >
                {loading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : (
                  <>
                    Analyze Fit <span className="ml-2 group-hover:translate-x-1 transition-transform">→</span>
                  </>
                )}
              </button>

              {error && (
                <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 flex items-center text-xs border border-red-100 dark:border-red-900/50">
                  <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                  {error}
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Results */}
          <div className="lg:col-span-8 h-full overflow-hidden">
            <div className="bg-white rounded-xl border border-gray-200 shadow-xl shadow-gray-200/50 h-full overflow-hidden flex flex-col relative">
              <AnimatePresence mode="wait">
                {loading ? (
                  <motion.div
                    key="loading"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 z-20 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm flex flex-col items-center justify-center p-8"
                  >
                    <div className="w-full max-w-sm">
                      <div className="flex justify-between text-sm font-medium mb-2 text-gray-600 dark:text-gray-300">
                        <span>Parsing & Analyzing...</span>
                        <span className="text-blue-600 dark:text-blue-400">{progress}%</span>
                      </div>
                      <div className="h-2 w-full bg-gray-100 dark:bg-slate-800 rounded-full overflow-hidden">
                        <motion.div
                          className="h-full bg-gradient-to-r from-blue-500 to-indigo-600"
                          initial={{ width: 0 }}
                          animate={{ width: `${progress}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                      <p className="text-xs text-center mt-4 text-gray-400 animate-pulse">
                        {progress < 30 ? "Extracting text..." :
                          progress < 60 ? "Generating embeddings..." :
                            progress < 90 ? "Matching skills & experience..." : "Finalizing verdict..."}
                      </p>
                    </div>
                  </motion.div>
                ) : result ? (
                  <motion.div
                    key="result"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col h-full overflow-hidden"
                  >
                    {/* Results Header */}
                    <div className="p-6 border-b border-gray-100 dark:border-slate-800 bg-gray-50/30 flex-shrink-0">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div>
                          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-1">Analysis Results</h2>
                          <p className="text-gray-500 dark:text-gray-400 text-xs">AI-powered fit assessment.</p>
                        </div>
                        <div className="flex items-center space-x-4">
                          <div className="text-right">
                            <div className="text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-br from-blue-600 to-indigo-600">
                              {result.score}%
                            </div>
                            <p className="text-[10px] text-gray-400 font-medium uppercase tracking-wide">Match Score</p>
                          </div>
                          <div className="h-10 w-px bg-gray-200 dark:bg-slate-700 hidden md:block"></div>
                          <div className={cn(
                            "px-4 py-1.5 rounded-full font-bold text-xs border",
                            result.score >= 80 ? "bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-900/30" :
                              result.score >= 60 ? "bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-400 dark:border-yellow-900/30" :
                                "bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-900/30"
                          )}>
                            {result.verdict}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Results Body */}
                    <div className="p-6 space-y-6 overflow-y-auto flex-1 custom-scrollbar">

                      {/* Summary Box */}
                      <div className="p-4 bg-blue-50 dark:bg-blue-900/10 rounded-lg border border-blue-100 dark:border-blue-900/30">
                        <h3 className="text-blue-900 dark:text-blue-300 font-semibold text-sm mb-2 flex items-center">
                          <FileText className="w-4 h-4 mr-2" /> Executive Summary
                        </h3>
                        <p className="text-blue-800/80 dark:text-blue-200/80 text-sm leading-relaxed">
                          {result.summary}
                        </p>
                      </div>

                      {/* Skills Grid */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-3 flex items-center">
                            <div className="w-2 h-2 rounded-full bg-green-500 mr-2"></div>
                            Matched Skills
                          </h3>
                          <div className="flex flex-wrap gap-1.5">
                            {result.matched_skills.map((skill, i) => (
                              <span key={i} className="px-2.5 py-1 rounded-md text-xs bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400 border border-green-100 dark:border-green-900/50 font-medium">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>

                        <div>
                          <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-3 flex items-center">
                            <div className="w-2 h-2 rounded-full bg-red-500 mr-2"></div>
                            Missing / To Improve
                          </h3>
                          <div className="flex flex-wrap gap-1.5">
                            {result.missing_skills.map((skill, i) => (
                              <span key={i} className="px-2.5 py-1 rounded-md text-xs bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400 border border-red-100 dark:border-red-900/50 font-medium">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>

                      {/* Suggestions */}
                      <div className="pt-5 border-t border-gray-100 dark:border-slate-800">
                        <h3 className="font-semibold text-gray-900 dark:text-white text-sm mb-3">Improvement Suggestions</h3>
                        <ul className="space-y-3">
                          {result.suggestions.map((item, i) => {
                            if (item.startsWith('###')) {
                              return (
                                <li key={i} className="pt-2">
                                  <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">{item.replace('###', '').trim()}</span>
                                </li>
                              );
                            }
                            return (
                              <li key={i} className="flex items-start text-xs text-gray-600 dark:text-gray-300">
                                <span className="mr-2 text-blue-500 mt-0.5">•</span>
                                <span className="leading-relaxed">{item}</span>
                              </li>
                            );
                          })}
                        </ul>
                      </div>
                    </div>
                  </motion.div>
                ) : (
                  <div className="h-full flex flex-col items-center justify-center text-center p-8 text-gray-400 dark:text-slate-600">
                    <div className="bg-gray-50 dark:bg-slate-800/50 p-5 rounded-full mb-4">
                      <FileText className="w-12 h-12 opacity-50" />
                    </div>
                    <div className="max-w-xs space-y-1">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">AI Analysis Dashboard</h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Upload your resume and paste the job description on the left to generate a comprehensive fit analysis here.
                      </p>
                    </div>
                  </div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </main>

      {/* Footer - Mini */}
      <footer className="py-2 text-center bg-white border-t border-gray-100 flex-shrink-0">
        <p className="text-[10px] text-gray-400 font-medium uppercase tracking-tighter">
          AI insights guide • Created with Gemini • Human verification recommended
        </p>
      </footer>
    </div>
  );
}
