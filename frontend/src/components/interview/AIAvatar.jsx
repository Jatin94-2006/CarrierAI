import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Bot } from 'lucide-react';

export const AIAvatar = ({ isSpeaking = false, name = "Aria • Lead AI Interviewer" }) => {
  return (
    <div className="relative flex flex-col items-center justify-center p-6 bg-navy-800/90 border border-slate-700/60 rounded-3xl overflow-hidden shadow-2xl">
      {/* Dynamic Background Glow */}
      <div 
        className={`absolute inset-0 transition-opacity duration-700 pointer-events-none ${
          isSpeaking 
            ? 'opacity-30 bg-gradient-to-t from-coral/40 via-purple-600/30 to-transparent' 
            : 'opacity-10 bg-radial from-slate-400 to-transparent'
        }`} 
      />

      {/* Ripple Rings when Speaking */}
      {isSpeaking && (
        <>
          <div className="absolute w-44 h-44 rounded-full border border-coral/40 animate-ping opacity-30" />
          <div className="absolute w-56 h-56 rounded-full border border-amber-400/20 animate-pulse opacity-20" />
        </>
      )}

      {/* Futuristic Animated Avatar Core */}
      <motion.div
        animate={isSpeaking ? { scale: [1, 1.05, 1], rotate: [0, 2, -2, 0] } : {}}
        transition={{ repeat: Infinity, duration: 2.5 }}
        className="relative z-10 w-28 h-28 sm:w-32 sm:h-32 rounded-3xl bg-gradient-to-tr from-navy-950 via-navy-800 to-slate-900 border-2 border-coral/50 p-1.5 shadow-glow-coral flex items-center justify-center"
      >
        <div className="w-full h-full rounded-2xl bg-navy-900 flex flex-col items-center justify-center relative overflow-hidden">
          {/* Inner holographic lines */}
          <div className="absolute inset-0 bg-grid-pattern opacity-40" />
          
          <div className="relative z-10 flex flex-col items-center">
            <Bot className={`w-10 h-10 transition-colors duration-300 ${isSpeaking ? 'text-coral' : 'text-slate-300'}`} />
            
            {/* Audio pulse bars on avatar badge */}
            <div className="flex items-center gap-1 mt-2">
              <span className={`w-1 h-2 rounded-full ${isSpeaking ? 'bg-coral animate-bounce' : 'bg-slate-600'}`} />
              <span className={`w-1 h-3 rounded-full ${isSpeaking ? 'bg-coral animate-bounce delay-75' : 'bg-slate-600'}`} />
              <span className={`w-1 h-2 rounded-full ${isSpeaking ? 'bg-coral animate-bounce delay-150' : 'bg-slate-600'}`} />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Identity Label */}
      <div className="relative z-10 mt-4 text-center">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-navy-950/80 border border-white/10 text-xs font-medium text-slate-200">
          <Sparkles className="w-3 h-3 text-coral" />
          <span>{name}</span>
        </div>
        <p className="text-[11px] text-coral mt-1 font-mono tracking-wide">
          {isSpeaking ? "Speaking & Assessing..." : "Listening attentively..."}
        </p>
      </div>
    </div>
  );
};
