import React, { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff, Mic, MicOff, User, AlertCircle, RefreshCw } from 'lucide-react';

export const VideoPreview = ({
  cameraActive = true,
  micActive = true,
  candidateName = "Candidate",
  className = "",
  showControlsOverlay = false,
  onToggleCamera,
  onToggleMic,
  videoRef: externalVideoRef = null,
  stream: externalStream = null
}) => {
  const internalVideoRef = useRef(null);
  const videoRef = externalVideoRef || internalVideoRef;
  const [stream, setStream] = useState(null);
  const [hasPermission, setHasPermission] = useState(null);
  const [isInitializing, setIsInitializing] = useState(true);

  // Request actual camera feed or handle graceful rejection
  useEffect(() => {
    let currentStream = null;

    const startMedia = async () => {
      setIsInitializing(true);
      try {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          const mediaStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
          });
          currentStream = mediaStream;
          setStream(mediaStream);
          setHasPermission(true);
          if (videoRef.current) {
            videoRef.current.srcObject = mediaStream;
          }
        } else {
          setHasPermission(false);
        }
      } catch (err) {
        console.warn("Camera/Mic access denied or unavailable in this environment:", err.message);
        setHasPermission(false);
      } finally {
        setIsInitializing(false);
      }
    };

    startMedia();

    return () => {
      if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Sync mute/unmute with tracks
  useEffect(() => {
    if (stream) {
      stream.getVideoTracks().forEach(track => {
        track.enabled = cameraActive;
      });
      stream.getAudioTracks().forEach(track => {
        track.enabled = micActive;
      });
    }
  }, [cameraActive, micActive, stream]);

  return (
    <div className={`relative bg-navy-950 border border-slate-700/80 rounded-3xl overflow-hidden flex items-center justify-center ${className}`}>
      {/* Live Video Feed */}
      {hasPermission && cameraActive ? (
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover transform -scale-x-100"
        />
      ) : (
        /* Fallback Elegant Applicant Visualizer */
        <div className="flex flex-col items-center justify-center text-center p-8 bg-gradient-to-b from-navy-900 to-navy-950 w-full h-full">
          <div className="relative mb-4">
            <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-full bg-gradient-to-tr from-coral to-amber-500 p-1 flex items-center justify-center shadow-xl">
              <div className="w-full h-full rounded-full bg-navy-900 flex items-center justify-center">
                <User className="w-12 h-12 text-slate-300" />
              </div>
            </div>
            {!cameraActive && (
              <span className="absolute bottom-0 right-0 p-1.5 bg-rose-500 text-white rounded-full border-2 border-navy-900">
                <CameraOff className="w-4 h-4" />
              </span>
            )}
          </div>
          <h4 className="text-base font-semibold text-white">{candidateName}</h4>
          <p className="text-xs text-slate-400 mt-1 max-w-xs">
            {!hasPermission 
              ? "Virtual camera feed active (Simulator mode enabled)"
              : "Camera is temporarily turned off"}
          </p>
        </div>
      )}

      {/* Top Floating Status Tags */}
      <div className="absolute top-4 left-4 flex items-center gap-2 z-20">
        <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-navy-900/80 backdrop-blur-md border border-white/10 text-xs font-mono text-white">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>{candidateName}</span>
        </div>
      </div>

      <div className="absolute top-4 right-4 flex items-center gap-2 z-20">
        <span className={`p-1.5 rounded-lg backdrop-blur-md border ${
          micActive ? 'bg-navy-900/80 border-white/10 text-emerald-400' : 'bg-rose-500/80 border-rose-400 text-white'
        }`}>
          {micActive ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
        </span>
        <span className={`p-1.5 rounded-lg backdrop-blur-md border ${
          cameraActive ? 'bg-navy-900/80 border-white/10 text-emerald-400' : 'bg-rose-500/80 border-rose-400 text-white'
        }`}>
          {cameraActive ? <Camera className="w-4 h-4" /> : <CameraOff className="w-4 h-4" />}
        </span>
      </div>

      {/* Floating Controls Overlay if requested */}
      {showControlsOverlay && (
        <div className="absolute bottom-4 inset-x-0 flex items-center justify-center gap-3 z-20">
          <button
            onClick={onToggleMic}
            className={`p-3 rounded-2xl border transition-all ${
              micActive
                ? 'bg-navy-800/90 text-white border-white/10 hover:bg-navy-700'
                : 'bg-rose-500 text-white border-rose-400'
            }`}
          >
            {micActive ? <Mic className="w-5 h-5" /> : <MicOff className="w-5 h-5" />}
          </button>
          <button
            onClick={onToggleCamera}
            className={`p-3 rounded-2xl border transition-all ${
              cameraActive
                ? 'bg-navy-800/90 text-white border-white/10 hover:bg-navy-700'
                : 'bg-rose-500 text-white border-rose-400'
            }`}
          >
            {cameraActive ? <Camera className="w-5 h-5" /> : <CameraOff className="w-5 h-5" />}
          </button>
        </div>
      )}
    </div>
  );
};
