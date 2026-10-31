import React from 'react';
import { Clock, ShieldCheck, Video, PhoneOff } from 'lucide-react';

export const MeetHeader = ({
  role = "Full Stack Developer",
  currentQIndex = 0,
  totalQuestions = 6,
  phase = "technical_core",
  questionType = "technical",
  skillTested = "React / Node.js",
  difficulty = "medium",
  timeRemainingSec = 90,
  totalLimitSec = 90,
  onEndCall
}) => {
  const formatTime = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  const getDifficultyColor = (diff) => {
    switch (diff?.toLowerCase()) {
      case "easy":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      case "hard":
        return "bg-rose-500/20 text-rose-400 border-rose-500/30";
      case "medium":
      default:
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
    }
  };

  const isLowTime = timeRemainingSec <= 15 && timeRemainingSec > 0;

  return (
    <header className="h-16 px-4 sm:px-6 bg-[#202124] border-b border-[#3c4043] flex items-center justify-between text-white select-none shrink-0 z-20">
      {/* Left: Live status and Target Role */}
      <div className="flex items-center space-x-3">
        <div className="flex items-center space-x-2 bg-emerald-500/10 text-emerald-400 px-2.5 py-1 rounded-full text-xs font-mono font-medium border border-emerald-500/20">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>LIVE INTERVIEW</span>
        </div>
        <h1 className="text-xs sm:text-sm font-semibold tracking-wide text-neutral-200 hidden md:block truncate max-w-xs">
          {role}
        </h1>
      </div>

      {/* Center: Phase, Question Progress, and Difficulty */}
      <div className="flex items-center space-x-2">
        <div className="bg-[#3c4043] px-3 py-1 rounded-full text-xs font-medium text-neutral-200">
          Question {currentQIndex + 1} of {totalQuestions}
        </div>
        
        {phase === "farewell" ? (
          <div className="uppercase tracking-wider text-[11px] font-bold px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 hidden sm:block">
            Farewell
          </div>
        ) : questionType === "hr" ? (
          <div className="uppercase tracking-wider text-[11px] font-semibold px-2.5 py-1 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30 hidden sm:block">
            HR Round
          </div>
        ) : (
          <div className="uppercase tracking-wider text-[11px] font-semibold px-2.5 py-1 rounded-full bg-blue-500/15 text-blue-400 border border-blue-500/30 hidden sm:block">
            Technical
          </div>
        )}

        {skillTested && (
          <div className="text-[11px] font-medium px-2.5 py-0.5 rounded-full bg-neutral-800 text-neutral-300 border border-[#3c4043] hidden lg:block">
            {skillTested}
          </div>
        )}

        <div className={`text-[11px] capitalize font-medium px-2 py-0.5 rounded border ${getDifficultyColor(difficulty)}`}>
          {difficulty}
        </div>
      </div>

      {/* Right: Countdown Timer */}
      <div className="flex items-center space-x-3">
        <div className={`flex items-center space-x-1.5 text-xs font-mono px-3 py-1.5 rounded-lg border transition-all ${
          isLowTime 
            ? "bg-rose-950/40 text-rose-300 border-rose-500/40 animate-pulse" 
            : "bg-[#28292c] text-neutral-300 border-[#3c4043]"
        }`}>
          <Clock className={`w-3.5 h-3.5 ${isLowTime ? "text-rose-400" : "text-neutral-400"}`} />
          <span>{formatTime(timeRemainingSec)}</span>
        </div>

        {onEndCall && (
          <button
            onClick={onEndCall}
            title="End Interview"
            className="hidden sm:flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 text-xs font-medium transition-all"
          >
            <PhoneOff className="w-3.5 h-3.5" />
            <span>Leave</span>
          </button>
        )}
      </div>
    </header>
  );
};

