import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, CheckCircle2, AlertTriangle, Sparkles, Award } from 'lucide-react';
import { 
  ResponsiveContainer, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend 
} from 'recharts';

export const PerformanceChart = ({ metricsData }) => {
  const chartData = [
    { subject: "Technical Knowledge", score: metricsData?.technicalKnowledge || 82, benchmark: 75 },
    { subject: "Communication", score: metricsData?.communication || 74, benchmark: 70 },
    { subject: "Problem Solving", score: metricsData?.problemSolving || 80, benchmark: 75 },
    { subject: "Confidence", score: metricsData?.confidence || 71, benchmark: 70 },
    { subject: "Answer Relevance", score: metricsData?.answerRelevance || 85, benchmark: 80 }
  ];

  return (
    <div className="bg-navy-800/80 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-subtle">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-white font-sans">
            Competency Radar & Benchmarks
          </h3>
          <p className="text-xs text-slate-400">
            Performance comparison against industry mid-level software engineer standards
          </p>
        </div>
        <span className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-xs">
          <Award className="w-3.5 h-3.5" /> High Potential
        </span>
      </div>

      <div className="w-full h-72">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="75%" data={chartData}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="subject" tick={{ fill: '#cbd5e1', fontSize: 11 }} />
            <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" />
            <Radar name="Your Score" dataKey="score" stroke="#ff806b" fill="#ff806b" fillOpacity={0.45} />
            <Radar name="Industry Benchmark" dataKey="benchmark" stroke="#38bdf8" fill="#38bdf8" fillOpacity={0.2} />
            <Legend 
              wrapperStyle={{ fontSize: 12, paddingTop: 12 }} 
              formatter={(value) => <span className="text-slate-300 font-medium">{value}</span>}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#07121e', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export const QuestionAnalysis = ({ questions = [] }) => {
  const [expandedId, setExpandedId] = useState(1);

  const toggleAccordion = (id) => {
    setExpandedId(prev => (prev === id ? null : id));
  };

  return (
    <div className="space-y-3">
      {questions.map((q) => {
        const isExpanded = expandedId === q.qNum;
        const scoreColor = q.score >= 8.5 ? 'text-emerald-400 border-emerald-500/30' : 'text-amber-400 border-amber-500/30';

        return (
          <div
            key={q.qNum}
            className="rounded-2xl bg-navy-800/80 border border-white/10 overflow-hidden transition-all duration-200"
          >
            <button
              onClick={() => toggleAccordion(q.qNum)}
              className="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-white/5 transition-colors cursor-pointer"
            >
              <div className="flex items-center gap-3.5 pr-4">
                <span className="w-7 h-7 rounded-lg bg-navy-950 border border-white/10 flex items-center justify-center font-mono text-xs font-bold text-coral shrink-0">
                  Q{q.qNum}
                </span>
                <div>
                  <h4 className="text-sm font-semibold text-white leading-snug">
                    {q.question}
                  </h4>
                  <span className="text-[11px] text-slate-400 font-medium">
                    {q.category}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-4 shrink-0">
                <span className={`px-2.5 py-1 rounded-xl bg-navy-950 font-mono font-bold text-xs border ${scoreColor}`}>
                  {q.score} / 10
                </span>
                {isExpanded ? (
                  <ChevronUp className="w-5 h-5 text-slate-400" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-slate-400" />
                )}
              </div>
            </button>

            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="px-5 pb-5 pt-1 border-t border-white/5 bg-navy-950/40 text-xs"
                >
                  <div className="p-4 rounded-xl bg-navy-900/90 border border-coral/20 mt-2 space-y-2">
                    <div className="flex items-center gap-2 text-coral font-semibold text-xs">
                      <Sparkles className="w-4 h-4" />
                      <span>AI Evaluator Feedback:</span>
                    </div>
                    <p className="text-slate-300 leading-relaxed text-xs">
                      "{q.feedback}"
                    </p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
};
