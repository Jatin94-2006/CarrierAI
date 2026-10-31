import React from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Clock, Award, BookOpen, Sparkles } from 'lucide-react';
import { Button } from '../common/Button';

export const ResourceCard = ({ resource, onStartLearning }) => {
  const badgeColors = {
    freeCodeCamp: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    'Microsoft Learn': 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    YouTube: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
    NPTEL: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  };

  return (
    <motion.div
      whileHover={{ y: -4 }}
      className="bg-navy-800/80 backdrop-blur-md border border-white/10 hover:border-coral/40 rounded-2xl p-6 transition-all shadow-subtle flex flex-col justify-between"
    >
      <div>
        {/* Header badges */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className={`text-[10px] font-mono uppercase px-2.5 py-1 rounded-full border ${badgeColors[resource.badge] || 'bg-slate-800 text-slate-300'}`}>
            {resource.badge}
          </span>
          <span className="text-[11px] font-medium text-slate-400 flex items-center gap-1">
            <Clock className="w-3.5 h-3.5 text-coral" /> {resource.duration}
          </span>
        </div>

        <h4 className="text-base font-bold text-white mb-1.5 leading-snug">
          {resource.title}
        </h4>

        <div className="flex items-center gap-3 text-xs text-slate-400 mb-3">
          <span className="text-coral font-medium">{resource.skill}</span>
          <span>•</span>
          <span>{resource.level}</span>
          <span>•</span>
          <span className="text-emerald-400">{resource.type}</span>
        </div>

        {/* Why this is recommended */}
        <div className="p-3 rounded-xl bg-navy-950/80 border border-white/5 mb-5">
          <div className="flex items-start gap-2">
            <Sparkles className="w-3.5 h-3.5 text-coral mt-0.5 shrink-0" />
            <p className="text-[11px] text-slate-300 leading-relaxed">
              <strong className="text-coral font-semibold">Why this is recommended: </strong>
              {resource.why}
            </p>
          </div>
        </div>
      </div>

      <div className="pt-2 flex items-center justify-between gap-3 border-t border-white/5">
        <span className="text-xs text-amber-400 font-mono">
          {resource.rating}
        </span>
        <Button
          size="sm"
          onClick={() => {
            if (onStartLearning) onStartLearning(resource);
            else window.open(resource.link, '_blank');
          }}
          className="gap-1.5"
        >
          Start Learning <ExternalLink className="w-3.5 h-3.5" />
        </Button>
      </div>
    </motion.div>
  );
};
