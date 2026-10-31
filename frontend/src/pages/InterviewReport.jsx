import React from 'react';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  Check,
  AlertTriangle, 
  RotateCcw, 
  Download, 
  Award, 
  ShieldCheck, 
  Compass, 
  FileText,
  BarChart2,
  TrendingUp,
  HelpCircle,
  BookOpen,
  ExternalLink,
  GraduationCap,
  Layers,
  Target
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { ScoreRing } from '../components/common/AIOrb';
import { PerformanceChart, QuestionAnalysis } from '../components/interview/QuestionAnalysis';
import { PDFReportButton } from '../components/interview/PDFReportButton';
import { INTERVIEW_REPORT_DATA } from '../data/mockData';

export const InterviewReport = ({ navigate, reportData }) => {
  if (!reportData || !reportData.overallScore) {
    return (
      <div className="py-20 px-4 max-w-2xl mx-auto text-center space-y-6 animate-in fade-in duration-300">
        <div className="w-16 h-16 rounded-3xl bg-coral/10 border border-coral/30 text-coral flex items-center justify-center mx-auto shadow-glow-coral">
          <Award className="w-8 h-8" />
        </div>
        <div className="space-y-2">
          <span className="text-xs font-mono text-coral font-medium uppercase tracking-wider">Awaiting Evaluation</span>
          <h2 className="text-3xl sm:text-4xl font-serif font-bold text-white tracking-tight">
            No Interview Report Yet
          </h2>
          <p className="text-sm text-slate-300 max-w-lg mx-auto leading-relaxed">
            Your comprehensive scorecard, technical accuracy breakdown, demeanor observations, and gap analysis will appear here after you finish your AI mock interview.
          </p>
        </div>
        <div className="pt-4 flex flex-wrap items-center justify-center gap-4">
          <Button
            size="lg"
            onClick={() => navigate('interview-setup')}
            className="shadow-glow-coral text-navy-950 font-bold"
          >
            Start Mock Interview <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
          <Button
            variant="secondary"
            size="lg"
            onClick={() => navigate('resume-analysis')}
          >
            Upload Resume First
          </Button>
        </div>
      </div>
    );
  }
  return (
    <div className="py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-10 animate-in fade-in duration-300">
      
      {/* Printable / Downloadable wrapper container */}
      <div id="interview-report-content" className="space-y-10">
        
        {/* HERO REPORT CARD (SECTION 13) */}
        <div className="relative rounded-3xl bg-gradient-to-r from-navy-800 via-navy-800/90 to-navy-900 border border-white/10 p-6 sm:p-10 shadow-2xl overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-coral/10 rounded-full blur-3xl pointer-events-none" />
          
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
            <div className="space-y-3 text-center md:text-left max-w-2xl">
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-coral/10 border border-coral/25 text-coral text-xs font-mono font-medium">
                <Award className="w-3.5 h-3.5" />
                <span>OFFICIAL PERFORMANCE REPORT</span>
              </div>
              <h1 className="text-3xl sm:text-5xl font-serif font-bold text-white tracking-tight">
                Your Interview Report
              </h1>
              <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
                Here's how you performed during your AI mock session. Evaluated across 5 core competencies for <strong className="text-coral">{reportData.targetRole}</strong>.
              </p>

              {/* Action Buttons */}
              <div className="pt-2 flex flex-wrap items-center justify-center md:justify-start gap-4">
                <PDFReportButton reportData={reportData} />
                <Button
                  variant="secondary"
                  size="lg"
                  onClick={() => navigate('interview-setup')}
                  className="gap-2"
                >
                  <RotateCcw className="w-4 h-4 text-coral" /> Practice Again
                </Button>
              </div>
            </div>

            {/* Overall Score Ring */}
            <div className="flex flex-col items-center justify-center p-6 rounded-3xl bg-navy-950/80 border border-white/10 shadow-inner shrink-0">
              <ScoreRing
                score={reportData.overallScore}
                size={160}
                strokeWidth={12}
                color="#ff806b"
                label={reportData.performanceGrade}
                sublabel={reportData.readinessRating}
              />
              <span className="text-[11px] font-mono text-emerald-400 mt-2 font-medium">
                Target Role Benchmark Passed
              </span>
            </div>
          </div>
        </div>

        {/* 5 CORE SCORE CARDS (SECTION 13) */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          
          <div className="p-4 rounded-2xl bg-navy-800/80 border border-white/10 text-center">
            <span className="text-[11px] text-slate-400 block mb-1">Technical Knowledge</span>
            <strong className="text-2xl sm:text-3xl font-mono font-bold text-white block">
              {reportData.metrics.technicalKnowledge}%
            </strong>
            <span className="text-[10px] text-emerald-400 font-medium mt-1 inline-block">Above Average</span>
          </div>

          <div className="p-4 rounded-2xl bg-navy-800/80 border border-white/10 text-center">
            <span className="text-[11px] text-slate-400 block mb-1">Communication</span>
            <strong className="text-2xl sm:text-3xl font-mono font-bold text-sky-400 block">
              {reportData.metrics.communication}%
            </strong>
            <span className="text-[10px] text-slate-400 font-medium mt-1 inline-block">Clear Tone</span>
          </div>

          <div className="p-4 rounded-2xl bg-navy-800/80 border border-white/10 text-center">
            <span className="text-[11px] text-slate-400 block mb-1">Problem Solving</span>
            <strong className="text-2xl sm:text-3xl font-mono font-bold text-emerald-400 block">
              {reportData.metrics.problemSolving}%
            </strong>
            <span className="text-[10px] text-emerald-400 font-medium mt-1 inline-block">Structured</span>
          </div>

          <div className="p-4 rounded-2xl bg-navy-800/80 border border-white/10 text-center">
            <span className="text-[11px] text-slate-400 block mb-1">Confidence</span>
            <strong className="text-2xl sm:text-3xl font-mono font-bold text-amber-400 block">
              {reportData.metrics.confidence}%
            </strong>
            <span className="text-[10px] text-amber-400 font-medium mt-1 inline-block">Room to Grow</span>
          </div>

          <div className="p-4 rounded-2xl bg-navy-800/80 border border-white/10 text-center col-span-2 sm:col-span-1">
            <span className="text-[11px] text-slate-400 block mb-1">Answer Relevance</span>
            <strong className="text-2xl sm:text-3xl font-mono font-bold text-coral block">
              {reportData.metrics.answerRelevance}%
            </strong>
            <span className="text-[10px] text-coral font-medium mt-1 inline-block">High Alignment</span>
          </div>

        </div>

        {/* PERFORMANCE RADAR CHART & BENCHMARK (SECTION 14) */}
        <PerformanceChart metricsData={reportData.metrics} />

        {/* STRENGTHS AND AREAS TO IMPROVE (SECTION 14) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Strengths */}
          <div className="p-6 rounded-3xl bg-navy-800/80 border border-emerald-500/30 shadow-subtle space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-white/10">
              <div className="p-1.5 rounded-xl bg-emerald-500/15 text-emerald-400">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white font-sans">
                Key Strengths Demonstrated
              </h3>
            </div>
            <div className="space-y-3 text-xs leading-relaxed">
              {reportData.strengths.map((s, idx) => (
                <div key={idx} className="flex items-start gap-2.5">
                  <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span className="text-slate-200">{s}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Areas to Improve */}
          <div className="p-6 rounded-3xl bg-navy-800/80 border border-amber-500/30 shadow-subtle space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-white/10">
              <div className="p-1.5 rounded-xl bg-amber-500/15 text-amber-400">
                <AlertTriangle className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-white font-sans">
                Target Areas for Improvement
              </h3>
            </div>
            <div className="space-y-3 text-xs leading-relaxed">
              {reportData.areasToImprove.map((item, idx) => (
                <div key={idx} className="flex items-start gap-2.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400 shrink-0 mt-1.5" />
                  <span className="text-slate-200">{item}</span>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* QUESTION-WISE DETAILED ANALYSIS (SECTION 15) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold text-white font-sans">
                Question-by-Question AI Breakdown
              </h3>
              <p className="text-xs text-slate-400">
                Click any question to inspect detailed accuracy score and evaluative feedback.
              </p>
            </div>
          </div>

          <QuestionAnalysis questions={reportData.questionAnalyses} />
        </div>

        {/* AI COACH FEEDBACK CARD (SECTION 16) */}
        <div className="p-8 rounded-3xl bg-gradient-to-r from-navy-800 to-navy-900 border border-coral/30 shadow-glow-coral relative overflow-hidden">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
            <div className="space-y-3 max-w-3xl">
              <div className="flex items-center gap-2 text-coral font-bold text-sm">
                <Sparkles className="w-4 h-4" />
                <span>AI Coach Feedback</span>
              </div>
              <p className="text-sm sm:text-base text-slate-200 leading-relaxed font-sans">
                "{reportData.aiCoachFeedback}"
              </p>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-3 w-full sm:w-auto shrink-0">
              <Button
                size="lg"
                onClick={() => navigate('interview-setup')}
                className="shadow-glow-coral text-navy-950 font-bold w-full sm:w-auto"
              >
                Practice Again <RotateCcw className="w-4 h-4 ml-1" />
              </Button>
              <Button
                variant="secondary"
                size="lg"
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                className="w-full sm:w-auto"
              >
                View Full Report
              </Button>
            </div>
          </div>
        </div>

        {/* DUAL-TRACK UPSKILLING COURSES: TECHNICAL & BEHAVIORAL/INTERVIEW (AGENT 2 + AGENT 3) */}
        <div className="space-y-6 pt-4 border-t border-white/10">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-coral/10 border border-coral/25 text-coral text-xs font-mono font-medium mb-2">
                <GraduationCap className="w-3.5 h-3.5" />
                <span>AGENT 3 CURATED MICRO-COURSES (&lt; 1 WEEK)</span>
              </div>
              <h3 className="text-2xl font-serif font-bold text-white">
                Targeted Upskilling: Technical & Interview Competencies
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Personalized short courses curated to bridge deficits detected across both resume screening and your live interview.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-semibold">
                Technical Track
              </span>
              <span className="px-3 py-1 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/30 text-xs font-semibold">
                Interview Delivery Track
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {(reportData.recommendations && reportData.recommendations.length > 0
              ? reportData.recommendations
              : [
                  {
                    id: 'rec-t-1',
                    skill: reportData.combinedGaps?.[0] || 'System Architecture',
                    category: 'Technical Competency',
                    title: `${reportData.combinedGaps?.[0] || 'System Architecture'} Fast-Track Specialization`,
                    badge: 'freeCodeCamp',
                    level: 'Intermediate',
                    estimatedHours: '< 1 week',
                    whyMatters: 'Identified during technical question evaluation and resume screening.',
                    link: 'https://freecodecamp.org'
                  },
                  {
                    id: 'rec-s-1',
                    skill: 'Behavioral Communication',
                    category: 'Communication & Interview Delivery',
                    title: 'STAR Method & Engineering Articulation',
                    badge: 'Coursera',
                    level: 'Professional Development',
                    estimatedHours: '< 1 week',
                    whyMatters: 'Strengthens verbal articulation, structured responses, and confidence.',
                    link: 'https://coursera.org'
                  }
                ]
            ).map((rec) => {
              const isTech = rec.category?.toLowerCase().includes('technical');
              return (
                <div
                  key={rec.id}
                  className="p-5 rounded-2xl bg-navy-800/80 border border-white/10 hover:border-coral/40 transition-all space-y-3 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between text-xs mb-2">
                      <span className={`px-2.5 py-0.5 rounded-full font-mono font-bold text-[11px] ${
                        isTech ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30' : 'bg-sky-500/15 text-sky-400 border border-sky-500/30'
                      }`}>
                        {rec.category || (isTech ? 'Technical Track' : 'Interview Track')}
                      </span>
                      <span className="text-slate-400 font-mono text-xs">{rec.estimatedHours || '< 1 week'}</span>
                    </div>

                    <h4 className="text-base font-bold text-white mt-1">{rec.title}</h4>
                    <p className="text-xs text-slate-300 leading-relaxed mt-2 p-3 rounded-xl bg-navy-950/80 border border-white/5">
                      <strong className="text-coral">Why this matters: </strong>
                      {rec.whyMatters}
                    </p>
                  </div>

                  <div className="flex items-center justify-between gap-2 pt-3 border-t border-white/5">
                    <span className="text-[11px] font-mono text-slate-400">
                      Platform: <strong className="text-slate-200">{rec.badge || 'Online'}</strong>
                    </span>
                    <Button
                      size="sm"
                      onClick={() => window.open(rec.link || 'https://freecodecamp.org', '_blank')}
                      className="gap-1 text-xs shadow-glow-coral text-navy-950 font-bold"
                    >
                      Start Learning <ExternalLink className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>

      {/* Bottom Sticky Action Bar (Section 17) */}
      <div className="pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
        <Button
          variant="secondary"
          onClick={() => navigate('resume-analysis')}
          className="w-full sm:w-auto"
        >
          <FileText className="w-4 h-4 mr-2 text-coral" />
          Start New Assessment
        </Button>

        <PDFReportButton reportData={reportData} />
      </div>

    </div>
  );
};
