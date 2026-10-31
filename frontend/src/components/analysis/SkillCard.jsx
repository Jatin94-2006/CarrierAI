import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, AlertCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { ProgressBar } from '../common/AIOrb'; // We exported ProgressBar from AIOrb or let's import directly

export const SkillCard = ({
  skill,
  type = 'strong', // strong | moderate | missing
  onLearnMore
}) => {
  const configs = {
    strong: {
      borderColor: 'border-emerald-500/30 hover:border-emerald-500/60',
      badgeBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      icon: <CheckCircle2 className="w-4 h-4 text-emerald-400" />,
      tag: "Strong Match",
      progressColor: 'emerald'
    },
    moderate: {
      borderColor: 'border-amber-500/30 hover:border-amber-500/60',
      badgeBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      icon: <AlertTriangle className="w-4 h-4 text-amber-400" />,
      tag: "Needs Practice",
      progressColor: 'amber'
    },
    missing: {
      borderColor: 'border-rose-500/30 hover:border-rose-500/60',
      badgeBg: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
      icon: <AlertCircle className="w-4 h-4 text-rose-400" />,
      tag: "Skill Gap",
      progressColor: 'rose'
    }
  };

  const current = configs[type] || configs.strong;

  return (
    <motion.div
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className={`rounded-2xl p-5 bg-navy-800/80 backdrop-blur-md border ${current.borderColor} transition-all shadow-subtle flex flex-col justify-between`}
    >
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            {current.icon}
            <h4 className="font-semibold text-white text-base font-sans">{skill.name}</h4>
          </div>
          <span className={`text-[10px] uppercase font-mono px-2 py-0.5 rounded-full border ${current.badgeBg}`}>
            {current.tag}
          </span>
        </div>

        <p className="text-xs text-slate-400 leading-relaxed mb-4 min-h-[34px]">
          {skill.desc}
        </p>
      </div>

      <div className="space-y-3 pt-3 border-t border-white/5">
        {/* Comparison bars */}
        <div className="space-y-1.5">
          <div className="flex justify-between text-[11px]">
            <span className="text-slate-400">Your Current Level</span>
            <span className="text-white font-mono font-medium">{skill.level}%</span>
          </div>
          <div className="w-full bg-navy-950 h-2 rounded-full overflow-hidden border border-white/5">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${skill.level}%` }}
              transition={{ duration: 1 }}
              className={`h-full rounded-full ${
                type === 'strong' ? 'bg-emerald-400' : type === 'moderate' ? 'bg-amber-400' : 'bg-rose-400'
              }`}
            />
          </div>
        </div>

        <div className="space-y-1.5">
          <div className="flex justify-between text-[11px]">
            <span className="text-slate-400">Target Role Requirement</span>
            <span className="text-coral font-mono font-medium">{skill.required}%</span>
          </div>
          <div className="w-full bg-navy-950 h-2 rounded-full overflow-hidden border border-white/5">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${skill.required}%` }}
              transition={{ duration: 1 }}
              className="h-full rounded-full bg-coral/80"
            />
          </div>
        </div>

        {skill.gap && (
          <div className="flex items-center justify-between pt-1 text-[11px] font-mono">
            <span className="text-slate-500">Deficit Gap:</span>
            <span className="text-rose-400 font-bold">-{skill.gap}%</span>
          </div>
        )}
      </div>
    </motion.div>
  );
};
