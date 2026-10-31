import React, { useState, useEffect } from 'react';
import { Mic, MicOff, VideoOff, Eye, Radio, AlertCircle } from 'lucide-react';

export const CandidateTile = ({
  videoRef,
  candidateName = "Candidate",
  isCameraOn = true,
  isMicOn = true,
  isAnswering = false,
  hasPermission = true,
  permissionError = null,
  audioLevel = 0,
  liveTranscript = ""
}) => {
  const [silenceDuration, setSilenceDuration] = useState(0);

  const initials = (candidateName || "Candidate")
    .split(" ")
    .map((n) => n[0])
    .slice(0, 2)
    .join("")
    .toUpperCase() || "YOU";

  const isSpeakingLive = isAnswering && (audioLevel > 3 || liveTranscript.length > 0);

  // Track silence warning while answering
  useEffect(() => {
    let timer = null;
    if (isAnswering && audioLevel <= 2 && !liveTranscript) {
      timer = setInterval(() => {
        setSilenceDuration((prev) => prev + 1);
      }, 1000);
    } else {
      setSilenceDuration(0);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isAnswering, audioLevel, liveTranscript]);

  return (
    <div className="relative flex-1 h-full min-h-[340px] sm:min-h-[380px] bg-[#202124] rounded-2xl border border-[#3c4043] flex flex-col items-center justify-center overflow-hidden shadow-2xl transition-all duration-300">
      {/* Live Video Feed */}
      {hasPermission && isCameraOn ? (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className={`w-full h-full object-cover transform -scale-x-100 transition-opacity duration-300 ${
            isAnswering ? "ring-2 ring-emerald-500/60" : ""
          }`}
        />
      ) : (
        /* Camera Off Fallback */
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="w-24 h-24 rounded-full bg-[#3c4043] flex items-center justify-center text-2xl font-bold text-neutral-300 shadow-inner">
            {initials}
          </div>
          <div className="flex items-center space-x-2 text-xs text-neutral-400">
            <VideoOff className="w-4 h-4" />
            <span>Camera is turned off</span>
          </div>
        </div>
      )}

      {/* Permission Error Banner if any */}
      {permissionError && (
        <div className="absolute inset-x-4 top-4 bg-rose-950/90 border border-rose-500/50 text-rose-200 text-xs p-3 rounded-lg z-20 backdrop-blur-md flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{permissionError} (Check camera & mic permissions)</span>
        </div>
      )}

      {/* Top Left: Live Demeanor / Behavioral Observation Badge */}
      <div className="absolute top-4 left-4 flex items-center space-x-2 bg-[#202124]/85 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#3c4043] text-xs z-10 shadow-md">
        <Eye className="w-3.5 h-3.5 text-emerald-400" />
        <span className="text-neutral-400">Observation:</span>
        <span className="font-semibold text-emerald-400">
          {isAnswering ? "Analyzing Composure & Eye Contact" : "Calm & Attentive"}
        </span>
      </div>

      {/* Top Right: Voice Tracking Waveform Meter */}
      {isAnswering && (
        <div className="absolute top-4 right-4 flex items-center space-x-2 bg-[#202124]/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-emerald-500/40 text-xs z-10 shadow-lg">
          <Radio className={`w-3.5 h-3.5 ${isSpeakingLive ? "text-emerald-400 animate-pulse" : "text-neutral-500"}`} />
          <span className="text-neutral-300 font-mono text-[11px]">
            {isSpeakingLive ? "VOICE ACTIVE" : "LISTENING..."}
          </span>
          <div className="flex items-center space-x-0.5 h-3">
            {[1, 2, 3, 4].map((bar) => (
              <span
                key={bar}
                className={`w-0.5 rounded-full transition-all duration-100 ${
                  audioLevel >= bar * 2.5
                    ? "bg-emerald-400 h-3"
                    : "bg-neutral-600 h-1"
                }`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Silence Alert if candidate has started answer but mic is silent */}
      {isAnswering && silenceDuration >= 6 && (
        <div className="absolute bottom-16 inset-x-6 mx-auto max-w-sm bg-amber-950/80 border border-amber-500/40 text-amber-200 text-xs px-3 py-2 rounded-xl z-20 backdrop-blur-md text-center flex items-center justify-center space-x-2 animate-bounce">
          <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
          <span>No speech detected. Speak clearly into your microphone.</span>
        </div>
      )}

      {/* Bottom left participant tag */}
      <div className="absolute bottom-4 left-4 flex items-center space-x-2 bg-[#202124]/90 backdrop-blur-md px-3 py-1.5 rounded-lg border border-[#3c4043] z-20">
        <span
          className={`w-2 h-2 rounded-full ${
            isSpeakingLive ? "bg-emerald-400 animate-pulse" : "bg-neutral-500"
          }`}
        />
        <span className="text-xs font-medium text-neutral-200">
          {candidateName} (You)
        </span>
        {isMicOn ? (
          <Mic className={`w-3.5 h-3.5 ${isSpeakingLive ? "text-emerald-400" : "text-neutral-400"}`} />
        ) : (
          <MicOff className="w-3.5 h-3.5 text-rose-400" />
        )}
      </div>
    </div>
  );
};

