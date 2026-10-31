import React, { useEffect, useState } from 'react';
import { 
  Mic, 
  MicOff, 
  Camera, 
  CameraOff, 
  MessageSquare, 
  Settings, 
  PhoneOff, 
  Clock, 
  Volume2,
  ChevronRight,
  Shield,
  Bot,
  User
} from 'lucide-react';

export const InterviewTimer = ({ initialMinutes = 15, onTimeExpired }) => {
  const [secondsLeft, setSecondsLeft] = useState(initialMinutes * 60);

  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          if (onTimeExpired) onTimeExpired();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [onTimeExpired]);

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-navy-950/80 border border-white/10 font-mono text-xs text-white shadow-inner">
      <Clock className="w-3.5 h-3.5 text-coral animate-pulse" />
      <span>
        {String(minutes).padStart(2, '0')}:{String(seconds).padStart(2, '0')}
      </span>
    </div>
  );
};

export const InterviewControls = ({
  micActive = true,
  cameraActive = true,
  transcriptOpen = true,
  onToggleMic,
  onToggleCamera,
  onToggleTranscript,
  onOpenSettings,
  onEndInterview,
  isSubmitting = false
}) => {
  return (
    <div className="flex items-center justify-center gap-3 sm:gap-4 p-3 bg-navy-900/90 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl max-w-xl mx-auto">
      {/* Microphone */}
      <button
        onClick={onToggleMic}
        className={`p-3 sm:p-3.5 rounded-xl border transition-all cursor-pointer ${
          micActive
            ? 'bg-navy-800 text-slate-200 border-white/10 hover:bg-navy-700 hover:text-white'
            : 'bg-rose-500/20 text-rose-300 border-rose-500/40 hover:bg-rose-500/30'
        }`}
        title={micActive ? "Mute Microphone" : "Unmute Microphone"}
      >
        {micActive ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5 text-rose-400" />}
      </button>

      {/* Camera */}
      <button
        onClick={onToggleCamera}
        className={`p-3 sm:p-3.5 rounded-xl border transition-all cursor-pointer ${
          cameraActive
            ? 'bg-navy-800 text-slate-200 border-white/10 hover:bg-navy-700 hover:text-white'
            : 'bg-rose-500/20 text-rose-300 border-rose-500/40 hover:bg-rose-500/30'
        }`}
        title={cameraActive ? "Turn Off Camera" : "Turn On Camera"}
      >
        {cameraActive ? <Camera className="w-5 h-5" /> : <CameraOff className="w-5 h-5 text-rose-400" />}
      </button>

      {/* Live Transcript Drawer Toggle */}
      <button
        onClick={onToggleTranscript}
        className={`p-3 sm:p-3.5 rounded-xl border transition-all cursor-pointer ${
          transcriptOpen
            ? 'bg-coral text-navy-950 border-coral font-semibold shadow-glow-coral'
            : 'bg-navy-800 text-slate-200 border-white/10 hover:bg-navy-700 hover:text-white'
        }`}
        title="Toggle Real-Time Transcript"
      >
        <MessageSquare className="w-5 h-5" />
      </button>

      {/* Settings */}
      <button
        onClick={onOpenSettings}
        className="p-3 sm:p-3.5 rounded-xl bg-navy-800 text-slate-300 border border-white/10 hover:bg-navy-700 hover:text-white transition-all cursor-pointer"
        title="Audio & Video Settings"
      >
        <Settings className="w-5 h-5" />
      </button>

      {/* Red Leave / End Interview Button */}
      <button
        onClick={onEndInterview}
        disabled={isSubmitting}
        className="flex items-center gap-2 px-5 py-3 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs sm:text-sm shadow-lg shadow-rose-950 transition-all cursor-pointer disabled:opacity-50"
      >
        <PhoneOff className="w-4 h-4" />
        <span>End Interview</span>
      </button>
    </div>
  );
};

export const TranscriptPanel = ({
  transcripts = [],
  currentQuestionIndex = 0,
  totalQuestions = 5,
  isAiSpeaking = false,
  isApplicantSpeaking = false
}) => {
  return (
    <div className="bg-navy-800/90 backdrop-blur-md border border-slate-700/60 rounded-3xl p-5 flex flex-col h-full shadow-2xl">
      <div className="flex items-center justify-between pb-3 border-b border-white/10 mb-4">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-coral" />
          <h3 className="text-sm font-bold text-white">Live AI Transcript</h3>
        </div>
        <span className="text-[11px] font-mono text-slate-400">
          Question {currentQuestionIndex + 1} of {totalQuestions}
        </span>
      </div>

      {/* Real-time speech stream */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 text-xs">
        {transcripts.map((entry, idx) => (
          <div
            key={idx}
            className={`p-3 rounded-2xl ${
              entry.speaker === 'AI'
                ? 'bg-navy-950/70 border border-coral/20 text-slate-200'
                : 'bg-coral/10 border border-coral/30 text-white'
            }`}
          >
            <div className="flex items-center justify-between mb-1 text-[10px] font-mono">
              <span className={`font-semibold flex items-center gap-1.5 ${entry.speaker === 'AI' ? 'text-coral' : 'text-emerald-400'}`}>
                {entry.speaker === 'AI' ? (
                  <>
                    <Bot className="w-3.5 h-3.5" />
                    <span>Aria (AI Interviewer)</span>
                  </>
                ) : (
                  <>
                    <User className="w-3.5 h-3.5" />
                    <span>Krish Sharma (Applicant)</span>
                  </>
                )}
              </span>
              <span className="text-slate-500">{entry.timestamp}</span>
            </div>
            <p className="leading-relaxed">{entry.text}</p>
            {entry.behavioral && (
              <div className="mt-2 pt-1.5 border-t border-white/10 flex items-center gap-2.5 text-[10px] text-slate-400 font-mono">
                <span>Eye Contact: <strong className="text-cyan-400">{entry.behavioral.eye_contact_score || 85}%</strong></span>
                <span>•</span>
                <span>Confidence: <strong className="text-emerald-400 capitalize">{entry.behavioral.confidence_level || "High"}</strong></span>
                <span>•</span>
                <span>State: <strong className="text-slate-300 capitalize">{entry.behavioral.primary_expression || "Focused"}</strong></span>
              </div>
            )}
          </div>
        ))}

        {/* Live speech indicators */}
        {isAiSpeaking && (
          <div className="flex items-center gap-2 p-2 rounded-xl bg-navy-950/40 text-coral text-[11px] animate-pulse">
            <span className="w-2 h-2 rounded-full bg-coral animate-ping" />
            <span>AI is speaking the question...</span>
          </div>
        )}

        {isApplicantSpeaking && (
          <div className="flex items-center gap-2 p-2 rounded-xl bg-navy-950/40 text-emerald-400 text-[11px] animate-pulse">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span>Listening to your answer response...</span>
          </div>
        )}
      </div>
    </div>
  );
};
