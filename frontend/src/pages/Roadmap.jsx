import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Compass, 
  Sparkles, 
  CheckCircle2, 
  Clock, 
  Filter, 
  Search, 
  ArrowRight, 
  BookOpen, 
  Award,
  Video,
  Layers
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { RoadmapCard } from '../components/roadmap/RoadmapCard';
import { roadmapService } from '../utils/apiService';
import { THIRTY_DAY_ROADMAP } from '../data/mockData';
import confetti from 'canvas-confetti';

export const Roadmap = ({ navigate }) => {
  const [roadmap, setRoadmap] = useState(() => roadmapService.getRoadmap());
  const [activeFilter, setActiveFilter] = useState('all'); // all | completed | in-progress | upcoming
  const [searchQuery, setSearchQuery] = useState('');

  // Calculate statistics
  const totalDays = roadmap.length;
  const completedDays = roadmap.filter(d => d.tasks.every(t => t.done)).length;
  const totalTasks = roadmap.reduce((acc, d) => acc + d.tasks.length, 0);
  const completedTasks = roadmap.reduce((acc, d) => acc + d.tasks.filter(t => t.done).length, 0);
  const completionPercentage = Math.round((completedTasks / totalTasks) * 100);

  const handleToggleTask = (dayNumber, taskIndex) => {
    setRoadmap(prev => {
      const updated = prev.map(d => {
        if (d.day === dayNumber) {
          const updatedTasks = [...d.tasks];
          updatedTasks[taskIndex] = {
            ...updatedTasks[taskIndex],
            done: !updatedTasks[taskIndex].done
          };
          return { ...d, tasks: updatedTasks };
        }
        return d;
      });

      // Save state
      roadmapService.saveRoadmap(updated);

      // Trigger celebratory micro-confetti if day just completed
      const targetDay = updated.find(d => d.day === dayNumber);
      if (targetDay && targetDay.tasks.every(t => t.done)) {
        confetti({
          particleCount: 40,
          spread: 45,
          origin: { y: 0.8 },
          colors: ['#ff806b', '#34d399']
        });
      }

      return updated;
    });
  };

  // Filter roadmap items
  const filteredRoadmap = roadmap.filter(d => {
    const isDone = d.tasks.every(t => t.done);
    const isCurrent = d.day === 12;

    if (activeFilter === 'completed' && !isDone) return false;
    if (activeFilter === 'in-progress' && isDone) return false;
    if (activeFilter === 'upcoming' && (isDone || isCurrent)) return false;

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchTitle = d.title.toLowerCase().includes(q);
      const matchCategory = d.category.toLowerCase().includes(q);
      const matchDesc = d.description.toLowerCase().includes(q);
      const matchTasks = d.tasks.some(t => t.text.toLowerCase().includes(q));
      return matchTitle || matchCategory || matchDesc || matchTasks;
    }

    return true;
  });

  return (
    <div className="py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-10 animate-in fade-in duration-300">
      
      {/* HEADER WITH COMPLETION METRICS */}
      <div className="relative rounded-3xl bg-gradient-to-r from-navy-800 via-navy-800/90 to-navy-900 border border-white/10 p-6 sm:p-10 shadow-2xl overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-coral/10 rounded-full blur-3xl pointer-events-none" />
        
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="space-y-3 text-center md:text-left max-w-2xl">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-coral/10 border border-coral/25 text-coral text-xs font-mono font-medium">
              <Compass className="w-3.5 h-3.5" />
              <span>STRUCTURED CAREER BLUEPRINT</span>
            </div>
            <h1 className="text-3xl sm:text-5xl font-serif font-bold text-white tracking-tight">
              Your 30-Day Job Roadmap
            </h1>
            <p className="text-slate-300 text-xs sm:text-sm leading-relaxed">
              Every day outlines focused technical study, practical coding drills, real projects, and behavioral interview coaching tailored to your detected skill gaps.
            </p>

            <div className="pt-2 flex flex-wrap items-center justify-center md:justify-start gap-4">
              <Button
                size="md"
                onClick={() => navigate('interview-setup')}
                className="shadow-glow-coral text-navy-950 font-bold"
              >
                Launch Mock Interview →
              </Button>
              <Button
                variant="secondary"
                size="md"
                onClick={() => navigate('gap-analysis')}
              >
                Review Skill Gaps
              </Button>
            </div>
          </div>

          {/* Roadmap Completion Stat Card */}
          <div className="p-6 rounded-3xl bg-navy-950/80 border border-white/10 shadow-inner text-center shrink-0 min-w-[220px]">
            <span className="text-xs font-mono text-slate-400 uppercase tracking-wider block mb-1">
              Curriculum Progress
            </span>
            <div className="flex items-baseline justify-center gap-1">
              <strong className="text-4xl font-mono font-bold text-coral">{completionPercentage}%</strong>
              <span className="text-xs font-mono text-slate-400">Complete</span>
            </div>
            <div className="w-full bg-navy-900 h-2 rounded-full overflow-hidden mt-3 mb-2 border border-white/5">
              <div
                className="bg-coral h-full rounded-full transition-all duration-500"
                style={{ width: `${completionPercentage}%` }}
              />
            </div>
            <span className="text-[11px] font-mono text-emerald-400">
              {completedDays} of 30 Days Achieved
            </span>
          </div>
        </div>
      </div>

      {/* FILTER & SEARCH BAR */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-navy-800/80 border border-white/10">
        
        {/* Search Input */}
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search topics (e.g. React, Docker, JWT)..."
            className="w-full bg-navy-950 border border-slate-700/80 rounded-xl py-2 pl-10 pr-4 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-coral transition-colors"
          />
        </div>

        {/* Filter buttons */}
        <div className="flex flex-wrap items-center gap-1.5 self-start sm:self-auto">
          {[
            { id: 'all', label: 'All Days (30)' },
            { id: 'in-progress', label: 'In Progress / Current' },
            { id: 'completed', label: 'Completed' },
            { id: 'upcoming', label: 'Upcoming' }
          ].map(f => (
            <button
              key={f.id}
              onClick={() => setActiveFilter(f.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all cursor-pointer ${
                activeFilter === f.id
                  ? 'bg-coral text-navy-950 font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-white/5'
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>

      </div>

      {/* 30-DAY ROADMAP GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredRoadmap.map((dayItem) => (
          <RoadmapCard
            key={dayItem.day}
            dayData={dayItem}
            isCurrentDay={dayItem.day === 12}
            onToggleTask={handleToggleTask}
          />
        ))}
      </div>

      {filteredRoadmap.length === 0 && (
        <div className="p-12 text-center rounded-3xl bg-navy-800/40 border border-white/5">
          <p className="text-sm text-slate-400">No roadmap days found matching "{searchQuery}".</p>
          <button
            onClick={() => { setSearchQuery(''); setActiveFilter('all'); }}
            className="text-xs text-coral underline mt-2 cursor-pointer"
          >
            Reset Filters
          </button>
        </div>
      )}

      {/* Bottom Milestone Banner */}
      <div className="p-8 rounded-3xl bg-gradient-to-r from-navy-800 to-navy-900 border border-coral/30 shadow-glow-coral flex flex-col sm:flex-row items-center justify-between gap-6">
        <div>
          <h3 className="text-xl font-bold font-serif text-white">
            Day 30 Final Outcome: Full-Stack Placement Readiness
          </h3>
          <p className="text-xs text-slate-300 mt-1 max-w-2xl">
            Following this structured 30-day plan bridges your remaining 3 skill gaps and elevates your interview scoring past the 88% offer threshold.
          </p>
        </div>

        <Button
          size="lg"
          onClick={() => navigate('interview-setup')}
          className="shadow-glow-coral text-navy-950 font-bold shrink-0 w-full sm:w-auto"
        >
          Practice Today's Interview <ArrowRight className="w-4 h-4 ml-1" />
        </Button>
      </div>

    </div>
  );
};
