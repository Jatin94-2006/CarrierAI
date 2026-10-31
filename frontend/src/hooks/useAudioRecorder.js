import { useState, useRef, useCallback, useEffect } from 'react';

export function useAudioRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [duration, setDuration] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [liveTranscript, setLiveTranscript] = useState('');

  const isRecordingRef = useRef(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const speechRecognitionRef = useRef(null);
  const finalTranscriptRef = useRef('');
  const activeStreamRef = useRef(null);

  useEffect(() => {
    return () => {
      isRecordingRef.current = false;
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close().catch(() => {});
      }
      if (speechRecognitionRef.current) {
        try { speechRecognitionRef.current.stop(); } catch (_) {}
      }
      if (activeStreamRef.current) {
        try { activeStreamRef.current.getTracks().forEach((track) => track.stop()); } catch (_) {}
      }
    };
  }, []);

  const startRecording = useCallback(async (existingStream) => {
    try {
      isRecordingRef.current = true;
      audioChunksRef.current = [];
      finalTranscriptRef.current = '';
      setLiveTranscript('');
      setDuration(0);

      let stream;
      if (existingStream && existingStream.getAudioTracks().length > 0) {
        stream = new MediaStream(existingStream.getAudioTracks());
      } else {
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
          });
        } catch (e) {
          stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        }
      }
      activeStreamRef.current = stream;

      // Audio analysis for volume/waveform
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (AudioCtx) {
          const audioCtx = new AudioCtx();
          if (audioCtx.state === 'suspended') {
            await audioCtx.resume();
          }
          audioContextRef.current = audioCtx;
          const source = audioCtx.createMediaStreamSource(stream);
          const analyser = audioCtx.createAnalyser();
          analyser.fftSize = 64;
          source.connect(analyser);
          analyserRef.current = analyser;

          const dataArray = new Uint8Array(analyser.frequencyBinCount);
          const updateAudioLevel = () => {
            if (!isRecordingRef.current) return;
            analyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
              sum += dataArray[i];
            }
            const avg = sum / dataArray.length;
            setAudioLevel(Math.min(100, Math.round((avg / 255) * 100)));
            animationFrameRef.current = requestAnimationFrame(updateAudioLevel);
          };
          updateAudioLevel();
        }
      } catch (err) {
        console.warn("AudioContext setup failed:", err);
      }

      // MediaRecorder setup
      let mimeType = 'audio/webm';
      if (!MediaRecorder.isTypeSupported('audio/webm')) {
        if (MediaRecorder.isTypeSupported('audio/mp4')) mimeType = 'audio/mp4';
        else if (MediaRecorder.isTypeSupported('audio/ogg')) mimeType = 'audio/ogg';
        else mimeType = '';
      }

      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.start(250);
      setIsRecording(true);

      // Duration counter
      const startTime = Date.now();
      timerIntervalRef.current = setInterval(() => {
        setDuration(Math.floor((Date.now() - startTime) / 1000));
      }, 500);

      // SpeechRecognition for live candidate transcription
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (SpeechRecognition) {
        try {
          const recognition = new SpeechRecognition();
          recognition.continuous = true;
          recognition.interimResults = true;
          recognition.lang = 'en-US';

          recognition.onresult = (event) => {
            let interim = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
              if (event.results[i].isFinal) {
                finalTranscriptRef.current += event.results[i][0].transcript + ' ';
              } else {
                interim += event.results[i][0].transcript;
              }
            }
            setLiveTranscript((finalTranscriptRef.current + interim).trim());
          };

          recognition.onerror = (e) => {
            console.warn("Speech recognition warning:", e.error);
          };

          recognition.start();
          speechRecognitionRef.current = recognition;
        } catch (recErr) {
          console.warn("SpeechRecognition init failed:", recErr);
        }
      }
    } catch (err) {
      console.error("Failed to start audio recording:", err);
      setIsRecording(false);
    }
  }, []);

  const stopRecording = useCallback(() => {
    return new Promise((resolve) => {
      isRecordingRef.current = false;
      setIsRecording(false);
      setAudioLevel(0);

      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);

      if (speechRecognitionRef.current) {
        try { speechRecognitionRef.current.stop(); } catch (_) {}
      }

      const recorder = mediaRecorderRef.current;
      if (!recorder || recorder.state === 'inactive') {
        const fallbackBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        return resolve({
          audioBlob: fallbackBlob,
          transcript: finalTranscriptRef.current.trim(),
          duration
        });
      }

      recorder.onstop = () => {
        const mimeType = recorder.mimeType || 'audio/webm';
        const finalBlob = new Blob(audioChunksRef.current, { type: mimeType });
        resolve({
          audioBlob: finalBlob,
          transcript: finalTranscriptRef.current.trim() || liveTranscript.trim(),
          duration
        });
      };

      try {
        recorder.stop();
      } catch (err) {
        const fallbackBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        resolve({
          audioBlob: fallbackBlob,
          transcript: finalTranscriptRef.current.trim(),
          duration
        });
      }
    });
  }, [duration, liveTranscript]);

  return {
    isRecording,
    duration,
    audioLevel,
    liveTranscript,
    startRecording,
    stopRecording
  };
}

