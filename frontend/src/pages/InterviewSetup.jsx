import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Camera, 
  CameraOff, 
  Mic, 
  MicOff, 
  Settings, 
  Sparkles, 
  ArrowRight, 
  ArrowLeft, 
  CheckCircle2, 
  Clock, 
  HelpCircle, 
  Sliders, 
  ShieldCheck,
  Video
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { VideoPreview } from '../components/interview/VideoPreview';
import { Waveform } from '../components/interview/Waveform';
import { CANDIDATE_PROFILE } from '../data/mockData';

export const InterviewSetup = ({ navigate, onEnterInterview, currentUser }) => {
  const [micActive, setMicActive] = useState(true);
  const [cameraActive, setCameraActive] = useState(true);
  const [selectedDifficulty, setSelectedDifficulty] = useState('Intermediate');
  const [selectedType, setSelectedType] = useState('Technical + HR');
  const [showSettingsModal, setShowSettingsModal] = useState(false);

  const candidateName = currentUser?.name || CANDIDATE_PROFILE.name;
  const targetRole = currentUser?.role || CANDIDATE_PROFILE.role;

  const handleStart = () => {
    if (onEnterInterview) {
      onEnterInterview({
        micActive,
        cameraActive,
        difficulty: selectedDifficulty,
        type: selectedType,
        candidateName,
        role: targetRole
      });
    }
    navigate('interview-room');
  };

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto space-y-8 animate-in fade-in duration-300">
      
      {/* Top Header */}
      <div className="text-center max-w-2xl mx-auto space-y-2">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-coral/10 border border-coral/25 text-coral text-xs font-mono font-medium">
          <Video className="w-3.5 h-3.5" />
          <span>PRE-INTERVIEW CHECKROOM</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-serif font-bold text-white tracking-tight">
          Ready for your AI Interview?
        </h1>
        <p className="text-slate-400 text-xs sm:text-sm">
          Calibrate your camera and microphone. Ensure you are in a quiet, well-lit environment.
        </p>
      </div>

      {/* Main Video Preview Container (Google Meet Style) */}
      <div className="bg-navy-900 border border-slate-700/80 rounded-3xl p-4 sm:p-6 shadow-2xl relative">
        <div className="w-full h-80 sm:h-96 rounded-2xl overflow-hidden relative">
          <VideoPreview
            cameraActive={cameraActive}
            micActive={micActive}
            candidateName={candidateName}
            className="w-full h-full"
          />

          {/* Floating mic test level bar at bottom right of video */}
          <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between z-30 pointer-events-none">
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-navy-900/80 backdrop-blur-md border border-white/10 text-xs text-white">
              <span className={`w-2 h-2 rounded-full ${micActive ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'}`} />
              <span>{micActive ? "Mic Testing Active" : "Microphone Muted"}</span>
            </div>

            {micActive && (
              <div className="w-28 sm:w-36 pointer-events-auto">
                <Waveform isActive={true} mode="applicant" barCount={16} className="h-8 py-0.5" />
              </div>
            )}
          </div>
        </div>

        {/* Center Control Action Bar */}
        <div className="mt-4 flex items-center justify-center gap-4">
          <button
            onClick={() => setMicActive(!micActive)}
            className={`p-3 sm:p-3.5 rounded-2xl border transition-all cursor-pointer ${
              micActive
                ? 'bg-navy-800 text-slate-200 border-white/10 hover:bg-navy-700 hover:text-white'
                : 'bg-rose-500/20 text-rose-300 border-rose-500/40 hover:bg-rose-500/30'
            }`}
            title={micActive ? "Mute Microphone" : "Unmute Microphone"}
          >
            {micActive ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5 text-rose-400" />}
          </button>

          <button
            onClick={() => setCameraActive(!cameraActive)}
            className={`p-3 sm:p-3.5 rounded-2xl border transition-all cursor-pointer ${
              cameraActive
                ? 'bg-navy-800 text-slate-200 border-white/10 hover:bg-navy-700 hover:text-white'
                : 'bg-rose-500/20 text-rose-300 border-rose-500/40 hover:bg-rose-500/30'
            }`}
            title={cameraActive ? "Turn Off Camera" : "Turn On Camera"}
          >
            {cameraActive ? <Camera className="w-5 h-5" /> : <CameraOff className="w-5 h-5 text-rose-400" />}
          </button>

          <button
            onClick={() => setShowSettingsModal(true)}
            className="p-3 sm:p-3.5 rounded-2xl bg-navy-800 text-slate-300 border border-white/10 hover:bg-navy-700 hover:text-white transition-all cursor-pointer"
            title="Audio & Video Settings"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* INTERVIEW PARAMETERS & META CARDS */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        
        <div className="p-4 rounded-2xl bg-navy-800/80 border border-white/10">
          <span className="text-[11px] text-slate-400 block mb-1">Interview Type</span>
          <span className="text-sm font-bold text-white block">{selectedType}</span>
          <span className="text-[10px] text-coral mt-1 block">{targetRole} Track</span>
        </div>

        <div className="p-4 rounded-2xl bg-navy-800/80 border border-white/10">
          <span className="text-[11px] text-slate-400 block mb-1">Difficulty</span>
          <span className="text-sm font-bold text-amber-400 block">{selectedDifficulty}</span>
          <span className="text-[10px] text-slate-400 mt-1 block">Adaptive Questions</span>
        </div>

        <div className="p-4 rounded-2xl bg-navy-800/80 border border-white/10">
          <span className="text-[11px] text-slate-400 block mb-1">Session Duration</span>
          <span className="text-sm font-bold text-white block">15 minutes</span>
          <span className="text-[10px] text-slate-400 mt-1 block">Timed pressure</span>
        </div>

        <div className="p-4 rounded-2xl bg-navy-800/80 border border-white/10">
          <span className="text-[11px] text-slate-400 block mb-1">Question Count</span>
          <span className="text-sm font-bold text-white block">10 Questions</span>
          <span className="text-[10px] text-emerald-400 mt-1 block">Detailed Scoring</span>
        </div>

      </div>

      {/* Primary Action Buttons */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
        <Button
          variant="secondary"
          size="lg"
          onClick={() => navigate('resume-analysis')}
          className="w-full sm:w-auto"
        >
          <ArrowLeft className="w-4 h-4 mr-1" /> Back to Resume Analysis
        </Button>

        <Button
          size="lg"
          onClick={handleStart}
          className="w-full sm:w-auto shadow-glow-coral text-navy-950 font-bold px-10 text-base"
        >
          Enter Interview <ArrowRight className="w-4 h-4 ml-1" />
        </Button>
      </div>

    </div>
  );
};
