import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  ArrowRight, 
  CheckCircle2, 
  AlertTriangle, 
  AlertCircle, 
  Video, 
  Compass, 
  RefreshCw,
  Award,
  Layers,
  BookOpen
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { ScoreRing } from '../components/common/AIOrb';
import { SkillCard } from '../components/analysis/SkillCard';
import { SkillGapChart } from '../components/analysis/SkillGapChart';
import { ResourceCard } from '../components/analysis/ResourceCard';
import { SKILL_GAP_DATA, RECOMMENDED_RESOURCES } from '../data/mockData';

export const GapAnalysis = ({ navigate }) => {
  const [loading, setLoading] = useState(true);

  // Artificial AI Loading state as requested in Section 6
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(false);
    }, 1200);

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="min-h-[70vh] flex flex-col items-center justify-center p-8 text-center">
        <div className="relative mb-6">
          <div className="w-20 h-20 rounded-full border-4 border-coral/20 border-t-coral animate-spin" />
          <div className="absolute inset-0 flex items-center justify-center">
            <Sparkles className="w-6 h-6 text-coral animate-pulse" />
          </div>
        </div>
        <h3 className="text-xl sm:text-2xl font-serif font-bold text-white">
          Analyzing skill gaps...
        </h3>
        <p className="text-xs text-slate-400 mt-2 max-w-sm">
          Comparing your profile with target job requirements and computing learning vectors...
        </p>
      </div>
    );
  }

  return (
    <div className="py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-12 animate-in fade-in duration-300">
      
      {/* HEADER WITH CIRCULAR ANIMATED SCORE */}
      <div className="relative rounded-3xl bg-gradient-to-r from-navy-800 via-navy-800/90 to-navy-900 border border-white/10 p-6 sm:p-10 shadow-2xl overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-coral/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="space-y-3 text-center md:text-left max-w-2xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-coral/10 border border-coral/25 text-coral text-xs font-mono font-medium">
              <Sparkles className="w-3.5 h-3.5" />
              <span>COMPUTED SKILL GAP REPORT</span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-serif font-bold text-white tracking-tight">
              Your Skill Gap Analysis
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
              {SKILL_GAP_DATA.summary}
            </p>

            <div className="pt-2 flex flex-wrap items-center justify-center md:justify-start gap-4">
              <Button
                size="md"
                onClick={() => navigate('interview-setup')}
                className="shadow-glow-coral text-navy-950 font-bold"
              >
                Start AI Interview →
              </Button>
              <Button
                variant="secondary"
                size="md"
                onClick={() => navigate('roadmap')}
              >
                Jump to 30-Day Roadmap
              </Button>
            </div>
          </div>

          {/* Top Circular Animated Score */}
          <div className="flex flex-col items-center justify-center p-6 rounded-3xl bg-navy-950/80 border border-white/10 shadow-inner shrink-0">
            <ScoreRing
              score={SKILL_GAP_DATA.overallMatch}
              size={150}
              strokeWidth={11}
              color="#ff806b"
              label="Skill Match"
              sublabel="Target: 85%"
            />
            <span className="text-[11px] font-mono text-emerald-400 mt-2 font-medium">
              Competitive Foundation
            </span>
          </div>
        </div>
      </div>

      {/* SKILL COMPARISON VISUALIZATION (RECHARTS BAR & RADAR) */}
      <SkillGapChart skillsData={SKILL_GAP_DATA} />

      {/* THREE SKILL CATEGORY SECTIONS */}
      <div className="space-y-8">
        
        {/* Section 1: Strong Skills (Green) */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1 rounded-full bg-emerald-500/20 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
            <h3 className="text-base sm:text-lg font-bold text-white font-sans">
              Strong Skills <span className="text-xs text-emerald-400 font-mono font-normal">({SKILL_GAP_DATA.strongSkills.length} Verified)</span>
            </h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {SKILL_GAP_DATA.strongSkills.map((skill, i) => (
              <SkillCard key={i} skill={skill} type="strong" />
            ))}
          </div>
        </div>

        {/* Section 2: Needs Improvement (Orange) */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1 rounded-full bg-amber-500/20 text-amber-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <h3 className="text-base sm:text-lg font-bold text-white font-sans">
              Needs Improvement <span className="text-xs text-amber-400 font-mono font-normal">({SKILL_GAP_DATA.needsImprovement.length} Priorities)</span>
            </h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {SKILL_GAP_DATA.needsImprovement.map((skill, i) => (
              <SkillCard key={i} skill={skill} type="moderate" />
            ))}
          </div>
        </div>

        {/* Section 3: Missing Skills (Red/Rose) */}
        <div>
          <div className="flex items-center gap-2 mb-4">
            <div className="p-1 rounded-full bg-rose-500/20 text-rose-400">
              <AlertCircle className="w-4 h-4" />
            </div>
            <h3 className="text-base sm:text-lg font-bold text-white font-sans">
              Missing Skills <span className="text-xs text-rose-400 font-mono font-normal">({SKILL_GAP_DATA.missingSkills.length} High Impact Gaps)</span>
            </h3>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {SKILL_GAP_DATA.missingSkills.map((skill, i) => (
              <SkillCard key={i} skill={skill} type="missing" />
            ))}
          </div>
        </div>

      </div>

      {/* SECTION 7: AI RECOMMENDATIONS */}
      <div className="pt-6 border-t border-white/10 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="text-coral text-xs font-mono uppercase tracking-widest font-semibold">
              CURATED LEARNING PATHWAYS
            </span>
            <h2 className="text-2xl sm:text-3xl font-serif text-white font-bold mt-1">
              Recommended Learning Resources
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              High-yield certified courses targeting your biggest skill gaps before your interview.
            </p>
          </div>

          <Button
            size="md"
            onClick={() => navigate('interview-setup')}
            className="shadow-glow-coral text-navy-950 font-bold self-start sm:self-auto"
          >
            Start AI Interview →
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {RECOMMENDED_RESOURCES.map((res) => (
            <ResourceCard
              key={res.id}
              resource={res}
              onStartLearning={() => window.open(res.link, '_blank')}
            />
          ))}
        </div>
      </div>

      {/* Bottom CTA to Interview */}
      <div className="p-8 rounded-3xl bg-gradient-to-r from-navy-800 to-navy-900 border border-coral/30 shadow-glow-coral flex flex-col sm:flex-row items-center justify-between gap-6">
        <div>
          <h3 className="text-xl font-bold font-serif text-white">
            Ready to test your knowledge live?
          </h3>
          <p className="text-xs text-slate-300 mt-1">
            Simulate a realistic 15-minute mock interview with our interactive AI voice agent.
          </p>
        </div>

        <Button
          size="lg"
          onClick={() => navigate('interview-setup')}
          className="shadow-glow-coral text-navy-950 font-bold w-full sm:w-auto px-8"
        >
          Start AI Interview →
        </Button>
      </div>

    </div>
  );
};
