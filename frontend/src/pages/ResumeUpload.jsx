import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  Trash2, 
  RefreshCw, 
  Sparkles, 
  ArrowRight, 
  AlertCircle,
  Cpu,
  Layers,
  FileCheck
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { AIOrb } from '../components/common/AIOrb';
import { SAMPLE_JOB_DESCRIPTION } from '../data/mockData';
import { analysisService } from '../utils/apiService';

export const ResumeUpload = ({ navigate, onAnalysisComplete, onCandidateUpdate }) => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [progressPercent, setProgressPercent] = useState(0);
  const [currentStepText, setCurrentStepText] = useState('');
  
  const fileInputRef = useRef(null);

  const timelineSteps = [
    { title: "Resume uploaded & verified", state: "done" },
    { title: "Extracting candidate technical profile & history", state: "done" },
    { title: "Reading target job description requirements", state: "active" },
    { title: "Comparing technical competencies & frameworks", state: "pending" },
    { title: "Identifying skill gaps & learning paths", state: "pending" },
    { title: "Generating personalized career readiness matrix", state: "pending" }
  ];

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      setFile({
        name: droppedFile.name,
        size: `${(droppedFile.size / (1024 * 1024)).toFixed(1)} MB`,
        uploaded: true
      });
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selected = e.target.files[0];
      setFile({
        name: selected.name,
        size: `${(selected.size / (1024 * 1024)).toFixed(1)} MB`,
        uploaded: true
      });
    }
  };

  const handleUseSampleJD = () => {
    setJobDescription(SAMPLE_JOB_DESCRIPTION);
  };

  const handleRemoveFile = () => {
    setFile(null);
  };

  const handleStartAnalysis = async () => {
    if (!file) {
      alert("Please upload your resume before running analysis.");
      return;
    }
    if (!jobDescription.trim()) {
      alert("Please provide the job description you are targeting.");
      return;
    }

    setIsAnalyzing(true);
    setAnalysisStep(1);
    setProgressPercent(15);

    // Run simulated multi-step AI Agent process
    await analysisService.analyzeProfile(file, jobDescription, (update) => {
      setAnalysisStep(update.step);
      setProgressPercent(update.progress);
      setCurrentStepText(update.text);
    });

    setTimeout(() => {
      if (onAnalysisComplete) onAnalysisComplete();
      navigate('gap-analysis');
    }, 600);
  };

  return (
    <div className="py-10 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto">
      
      {/* PROCESSING MODAL OVERLAY (SECTION 5) */}
      <AnimatePresence>
        {isAnalyzing && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/90 backdrop-blur-xl">
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className="w-full max-w-xl bg-navy-900 border border-slate-700/80 rounded-3xl p-8 shadow-2xl text-center space-y-6"
            >
              <div className="flex justify-center">
                <AIOrb size="md" speaking={true} />
              </div>

              <div>
                <h3 className="text-xl sm:text-2xl font-serif font-bold text-white">
                  AI is analyzing your career profile...
                </h3>
                <p className="text-xs text-slate-400 mt-1">
                  Our neural agents are benchmarking your resume against target requirements.
                </p>
              </div>

              {/* Progress Bar */}
              <div className="space-y-1.5 text-left">
                <div className="flex justify-between text-xs font-mono font-medium">
                  <span className="text-slate-400 truncate pr-2">{currentStepText || "Parsing syntax..."}</span>
                  <span className="text-coral">{progressPercent}%</span>
                </div>
                <div className="w-full bg-navy-950 h-3 rounded-full overflow-hidden border border-white/5">
                  <motion.div
                    animate={{ width: `${progressPercent}%` }}
                    transition={{ ease: "easeOut", duration: 0.4 }}
                    className="h-full bg-gradient-to-r from-coral via-amber-400 to-coral rounded-full"
                  />
                </div>
              </div>

              {/* Live Timeline List */}
              <div className="space-y-2.5 text-left text-xs bg-navy-950/70 p-4 rounded-2xl border border-white/5">
                {timelineSteps.map((step, idx) => {
                  const isDone = analysisStep > idx + 1;
                  const isCurrent = analysisStep === idx + 1;
                  return (
                    <div key={idx} className="flex items-center gap-2.5">
                      {isDone ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      ) : isCurrent ? (
                        <span className="w-4 h-4 rounded-full border-2 border-coral border-t-transparent animate-spin shrink-0" />
                      ) : (
                        <span className="w-4 h-4 rounded-full border border-slate-600 shrink-0" />
                      )}
                      <span className={`${isDone ? 'text-slate-300' : isCurrent ? 'text-coral font-semibold' : 'text-slate-500'}`}>
                        {step.title}
                      </span>
                    </div>
                  );
                })}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Main Upload Screen Header */}
      <div className="text-center max-w-2xl mx-auto mb-10 space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-coral/10 border border-coral/25 text-coral text-xs font-mono font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          <span>NEURAL MATCHING ENGINE</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-white tracking-tight">
          Let's understand where you stand.
        </h1>
        <p className="text-slate-400 text-xs sm:text-sm">
          Upload your resume and provide the job you're targeting. Our AI will compute your skill match and gaps.
        </p>
      </div>

      <div className="space-y-8">
        
        {/* STEP 1: RESUME UPLOAD */}
        <div className="bg-navy-800/80 backdrop-blur-md border border-white/10 rounded-3xl p-6 sm:p-8 shadow-subtle">
          <div className="flex items-center gap-3 mb-4">
            <span className="w-7 h-7 rounded-xl bg-coral text-navy-950 font-bold font-mono text-xs flex items-center justify-center">
              1
            </span>
            <div>
              <h3 className="text-base font-bold text-white font-sans">
                Upload Your Resume
              </h3>
              <p className="text-xs text-slate-400">
                Supports PDF, DOC, DOCX (Max 10 MB)
              </p>
            </div>
          </div>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileInputChange}
            accept=".pdf,.doc,.docx"
            className="hidden"
          />

          {!file ? (
            /* Drag and Drop Zone */
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`border-2 border-dashed rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition-all duration-200 ${
                isDragging
                  ? 'border-coral bg-coral/5 scale-[1.01]'
                  : 'border-slate-700/80 hover:border-coral/50 hover:bg-white/[0.02]'
              }`}
            >
              <div className="w-14 h-14 rounded-2xl bg-coral/10 text-coral flex items-center justify-center mx-auto mb-4">
                <UploadCloud className="w-7 h-7" />
              </div>
              <h4 className="text-sm font-semibold text-white mb-1">
                Upload Resume
              </h4>
              <p className="text-xs text-slate-400 mb-4">
                Drag & drop your resume here or <span className="text-coral underline font-medium">browse files</span>
              </p>
              <span className="inline-block px-3 py-1 rounded-full bg-navy-950 text-[10px] font-mono text-slate-400 border border-white/5">
                ATS-Compliant Parsing Active
              </span>
            </div>
          ) : (
            /* File Uploaded Card */
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-5 rounded-2xl bg-navy-950/80 border border-emerald-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="flex items-center gap-3.5">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                  <FileCheck className="w-6 h-6" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h4 className="text-sm font-semibold text-white font-mono">
                      {file.name}
                    </h4>
                    <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                      Uploaded
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    {file.size} • Verified ATS Format
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-auto">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-3 py-1.5 rounded-xl border border-white/10 hover:border-coral/40 text-xs text-slate-300 hover:text-white transition-colors cursor-pointer flex items-center gap-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" /> Replace
                </button>
                <button
                  type="button"
                  onClick={handleRemoveFile}
                  className="px-3 py-1.5 rounded-xl border border-rose-500/20 hover:bg-rose-500/10 text-xs text-rose-400 transition-colors cursor-pointer flex items-center gap-1.5"
                >
                  <Trash2 className="w-3.5 h-3.5" /> Remove
                </button>
              </div>
            </motion.div>
          )}
        </div>

        {/* STEP 2: JOB DESCRIPTION */}
        <div className="bg-navy-800/80 backdrop-blur-md border border-white/10 rounded-3xl p-6 sm:p-8 shadow-subtle">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div className="flex items-center gap-3">
              <span className="w-7 h-7 rounded-xl bg-coral text-navy-950 font-bold font-mono text-xs flex items-center justify-center">
                2
              </span>
              <div>
                <h3 className="text-base font-bold text-white font-sans">
                  Target Job Description
                </h3>
                <p className="text-xs text-slate-400">
                  Paste the job posting you want to optimize for
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={handleUseSampleJD}
              className="px-3 py-1.5 rounded-xl bg-coral/10 hover:bg-coral/20 border border-coral/30 text-coral text-xs font-semibold transition-all cursor-pointer flex items-center gap-1.5 self-start sm:self-auto"
            >
              <Sparkles className="w-3.5 h-3.5" /> Use Sample Full Stack JD
            </button>
          </div>

          <div className="relative">
            <textarea
              rows={8}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the job description you're targeting here..."
              className="w-full bg-navy-950 border border-slate-700/80 rounded-2xl p-4 text-xs sm:text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-coral transition-colors resize-y font-mono leading-relaxed"
            />
            <div className="flex justify-between items-center mt-2 text-xs text-slate-500 font-mono">
              <span>Auto-detects: Skills, Years of Exp, Frameworks, Certifications</span>
              <span>{jobDescription.length} characters</span>
            </div>
          </div>
        </div>

        {/* STEP 3: SUBMIT ACTION */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-6 rounded-3xl bg-navy-800/60 border border-white/10">
          <div>
            <h4 className="text-sm font-bold text-white">Ready for AI Gap Analysis</h4>
            <p className="text-xs text-slate-400 mt-0.5">
              Comparison takes ~3 seconds to extract tech stack alignments and generate a customized study plan.
            </p>
          </div>

          <Button
            size="lg"
            onClick={handleStartAnalysis}
            className="w-full sm:w-auto shadow-glow-coral text-navy-950 font-bold text-sm px-8"
          >
            Analyze My Profile →
          </Button>
        </div>

      </div>

    </div>
  );
};
