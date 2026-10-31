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
  AlertTriangle,
  Cpu, 
  Check, 
  Sliders, 
  BookOpen, 
  ExternalLink,
  Award,
  Video,
  Download,
  Layers
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { AIOrb, ScoreRing } from '../components/common/AIOrb';
import { SkillCard } from '../components/analysis/SkillCard';
import { SAMPLE_JOB_DESCRIPTION, HIGH_SCORE_ANALYSIS, LOW_SCORE_ANALYSIS, DETAILED_GAP_DATA } from '../data/mockData';
import { careerService, pdfService } from '../utils/apiService';
import confetti from 'canvas-confetti';

export const ResumeAnalysisFlow = ({ navigate, onSetReportData, onCandidateUpdate }) => {
  // Upload State
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [jobDescription, setJobDescription] = useState('');
  
  // Phase State: 'input' | 'analyzing' | 'score_result' | 'gap_analyzing' | 'low_score_report'
  const [phase, setPhase] = useState('input');

  // Resume Analysis Loading State (Section 5)
  const [analysisStep, setAnalysisStep] = useState(0);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [analysisStepText, setAnalysisStepText] = useState('');

  // Gap Analysis Loading State (Section 8)
  const [gapStep, setGapStep] = useState(0);
  const [gapProgress, setGapProgress] = useState(0);
  const [gapStepText, setGapStepText] = useState('');

  // Results State
  const [scoreData, setScoreData] = useState(HIGH_SCORE_ANALYSIS);
  const [gapData, setGapData] = useState(DETAILED_GAP_DATA);
  const [isDownloadingPDF, setIsDownloadingPDF] = useState(false);

  const fileInputRef = useRef(null);

  const resumeLoadingSteps = [
    "Resume uploaded",
    "Extracting candidate information",
    "Parsing technical skills",
    "Reading job description",
    "Comparing experience with requirements",
    "Evaluating projects and education",
    "Calculating profile score",
    "Finalizing analysis"
  ];

  const gapLoadingSteps = [
    "Resume analysis completed",
    "Job requirements extracted",
    "Comparing required skills",
    "Identifying missing skills",
    "Evaluating proficiency gaps",
    "Generating recommendations"
  ];

  // Drag & Drop handlers
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
      const dropped = e.dataTransfer.files[0];
      setFile({
        name: dropped.name,
        size: `${(dropped.size / (1024 * 1024)).toFixed(1)} MB`,
        uploaded: true,
        fileObject: dropped
      });
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const selected = e.target.files[0];
      setFile({
        name: selected.name,
        size: `${(selected.size / (1024 * 1024)).toFixed(1)} MB`,
        uploaded: true,
        fileObject: selected
      });
    }
  };

  // Submit and start analysis
  const handleSubmit = async () => {
    if (!file) {
      alert("Please upload your resume before proceeding.");
      return;
    }

    setPhase('analyzing');
    setAnalysisStep(1);
    setAnalysisProgress(15);

    const res = await careerService.analyzeResume(file, jobDescription, null, (update) => {
      setAnalysisStep(update.step);
      setAnalysisProgress(update.progress);
      setAnalysisStepText(update.text);
    });

    if (!res || !res.success || !res.data) {
      alert(res?.error || "Unable to connect to CareerAI backend service at http://127.0.0.1:8000. Please ensure the backend server is running.");
      setPhase('input');
      return;
    }

    if (res.data) {
      setScoreData(res.data);
      if (onCandidateUpdate) {
        onCandidateUpdate({
          name: res.data.candidateName,
          email: res.data.candidateEmail,
          phone: res.data.candidatePhone,
          role: res.data.targetRole,
          skills: res.data.matchedSkills || [],
          score: res.data.overallScore,
          rank: res.data.simulationRank,
          ...(res.data.candidateProfile || {})
        });
      }
    }
    if (res.gapData) {
      setGapData(res.gapData);
    }

    // Decision criterion based on simulation rank:
    // If simulation rank <= 75 (top 75 personas): Proceed to interview (Path A)
    // If simulation rank > 75: Analyze technical skill gap only & suggest only technical courses (Path B)
    const candRank = res.data?.simulationRank != null ? Number(res.data.simulationRank) : 24;
    const isPathA = candRank <= 75;
    if (isPathA) {
      setTimeout(() => {
        setPhase('score_result');
      }, 500);
    } else {
      setTimeout(() => {
        startAutomaticGapAnalysis();
      }, 500);
    }
  };

  // Automatic Gap Analysis for score < 75
  const startAutomaticGapAnalysis = async () => {
    setPhase('gap_analyzing');
    setGapStep(1);
    setGapProgress(20);

    const gapRes = await careerService.analyzeSkillGaps((update) => {
      setGapStep(update.step);
      setGapProgress(update.progress);
      setGapStepText(update.text);
    });

    if (gapRes.data) {
      setGapData(gapRes.data);
    }

    setTimeout(() => {
      setPhase('low_score_report');
    }, 600);
  };

  const handleProceedToInterview = () => {
    navigate('interview-setup');
  };

  const handleViewFinalReport = () => {
    if (onSetReportData) onSetReportData(scoreData);
    navigate('report');
  };

  const handleDownloadReportPDF = async () => {
    setIsDownloadingPDF(true);
    try {
      await pdfService.generateReportPDF("low-score-report-content", "CareerAI Assessment Report");
      confetti({
        particleCount: 70,
        spread: 60,
        origin: { y: 0.8 },
        colors: ['#ff806b', '#38bdf8', '#34d399']
      });
    } finally {
      setIsDownloadingPDF(false);
    }
  };

  return (
    <div className="py-10 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto select-none">
      
      {/* =====================================================
           PHASE 1: RESUME & JOB DESCRIPTION INPUT SCREEN
      ===================================================== */}
      {phase === 'input' && (
        <div className="space-y-8 animate-in fade-in duration-300">
          
          {/* Header */}
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-coral/10 border border-coral/25 text-coral text-xs font-mono font-medium">
              <Sparkles className="w-3.5 h-3.5" />
              <span>AI RESUME & JD BENCHMARKING</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-serif font-bold text-white tracking-tight">
              Let's understand where you stand.
            </h1>
            <p className="text-slate-400 text-xs sm:text-sm">
              Upload your resume and provide the job you're targeting.
            </p>
          </div>

          {/* Step 1: Resume Upload Area */}
          <div className="bg-[#0b1928]/80 backdrop-blur-md border border-white/10 rounded-3xl p-6 sm:p-8 shadow-subtle">
            <div className="flex items-center gap-3 mb-4">
              <span className="w-7 h-7 rounded-xl bg-coral text-navy-950 font-bold font-mono text-xs flex items-center justify-center">
                1
              </span>
              <div>
                <h3 className="text-base font-bold text-white font-sans">
                  Upload your Resume
                </h3>
                <p className="text-xs text-slate-400">
                  Supported formats: PDF, DOC, DOCX, TXT, JSON
                </p>
              </div>
            </div>

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileInputChange}
              accept=".pdf,.doc,.docx,.txt,.json,application/json,text/plain"
              className="hidden"
            />

            {!file ? (
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
                  Upload your Resume
                </h4>
                <p className="text-xs text-slate-400 mb-2">
                  Drag & drop your resume here or <span className="text-coral underline font-medium">browse</span>
                </p>
                <span className="inline-block text-[10px] font-mono text-slate-500">
                  PDF, DOC, DOCX up to 10 MB
                </span>
              </div>
            ) : (
              <div className="p-5 rounded-2xl bg-navy-950/80 border border-emerald-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-3.5">
                  <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
                    <FileText className="w-6 h-6" />
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
                      {file.size}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="px-3.5 py-1.5 rounded-xl border border-white/10 hover:border-coral/40 text-xs text-slate-300 hover:text-white transition-colors cursor-pointer flex items-center gap-1.5"
                  >
                    <RefreshCw className="w-3.5 h-3.5" /> Replace
                  </button>
                  <button
                    type="button"
                    onClick={() => setFile(null)}
                    className="px-3.5 py-1.5 rounded-xl border border-rose-500/20 hover:bg-rose-500/10 text-xs text-rose-400 transition-colors cursor-pointer flex items-center gap-1.5"
                  >
                    <Trash2 className="w-3.5 h-3.5" /> Remove
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Step 2: Job Description Area */}
          <div className="bg-[#0b1928]/80 backdrop-blur-md border border-white/10 rounded-3xl p-6 sm:p-8 shadow-subtle">
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
                    Paste the job description you're targeting here
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={() => setJobDescription(`Job Title: Python Backend Engineer
Company: CloudScale Systems
Requirements: Python 3, FastAPI or Django, PostgreSQL, Docker, Redis, REST APIs, Git, Unit Testing.`)}
                  className="px-2.5 py-1 rounded-xl bg-sky-500/10 hover:bg-sky-500/20 border border-sky-500/30 text-sky-400 text-xs font-semibold transition-all cursor-pointer"
                >
                  Backend
                </button>
                <button
                  type="button"
                  onClick={() => setJobDescription(`Job Title: Data Scientist / ML Engineer
Company: NeuralMetrics AI
Requirements: Python, Pandas, NumPy, Scikit-learn, TensorFlow or PyTorch, SQL, Machine Learning Model Deployment.`)}
                  className="px-2.5 py-1 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 border border-purple-500/30 text-purple-400 text-xs font-semibold transition-all cursor-pointer"
                >
                  Data Science
                </button>
                <button
                  type="button"
                  onClick={() => setJobDescription(`Job Title: DevOps & Cloud Platform Engineer
Company: InfraOps Global
Requirements: Docker, Kubernetes, AWS or Azure, Terraform, Linux, CI/CD pipelines, Git, Prometheus.`)}
                  className="px-2.5 py-1 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-semibold transition-all cursor-pointer"
                >
                  DevOps
                </button>
                <button
                  type="button"
                  onClick={() => setJobDescription(SAMPLE_JOB_DESCRIPTION)}
                  className="px-2.5 py-1 rounded-xl bg-coral/10 hover:bg-coral/20 border border-coral/30 text-coral text-xs font-semibold transition-all cursor-pointer"
                >
                  Full Stack
                </button>
                {jobDescription && (
                  <button
                    type="button"
                    onClick={() => setJobDescription('')}
                    className="px-2.5 py-1 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-400 text-xs transition-all cursor-pointer"
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>

            <textarea
              rows={8}
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste any target job description here (e.g. Data Scientist, DevOps Engineer, Python Backend, Mobile App Developer)... Leave blank to auto-infer role and requirements directly from your resume."
              className="w-full bg-navy-950 border border-slate-700/80 rounded-2xl p-4 text-xs sm:text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-coral transition-colors font-mono leading-relaxed"
            />
            <div className="flex justify-between items-center mt-2 text-xs text-slate-500 font-mono">
              <span>{jobDescription.trim() ? "Custom role and skills will be parsed dynamically" : "Leave blank to auto-detect target role from resume"}</span>
              <span>{jobDescription.length} characters</span>
            </div>
          </div>

          {/* Submit Action */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-6 rounded-3xl bg-[#0b1928]/90 border border-white/10">
            <div>
              <h4 className="text-sm font-bold text-white">Execute Career Profile Analysis</h4>
              <p className="text-xs text-slate-400 mt-0.5">
                Evaluation takes ~3 seconds to extract tech alignment, calculate ATS score, and benchmark requirements.
              </p>
            </div>

            <Button
              size="lg"
              onClick={handleSubmit}
              className="w-full sm:w-auto shadow-glow-coral text-navy-950 font-bold text-sm px-8"
            >
              Analyze My Profile
            </Button>
          </div>

        </div>
      )}

      {/* =====================================================
           PHASE 2: AI RESUME ANALYSIS LOADING SCREEN (Section 5)
      ===================================================== */}
      {phase === 'analyzing' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/90 backdrop-blur-xl">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-xl bg-[#0b1928] border border-slate-700/80 rounded-3xl p-8 sm:p-10 shadow-2xl text-center space-y-6"
          >
            <div className="flex justify-center">
              <AIOrb size="md" speaking={true} />
            </div>

            <div>
              <h3 className="text-2xl font-serif font-bold text-white">
                Analyzing your career profile
              </h3>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Our AI is analyzing your resume against the target job requirements.
              </p>
            </div>

            {/* Percentage Progress Indicator */}
            <div className="space-y-1.5 text-left">
              <div className="flex justify-between text-xs font-mono font-medium">
                <span className="text-slate-300 truncate pr-2">{analysisStepText || "Analysis in progress"}</span>
                <span className="text-coral font-bold">{analysisProgress}%</span>
              </div>
              <div className="w-full bg-navy-950 h-3 rounded-full overflow-hidden border border-white/5">
                <motion.div
                  animate={{ width: `${analysisProgress}%` }}
                  transition={{ ease: "easeOut", duration: 0.3 }}
                  className="h-full bg-gradient-to-r from-coral via-amber-400 to-coral rounded-full"
                />
              </div>
            </div>

            {/* Live Step-by-Step Timeline (Section 5) */}
            <div className="space-y-2.5 text-left text-xs bg-navy-950/70 p-4 rounded-2xl border border-white/5">
              {resumeLoadingSteps.map((stepTextItem, idx) => {
                const isDone = analysisStep > idx + 1;
                const isCurrent = analysisStep === idx + 1;
                return (
                  <div key={idx} className="flex items-center gap-2.5">
                    {isDone ? (
                      <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                    ) : isCurrent ? (
                      <span className="w-4 h-4 rounded-full border-2 border-coral border-t-transparent animate-spin shrink-0" />
                    ) : (
                      <span className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                    )}
                    <span className={`${isDone ? 'text-slate-300' : isCurrent ? 'text-coral font-semibold' : 'text-slate-500'}`}>
                      {stepTextItem}
                    </span>
                  </div>
                );
              })}
            </div>
          </motion.div>
        </div>
      )}

      {/* =====================================================
           PHASE 3: RESUME SCORE RESULT & DECISION LOGIC (Section 6 & 7)
           (Triggered when Score >= 75)
      ===================================================== */}
      {phase === 'score_result' && (
        <div className="space-y-8 animate-in fade-in duration-300">
          
          {/* Hero Score Ring Card */}
          <div className="relative rounded-3xl bg-gradient-to-r from-[#0b1928] via-[#0b1928]/95 to-[#102235] border border-white/10 p-6 sm:p-10 shadow-2xl overflow-hidden">
            <div className="absolute top-0 right-0 w-80 h-80 bg-coral/10 rounded-full blur-3xl pointer-events-none" />
            
            <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="space-y-3 text-center md:text-left max-w-xl">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-coral/10 border border-coral/25 text-coral text-xs font-mono font-medium">
                  <Award className="w-3.5 h-3.5" />
                  <span>RESUME BENCHMARK RESULT</span>
                </div>
                <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white tracking-tight">
                  Profile Score Calculated
                </h2>
                <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
                  {scoreData.summary}
                </p>
              </div>

              {/* Score Ring */}
              <div className="flex flex-col items-center justify-center p-6 rounded-3xl bg-navy-950/80 border border-white/10 shadow-inner shrink-0">
                <ScoreRing
                  score={scoreData.overallScore}
                  size={150}
                  strokeWidth={11}
                  color="#ff806b"
                  label={scoreData.status}
                  sublabel="Score Benchmark"
                />
                <span className="text-[11px] font-mono text-emerald-400 mt-2 font-medium">
                  Meets Interview Benchmark (≥ 75)
                </span>
              </div>
            </div>
          </div>

          {/* 6 Category Breakdown Bars (Section 6) */}
          <div className="p-6 sm:p-8 rounded-3xl bg-[#0b1928]/80 border border-white/10 space-y-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider pb-3 border-b border-white/10">
              Profile Category Evaluation Breakdown
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
              {scoreData.categories.map((cat, idx) => (
                <div key={idx} className="p-4 rounded-2xl bg-navy-950/60 border border-white/5 space-y-2">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{cat.name}</span>
                    <span className="font-mono text-coral font-bold">{cat.score}%</span>
                  </div>
                  <div className="w-full bg-navy-900 h-2 rounded-full overflow-hidden border border-white/5">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-coral to-amber-400"
                      style={{ width: `${cat.score}%` }}
                    />
                  </div>
                  <p className="text-[11px] text-slate-400">{cat.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* DECISION MODAL / CARD (Section 7: Score >= 75) */}
          <div className="p-8 rounded-3xl bg-gradient-to-r from-[#0b1928] to-[#102235] border border-coral/40 shadow-glow-coral relative overflow-hidden">
            <div className="max-w-2xl space-y-3">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-medium">
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>INTERVIEW QUALIFICATION GRANTED</span>
              </div>
              <h3 className="text-2xl font-serif font-bold text-white">
                Your profile is interview-ready.
              </h3>
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                Your resume shows strong alignment with the target role. Would you like to continue with an AI mock interview?
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-4 pt-6">
              <Button
                size="lg"
                onClick={handleProceedToInterview}
                className="w-full sm:w-auto shadow-glow-coral text-navy-950 font-bold px-8"
              >
                Proceed to Interview <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={handleViewFinalReport}
                className="w-full sm:w-auto"
              >
                View Final Report
              </Button>
            </div>
          </div>

        </div>
      )}

      {/* =====================================================
           PHASE 4: AUTOMATIC GAP ANALYSIS LOADER (Section 8: Score < 75)
      ===================================================== */}
      {phase === 'gap_analyzing' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/90 backdrop-blur-xl">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-xl bg-[#0b1928] border border-slate-700/80 rounded-3xl p-8 sm:p-10 shadow-2xl text-center space-y-6"
          >
            <div className="flex justify-center">
              <AIOrb size="md" speaking={true} />
            </div>

            <div>
              <h3 className="text-2xl font-serif font-bold text-white">
                Identifying your skill gaps
              </h3>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                We found areas where your profile can be improved for this role.
              </p>
            </div>

            <div className="space-y-1.5 text-left">
              <div className="flex justify-between text-xs font-mono font-medium">
                <span className="text-slate-300 truncate pr-2">{gapStepText || "Scanning qualification vectors..."}</span>
                <span className="text-coral font-bold">{gapProgress}%</span>
              </div>
              <div className="w-full bg-navy-950 h-3 rounded-full overflow-hidden border border-white/5">
                <motion.div
                  animate={{ width: `${gapProgress}%` }}
                  transition={{ ease: "easeOut", duration: 0.3 }}
                  className="h-full bg-gradient-to-r from-coral via-amber-400 to-coral rounded-full"
                />
              </div>
            </div>

            {/* Gap Step Timeline */}
            <div className="space-y-2.5 text-left text-xs bg-navy-950/70 p-4 rounded-2xl border border-white/5">
              {gapLoadingSteps.map((stepTextItem, idx) => {
                const isDone = gapStep > idx + 1;
                const isCurrent = gapStep === idx + 1;
                return (
                  <div key={idx} className="flex items-center gap-2.5">
                    {isDone ? (
                      <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                    ) : isCurrent ? (
                      <span className="w-4 h-4 rounded-full border-2 border-coral border-t-transparent animate-spin shrink-0" />
                    ) : (
                      <span className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                    )}
                    <span className={`${isDone ? 'text-slate-300' : isCurrent ? 'text-coral font-semibold' : 'text-slate-500'}`}>
                      {stepTextItem}
                    </span>
                  </div>
                );
              })}
            </div>
          </motion.div>
        </div>
      )}

      {/* =====================================================
           PHASE 5: FINAL REPORT & GAP ANALYSIS FOR LOW-SCORE (Section 9, 10, 11)
      ===================================================== */}
      {phase === 'low_score_report' && (
        <div id="low-score-report-content" className="space-y-10 animate-in fade-in duration-300">
          
          {/* Header Summary */}
          <div className="p-8 rounded-3xl bg-[#0b1928] border border-white/10 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <span className="text-coral text-xs font-mono uppercase tracking-widest font-semibold">
                  TECHNICAL SKILL REMEDIATION REPORT
                </span>
                <h1 className="text-3xl font-serif font-bold text-white mt-1">
                  Technical Skill Gap & Course Recommendations
                </h1>
                <p className="text-xs text-slate-400 mt-1">
                  Simulation Rank: <strong className="text-amber-400">Rank #{gapData.simulationRank || 78} of 100 Personas</strong> (Rank &gt; 75 Threshold: Direct Interview Access Restricted &bull; Technical Remediation Active)
                </p>
              </div>

              <Button
                size="md"
                onClick={handleDownloadReportPDF}
                disabled={isDownloadingPDF}
                className="shadow-glow-coral text-navy-950 font-bold gap-2"
              >
                <Download className="w-4 h-4" />
                <span>{isDownloadingPDF ? "Generating PDF..." : "Download Report PDF"}</span>
              </Button>
            </div>
          </div>

          {/* Metric Cards Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {Object.entries(gapData.finalReportMetrics).map(([key, val]) => (
              <div key={key} className="p-4 rounded-2xl bg-[#0b1928]/80 border border-white/10 text-center">
                <span className="text-[10px] text-slate-400 block mb-1 uppercase font-mono">
                  {key.replace(/([A-Z])/g, ' $1')}
                </span>
                <strong className="text-2xl font-mono font-bold text-white block">{val}%</strong>
              </div>
            ))}
          </div>

          {/* Section 9: Areas to Improve (Strong, Needs Improvement, Missing Skills) */}
          <div className="space-y-6 pt-4">
            <div>
              <h2 className="text-2xl font-serif font-bold text-white">
                {gapData.heading}
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                {gapData.subtitle}
              </p>
            </div>

            {/* Strong Skills */}
            <div>
              <h3 className="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-3">
                Strong Skills (Meets Benchmark)
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {gapData.strongSkills.map((s, idx) => (
                  <SkillCard key={idx} skill={s} type="strong" />
                ))}
              </div>
            </div>

            {/* Needs Improvement */}
            <div>
              <h3 className="text-xs font-bold text-amber-400 uppercase tracking-wider mb-3">
                Needs Improvement (Partial Knowledge)
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {gapData.needsImprovement.map((s, idx) => (
                  <SkillCard key={idx} skill={s} type="moderate" />
                ))}
              </div>
            </div>

            {/* Missing Skills */}
            <div>
              <h3 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-3">
                Missing Skills (High Priority Gaps)
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {gapData.missingSkills.map((s, idx) => (
                  <SkillCard key={idx} skill={s} type="missing" />
                ))}
              </div>
            </div>
          </div>

          {/* Section 10: Recommended Improvements */}
          <div className="space-y-4 pt-4 border-t border-white/10">
            <div>
              <h2 className="text-2xl font-serif font-bold text-white">
                Recommended Improvements
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Targeted learning to bridge your highest-priority gaps.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {gapData.recommendations.map((rec) => (
                <div
                  key={rec.id}
                  className="p-5 rounded-2xl bg-[#0b1928] border border-white/10 hover:border-coral/40 transition-all space-y-3 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between text-xs mb-2">
                      <span className="font-mono text-coral font-bold">{rec.skill}</span>
                      <span className="text-slate-400 font-mono">{rec.estimatedHours}</span>
                    </div>
                    <h4 className="text-base font-bold text-white">{rec.title}</h4>
                    <p className="text-xs text-slate-300 leading-relaxed mt-2 p-3 rounded-xl bg-navy-950/80 border border-white/5">
                      <strong className="text-coral">Why this matters: </strong>
                      {rec.whyMatters}
                    </p>
                  </div>

                  <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/5">
                    <Button
                      size="sm"
                      onClick={() => window.open(rec.link, '_blank')}
                      className="gap-1 text-xs"
                    >
                      Start Learning <ExternalLink className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Section 11: Strengths, Areas to Improve, Missing Skills & Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-white/10">
            
            {/* Strengths */}
            <div className="p-6 rounded-3xl bg-[#0b1928] border border-emerald-500/20 space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider pb-2 border-b border-white/10">
                Strengths
              </h3>
              <div className="space-y-2 text-xs">
                {gapData.strengths.map((st, i) => (
                  <div key={i} className="flex items-start gap-2 text-slate-200">
                    <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                    <span>{st}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Areas to Improve */}
            <div className="p-6 rounded-3xl bg-[#0b1928] border border-amber-500/20 space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider pb-2 border-b border-white/10">
                Areas to Improve
              </h3>
              <div className="space-y-2 text-xs">
                {gapData.areasToImprove.map((item, i) => (
                  <div key={i} className="flex items-start gap-2 text-slate-200">
                    <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="p-6 rounded-3xl bg-[#0b1928] border border-rose-500/20 space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider pb-2 border-b border-white/10">
                Missing Skills
              </h3>
              <div className="space-y-2 text-xs">
                {gapData.missingSkillsList.map((m, i) => (
                  <div key={i} className="flex items-start gap-2 text-slate-200">
                    <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    <span>{m}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommended Actions */}
            <div className="p-6 rounded-3xl bg-[#0b1928] border border-sky-500/20 space-y-3">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider pb-2 border-b border-white/10">
                Recommended Actions
              </h3>
              <div className="space-y-2 text-xs">
                {gapData.recommendedActions.map((act, i) => (
                  <div key={i} className="flex items-start gap-2 text-slate-200">
                    <ArrowRight className="w-4 h-4 text-sky-400 shrink-0 mt-0.5" />
                    <span>{act}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>

          {/* Section 11 Final Statement Banner */}
          <div className="p-6 rounded-2xl bg-[#0b1928] border border-white/10 text-center text-xs sm:text-sm text-slate-300">
            "Your profile can become significantly stronger by addressing the highest-priority skill gaps identified above."
          </div>

          {/* Bottom Actions */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-white/10">
            <Button
              variant="secondary"
              onClick={() => setPhase('input')}
              className="w-full sm:w-auto"
            >
              Start New Analysis
            </Button>

            <Button
              size="lg"
              onClick={() => navigate('interview-setup')}
              className="w-full sm:w-auto bg-navy-800 hover:bg-navy-700 text-coral border border-coral/30 font-bold gap-2"
            >
              <Video className="w-4 h-4" />
              <span>Practice Mock Interview (Agent 4)</span>
            </Button>

            <Button
              size="lg"
              onClick={handleDownloadReportPDF}
              disabled={isDownloadingPDF}
              className="w-full sm:w-auto shadow-glow-coral text-navy-950 font-bold gap-2"
            >
              <Download className="w-4 h-4" />
              <span>{isDownloadingPDF ? "Generating PDF..." : "Download Official PDF (Agent 5)"}</span>
            </Button>
          </div>

        </div>
      )}

    </div>
  );
};
