import React from 'react';
import { Sparkles, BookOpen, Mic } from 'lucide-react';

export const QuestionSubtitles = ({
  question,
  isSpeaking = false,
  isRecording = false,
  liveTranscript = ""
}) => {
  if (!question) return null;

  const qText = question.question || question.text || "";
  const skill = question.skill_tested || question.skill || question.category || "Core Competency";
  const phase = question.phase || "technical_core";
  const qType = question.type || "technical";

  return (
    <div className="w-full max-w-4xl mx-auto px-2 sm:px-4 py-2 shrink-0 z-20">
      <div className="bg-[#202124]/95 backdrop-blur-xl border border-[#3c4043] rounded-2xl p-4 sm:p-5 shadow-2xl transition-all duration-300">
        
        {/* Top Badges */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-2 pb-2 border-b border-[#3c4043]/60">
          <div className="flex items-center space-x-2">
            {phase === "farewell" ? (
              <span className="flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                <Sparkles className="w-3 h-3" />
                <span>FAREWELL</span>
              </span>
            ) : qType === "hr" ? (
              <span className="flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-purple-500/15 text-purple-300 border border-purple-500/30">
                <Sparkles className="w-3 h-3" />
                <span>HR QUESTION</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                <Sparkles className="w-3 h-3" />
                <span>TECHNICAL</span>
              </span>
            )}

            <span className="text-xs text-neutral-400 flex items-center space-x-1">
              <BookOpen className="w-3 h-3 text-neutral-500" />
              <span>Competency: <strong className="text-neutral-200">{skill}</strong></span>
            </span>
          </div>

          {isSpeaking && (
            <span className="text-xs text-blue-400 font-medium animate-pulse flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-ping" />
              <span>AI Interviewer Speaking...</span>
            </span>
          )}

          {isRecording && (
            <span className="text-xs text-emerald-400 font-medium animate-pulse flex items-center space-x-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>Recording Voice Response...</span>
            </span>
          )}
        </div>

        {/* Question Text */}
        <p className="text-sm sm:text-base font-sans font-medium text-neutral-100 leading-relaxed">
          {qText}
        </p>

        {/* Live Candidate Subtitle Stream */}
        {isRecording && (
          <div className="mt-3 pt-3 border-t border-[#3c4043]/70 flex items-start space-x-2 text-xs">
            <Mic className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5 animate-pulse" />
            <div className="flex-1">
              <span className="text-neutral-400 font-semibold mr-1.5">You:</span>
              <span className="text-emerald-300 font-sans italic">
                {liveTranscript || "Listening... Speak your answer now."}
              </span>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

