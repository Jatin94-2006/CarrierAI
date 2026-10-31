import React from 'react';
import {
  Mic,
  MicOff,
  Video,
  VideoOff,
  RotateCcw,
  SkipForward,
  PhoneOff,
  Square,
  Radio,
  Loader2
} from 'lucide-react';

export const MeetBottomBar = ({
  isCameraOn = true,
  isMicOn = true,
  isSpeaking = false,
  isRecording = false,
  recordingDurationSec = 0,
  isSubmitting = false,
  onToggleCamera,
  onToggleMic,
  onStartAnswer,
  onStopAnswer,
  onSkipQuestion,
  onRepeatQuestion,
  onEndCall
}) => {
  const formatSeconds = (sec) => {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="h-20 bg-[#202124] border-t border-[#3c4043] px-4 sm:px-6 flex items-center justify-between text-white select-none shrink-0 z-20">
      
      {/* Left: Meeting status label */}
      <div className="flex items-center space-x-3 w-1/4 hidden md:flex">
        <div className="text-xs text-neutral-400">
          <p className="font-semibold text-neutral-200">Google Meet Audio Room</p>
          <p className="text-[11px] text-neutral-500">Live spoken interview</p>
        </div>
      </div>

      {/* Center: Meeting Controls */}
      <div className="flex items-center space-x-3 sm:space-x-4 mx-auto md:mx-0">
        
        {/* Mic Toggle */}
        <button
          onClick={onToggleMic}
          title={isMicOn ? "Mute microphone" : "Unmute microphone"}
          className={`w-11 h-11 rounded-full flex items-center justify-center transition-all ${
            isMicOn
              ? "bg-[#3c4043] hover:bg-[#4a4e51] text-white"
              : "bg-rose-600 hover:bg-rose-700 text-white ring-2 ring-rose-400"
          }`}
        >
          {isMicOn ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
        </button>

        {/* Camera Toggle */}
        <button
          onClick={onToggleCamera}
          title={isCameraOn ? "Turn off camera" : "Turn on camera"}
          className={`w-11 h-11 rounded-full flex items-center justify-center transition-all ${
            isCameraOn
              ? "bg-[#3c4043] hover:bg-[#4a4e51] text-white"
              : "bg-rose-600 hover:bg-rose-700 text-white ring-2 ring-rose-400"
          }`}
        >
          {isCameraOn ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
        </button>

        {/* PRIMARY CTA: Answer Question / Finish Answer */}
        {!isRecording ? (
          <button
            onClick={onStartAnswer}
            disabled={isSubmitting || isSpeaking}
            title="Start answering via microphone"
            className="px-5 h-11 rounded-full bg-emerald-600 hover:bg-emerald-500 disabled:opacity-40 text-white font-semibold text-xs sm:text-sm flex items-center space-x-2 shadow-lg shadow-emerald-950 transition-all hover:scale-105 active:scale-95"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Processing...</span>
              </>
            ) : (
              <>
                <Radio className="w-4 h-4" />
                <span>Start Voice Answer</span>
              </>
            )}
          </button>
        ) : (
          <button
            onClick={onStopAnswer}
            disabled={isSubmitting}
            title="Finish speaking and submit answer"
            className="px-5 h-11 rounded-full bg-rose-600 hover:bg-rose-500 text-white font-semibold text-xs sm:text-sm flex items-center space-x-2.5 shadow-lg shadow-rose-950 animate-pulse transition-all hover:scale-105 active:scale-95"
          >
            <Square className="w-4 h-4 fill-current" />
            <span>Finish Answer ({formatSeconds(recordingDurationSec)})</span>
          </button>
        )}

        {/* Repeat Question */}
        <button
          onClick={onRepeatQuestion}
          disabled={isRecording || isSpeaking}
          title="Repeat question audio"
          className="w-11 h-11 rounded-full bg-[#3c4043] hover:bg-[#4a4e51] disabled:opacity-40 text-white flex items-center justify-center transition-all"
        >
          <RotateCcw className="w-4 h-4" />
        </button>

        {/* Skip Question */}
        <button
          onClick={onSkipQuestion}
          disabled={isRecording || isSubmitting}
          title="Skip this question"
          className="w-11 h-11 rounded-full bg-[#3c4043] hover:bg-[#4a4e51] disabled:opacity-40 text-white flex items-center justify-center transition-all"
        >
          <SkipForward className="w-4 h-4" />
        </button>

      </div>

      {/* Right: End Call Hang-Up */}
      <div className="flex items-center justify-end space-x-3 w-1/4">
        <button
          onClick={onEndCall}
          title="Leave interview and generate final report"
          className="w-12 h-11 rounded-full bg-rose-600 hover:bg-rose-700 text-white flex items-center justify-center shadow-lg transition-all hover:scale-105"
        >
          <PhoneOff className="w-5 h-5" />
        </button>
      </div>

    </div>
  );
};

