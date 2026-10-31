import React from 'react';
import { Mic, Volume2, Sparkles, Pin, Bot } from 'lucide-react';

export const InterviewerTile = ({
  isSpeaking = false,
  questionText = "",
  questionType = "technical",
  phase = "intro"
}) => {
  return (
    <div className="relative flex-1 h-full min-h-[340px] sm:min-h-[380px] bg-[#202124] rounded-2xl border border-[#3c4043] flex flex-col items-center justify-center overflow-hidden shadow-2xl transition-all duration-300">
      {/* Background ambient voice glow */}
      {isSpeaking && (
        <div className="absolute inset-0 bg-blue-500/10 blur-3xl pointer-events-none animate-pulse" />
      )}

      {/* Top right pin icon */}
      <div className="absolute top-4 right-4 text-neutral-400 hover:text-white transition-colors bg-[#3c4043]/50 p-2 rounded-full cursor-pointer">
        <Pin className="w-4 h-4" />
      </div>

      {/* Center Voice Visualizer */}
      <div className="flex flex-col items-center justify-center space-y-6 z-10 p-6 text-center">
        <div
          className={`relative w-24 h-24 sm:w-28 sm:h-28 rounded-full flex items-center justify-center transition-all duration-500 ${
            isSpeaking
              ? "bg-blue-600/20 ring-4 ring-blue-500/40 shadow-[0_0_50px_rgba(59,130,246,0.35)] scale-105"
              : "bg-[#28292c] ring-1 ring-[#3c4043]"
          }`}
        >
          {isSpeaking ? (
            <Volume2 className="w-10 h-10 sm:w-12 sm:h-12 text-blue-400 animate-pulse" />
          ) : (
            <Bot className="w-10 h-10 sm:w-12 sm:h-12 text-neutral-400" />
          )}

          {/* Concentric pulsing rings when speaking */}
          {isSpeaking && (
            <>
              <span className="absolute inset-0 rounded-full border-2 border-blue-400/40 animate-ping" />
              <span className="absolute -inset-2 rounded-full border border-blue-500/25 animate-pulse" />
            </>
          )}
        </div>

        {/* Dynamic Sound Wave Bars */}
        <div className="flex items-center space-x-1.5 h-10 sm:h-12">
          {[40, 75, 90, 60, 100, 70, 85, 45, 95, 65, 80, 50].map((h, idx) => (
            <span
              key={idx}
              className={`w-1 rounded-full transition-all duration-200 ${
                isSpeaking
                  ? "bg-gradient-to-t from-blue-500 to-indigo-400"
                  : "bg-neutral-600 h-2"
              }`}
              style={{
                height: isSpeaking ? `${Math.max(8, (h * Math.sin((idx + 1) * 0.8) + 60) * 0.45)}px` : "6px",
                animation: isSpeaking ? `barPulse 1.${2 + (idx % 4)}s ease-in-out infinite` : "none",
                animationDelay: `${idx * 0.08}s`,
              }}
            />
          ))}
        </div>

        {/* Voice status label */}
        <div className="flex items-center space-x-2 text-xs font-medium text-neutral-400">
          <Sparkles className="w-3.5 h-3.5 text-blue-400" />
          <span>
            {isSpeaking
              ? phase === "farewell"
                ? "Interviewer is bidding farewell..."
                : questionType === "hr"
                ? "HR Lead is asking a question..."
                : "AI Technical Lead is speaking..."
              : phase === "intro"
              ? "Welcome & Introduction"
              : phase === "farewell"
              ? "Farewell & Wrap-Up"
              : questionType === "hr"
              ? "HR & Culture Round"
              : "Technical Assessment Round"}
          </span>
        </div>
      </div>

      {/* Bottom left participant tag */}
      <div className="absolute bottom-4 left-4 flex items-center space-x-2 bg-[#202124]/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#3c4043] z-20">
        <span
          className={`w-2.5 h-2.5 rounded-full ${
            isSpeaking ? "bg-emerald-400 animate-pulse" : "bg-neutral-500"
          }`}
        />
        <span className="text-xs font-medium text-neutral-200">
          {questionType === "hr" ? "AI HR Lead" : "AI Technical Lead"}
        </span>
      </div>
    </div>
  );
};

