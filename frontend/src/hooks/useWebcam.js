import { useState, useEffect, useRef, useCallback } from 'react';

export function useWebcam() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);
  const [isCameraOn, setIsCameraOn] = useState(true);
  const [isMicOn, setIsMicOn] = useState(true);
  const [hasPermission, setHasPermission] = useState(false);
  const [permissionError, setPermissionError] = useState(null);

  const startStream = useCallback(async () => {
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 1280 }, height: { ideal: 720 }, facingMode: 'user' },
          audio: true,
        });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
        setHasPermission(true);
        setPermissionError(null);
        return stream;
      }
    } catch (err) {
      console.warn("Camera/Mic access error in useWebcam:", err);
      setPermissionError(err.message || "Failed to access camera and microphone.");
      setHasPermission(false);
    }
    return null;
  }, []);

  const stopStream = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  }, []);

  const toggleCamera = useCallback(() => {
    if (streamRef.current) {
      const videoTrack = streamRef.current.getVideoTracks()[0];
      if (videoTrack) {
        videoTrack.enabled = !videoTrack.enabled;
        setIsCameraOn(videoTrack.enabled);
      }
    }
  }, []);

  const toggleMic = useCallback(() => {
    if (streamRef.current) {
      const audioTrack = streamRef.current.getAudioTracks()[0];
      if (audioTrack) {
        audioTrack.enabled = !audioTrack.enabled;
        setIsMicOn(audioTrack.enabled);
      }
    }
  }, []);

  const captureFrame = useCallback(() => {
    return new Promise((resolve) => {
      const video = videoRef.current;
      if (!video || !isCameraOn || video.readyState < 2) {
        return resolve(null);
      }

      try {
        const canvas = document.createElement("canvas");
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;
        const ctx = canvas.getContext("2d");
        if (!ctx) return resolve(null);

        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        canvas.toBlob((blob) => resolve(blob), "image/jpeg", 0.75);
      } catch (e) {
        resolve(null);
      }
    });
  }, [isCameraOn]);

  useEffect(() => {
    startStream();
    return () => {
      stopStream();
    };
  }, [startStream, stopStream]);

  return {
    videoRef,
    streamRef,
    isCameraOn,
    isMicOn,
    hasPermission,
    permissionError,
    startStream,
    stopStream,
    toggleCamera,
    toggleMic,
    captureFrame,
  };
}

