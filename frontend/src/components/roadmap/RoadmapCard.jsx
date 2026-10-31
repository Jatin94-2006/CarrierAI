import React from 'react';
import { motion } from 'framer-motion';
import { 
  CheckCircle2, 
  Circle, 
  Clock, 
  BookOpen, 
  ExternalLink, 
  Layers, 
  Code, 
  Video, 
  Award,
  ChevronRight
} from 'lucide-react';

export const RoadmapCard = ({
  dayData,
  onToggleTask,
  isCurrentDay = false
}) => {
  const categoryBadges = {
    'Learning': 'bg-sky-500/10 text-sky-400 border-sky-500/20',
    'Practice': 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    'Learning & Practice': 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20',
    'Project': 'bg-coral/10 text-coral border-coral/30',
    'Interview Prep': 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
  };

  const completedTasksCount = dayData.tasks.filter(t => t.done).length;
  const totalTasksCount = dayData.tasks.length;
  const isFullyDone = completedTasksCount === totalTasksCount;

  return (
    <motion.div
      whileHover={{ y: -3 }}
      className={`rounded-2xl p-5 sm:p-6 transition-all duration-300 border ${
        isCurrentDay
          ? 'bg-navy-800/95 border-coral/60 shadow-glow-coral'
          : isFullyDone
          ? 'bg-navy-800/60 border-emerald-500/30'
          : 'bg-navy-800/80 border-white/10 hover:border-slate-600'
      }`}
    >
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-3">
        <div className="flex items-center gap-2.5">
          <span className={`px-2.5 py-1 rounded-xl font-mono text-xs font-bold border ${
            isCurrentDay
              ? 'bg-coral text-navy-950 border-coral'
              : isFullyDone
              ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
              : 'bg-navy-950 text-slate-300 border-white/10'
          }`}>
            Day {dayData.day}
          </span>
          <span className={`text-[10px] font-mono uppercase px-2.5 py-0.5 rounded-full border ${categoryBadges[dayData.category] || 'bg-slate-800 text-slate-300'}`}>
            {dayData.category}
          </span>
        </div>

        <div className="flex items-center gap-3 text-xs">
          <span className="text-slate-400 flex items-center gap-1 font-mono">
            <Clock className="w-3.5 h-3.5 text-coral" /> {dayData.duration}
          </span>
          <span className={`text-xs font-mono font-medium ${isFullyDone ? 'text-emerald-400' : 'text-slate-400'}`}>
            {completedTasksCount}/{totalTasksCount} Done
          </span>
        </div>
      </div>

      {/* Title & Description */}
      <h4 className="text-base sm:text-lg font-bold text-white mb-2 leading-snug">
        {dayData.title}
      </h4>
      <p className="text-xs text-slate-400 leading-relaxed mb-4">
        {dayData.description}
      </p>

      {/* Task Checklist */}
      <div className="space-y-2 mb-4 bg-navy-950/60 p-3.5 rounded-xl border border-white/5">
        <p className="text-[11px] font-semibold text-slate-300 uppercase tracking-wider mb-2">
          Daily Action Plan:
        </p>
        {dayData.tasks.map((task, idx) => (
          <div
            key={idx}
            onClick={() => onToggleTask(dayData.day, idx)}
            className="flex items-start gap-2.5 group cursor-pointer select-none"
          >
            <div className="mt-0.5 shrink-0 transition-transform group-hover:scale-110">
              {task.done ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              ) : (
                <Circle className="w-4 h-4 text-slate-500 group-hover:text-coral transition-colors" />
              )}
            </div>
            <span className={`text-xs leading-normal transition-all ${
              task.done
                ? 'line-through text-slate-500'
                : 'text-slate-200 group-hover:text-white'
            }`}>
              {task.text}
            </span>
          </div>
        ))}
      </div>

      {/* Suggested Resource */}
      {dayData.resource && (
        <div className="pt-3 border-t border-white/5 flex items-center justify-between text-xs">
          <span className="text-slate-400 text-[11px] truncate flex items-center gap-1.5">
            <BookOpen className="w-3.5 h-3.5 text-coral shrink-0" />
            <span className="truncate">{dayData.resource}</span>
          </span>
          <span className="text-coral text-[11px] font-medium flex items-center gap-0.5 shrink-0 ml-2">
            Study <ChevronRight className="w-3 h-3" />
          </span>
        </div>
      )}
    </motion.div>
  );
};
