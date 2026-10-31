import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2 } from 'lucide-react';

// Google Meet Interiewer UI Components
import { MeetHeader } from '../components/interview/meet/MeetHeader';
import { InterviewerTile } from '../components/interview/meet/InterviewerTile';
import { CandidateTile } from '../components/interview/meet/CandidateTile';
import { QuestionSubtitles } from '../components/interview/meet/QuestionSubtitles';
import { MeetBottomBar } from '../components/interview/meet/MeetBottomBar';
import { TranscriptReview } from '../components/interview/meet/TranscriptReview';

// Hooks & API
import { useWebcam } from '../hooks/useWebcam';
import { useAudioRecorder } from '../hooks/useAudioRecorder';
import { 
  startInterviewSession, 
  getQuestionAudioUrl, 
  submitQuestionAnswer, 
  finishInterviewSession, 
  evaluateInterviewSession 
} from '../utils/interviewApi';
import { MOCK_INTERVIEW_QUESTIONS, CANDIDATE_PROFILE } from '../data/mockData';

export const InterviewRoom = ({ navigate, onFinishInterview, sessionConfig, currentUser }) => {
  // 1. Pre-interview Countdown
  const [countdown, setCountdown] = useState(3);
  const [isCountingDown, setIsCountingDown] = useState(true);

  // 2. Interview Session State
  const initialName = sessionConfig?.candidateName || currentUser?.name || "Candidate";
  const initialRole = sessionConfig?.role || currentUser?.role || "Software Engineer";

  const [interviewId, setInterviewId] = useState(null);
  const [questions, setQuestions] = useState(MOCK_INTERVIEW_QUESTIONS);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [roleTitle, setRoleTitle] = useState(initialRole);
  const [candidateName, setCandidateName] = useState(initialName);

  // 3. Audio & Timer State
  const [isAiSpeaking, setIsAiSpeaking] = useState(false);
  const [timeRemainingSec, setTimeRemainingSec] = useState(90);
  const [isTimerActive, setIsTimerActive] = useState(false);

  // 4. Review Modal & Submission State
  const [pendingReview, setPendingReview] = useState(null);
  const [isSavingReview, setIsSavingReview] = useState(false);
  const [isSubmittingAnswer, setIsSubmittingAnswer] = useState(false);
  const [transcripts, setTranscripts] = useState([]);

  // Hardware Hooks
  const {
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
    captureFrame
  } = useWebcam();

  const {
    isRecording,
    duration: recDuration,
    audioLevel,
    liveTranscript,
    startRecording,
    stopRecording
  } = useAudioRecorder();

  // Internal audio player & timer refs
  const audioPlayerRef = useRef(new Audio());
  const lastPlayedQIdRef = useRef(null);
  const timerIntervalRef = useRef(null);
  const snapshotTimerRef = useRef(null);
  const capturedSnapshotsRef = useRef([]);

  // Initialize Interview Session with Agent 4 on mount
  useEffect(() => {
    let isMounted = true;
    async function initSession() {
      try {
        const sessionRes = await startInterviewSession(initialName, initialRole);
        if (sessionRes && sessionRes.questions && sessionRes.questions.length > 0 && isMounted) {
          const sId = sessionRes.sessionId || sessionRes.id;
          setInterviewId(sId);
          setQuestions(sessionRes.questions);
          if (sessionRes.role) setRoleTitle(sessionRes.role);
          if (sessionRes.candidateName) setCandidateName(sessionRes.candidateName);
          setTimeRemainingSec(sessionRes.questions[0].durationSeconds || sessionRes.questions[0].time_limit_sec || 90);
          console.log("[InterviewRoom] Agent 4 Google Meet session connected:", sId);
        }
      } catch (err) {
        console.warn("[InterviewRoom] Using local questions fallback:", err);
      }
    }
    initSession();

    // Start video/audio stream on load
    startStream();

    return () => {
      isMounted = false;
      stopAllAudio();
      stopStream();
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (snapshotTimerRef.current) clearInterval(snapshotTimerRef.current);
    };
  }, []);

  const currentQ = questions[currentQIndex] || questions[0] || MOCK_INTERVIEW_QUESTIONS[0];
  const totalQuestions = questions.length;

  // Stop all playing audio & speech synthesis
  const stopAllAudio = useCallback(() => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current.removeAttribute("src");
      audioPlayerRef.current.load();
      audioPlayerRef.current.onended = null;
      audioPlayerRef.current.onerror = null;
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setIsAiSpeaking(false);
  }, []);

  // Browser speech synthesis fallback
  const speakBrowserFallback = useCallback((text, onEnd) => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.lang = "en-US";
      utterance.onend = () => {
        setIsAiSpeaking(false);
        if (onEnd) onEnd();
      };
      utterance.onerror = () => {
        setIsAiSpeaking(false);
        if (onEnd) onEnd();
      };
      setIsAiSpeaking(true);
      window.speechSynthesis.speak(utterance);
    } else {
      setIsAiSpeaking(false);
      if (onEnd) onEnd();
    }
  }, []);

  // Play question audio (Single-instance Edge-TTS playback)
  const playQuestionAudio = useCallback((q) => {
    if (!q) return;
    const targetQ = q;

    stopAllAudio();
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    setIsTimerActive(false);

    const limitSec = targetQ.durationSeconds || targetQ.time_limit_sec || 90;
    setTimeRemainingSec(limitSec);

    const qId = targetQ.id || targetQ.q_id || 1;
    const textToSpeak = targetQ.aiSpeech || targetQ.question || "";

    const startCountdown = () => {
      setIsAiSpeaking(false);
      setIsTimerActive(true);
    };

    if (interviewId) {
      const audioUrl = getQuestionAudioUrl(interviewId, qId);
      const audio = new Audio(audioUrl);
      audioPlayerRef.current = audio;
      setIsAiSpeaking(true);

      audio.onended = () => {
        startCountdown();
      };

      audio.onerror = () => {
        speakBrowserFallback(textToSpeak, startCountdown);
      };

      audio.play().catch((err) => {
        if (err?.name === "AbortError") return;
        speakBrowserFallback(textToSpeak, startCountdown);
      });
    } else {
      speakBrowserFallback(textToSpeak, startCountdown);
    }
  }, [interviewId, speakBrowserFallback, stopAllAudio]);

  // Pre-interview Countdown Effect
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else {
      setIsCountingDown(false);
      // Play first question
      if (questions.length > 0) {
        lastPlayedQIdRef.current = questions[0].id || questions[0].q_id || 1;
        playQuestionAudio(questions[0]);
      }
    }
  }, [countdown, playQuestionAudio, questions]);

  // Play audio when question index changes (after countdown)
  useEffect(() => {
    if (isCountingDown || pendingReview) return;
    const qId = currentQ?.id || currentQ?.q_id;
    if (qId && lastPlayedQIdRef.current !== qId) {
      lastPlayedQIdRef.current = qId;
      playQuestionAudio(currentQ);
    }
  }, [currentQIndex, isCountingDown, pendingReview, currentQ, playQuestionAudio]);

  // Countdown Timer Interval
  useEffect(() => {
    if (isTimerActive && !isRecording && !pendingReview && !isAiSpeaking) {
      timerIntervalRef.current = setInterval(() => {
        setTimeRemainingSec((prev) => {
          if (prev <= 1) {
            clearInterval(timerIntervalRef.current);
            handleSkipQuestion();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, [isTimerActive, isRecording, pendingReview, isAiSpeaking]);

  // Start Answering Voice Response
  const handleStartAnswer = async () => {
    try {
      setIsTimerActive(false);
      capturedSnapshotsRef.current = [];

      await startRecording(streamRef.current);

      // Periodically capture keyframe snapshot every 3.5s for Agent 4 behavioral tracking
      snapshotTimerRef.current = setInterval(async () => {
        try {
          const frame = await captureFrame();
          if (frame && capturedSnapshotsRef.current.length < 5) {
            capturedSnapshotsRef.current.push(frame);
          }
        } catch (_) {}
      }, 3500);
    } catch (err) {
      console.error("Failed to start voice answer:", err);
    }
  };

  // Stop Answering & Open Review Modal
  const handleStopAnswer = async () => {
    setIsSubmittingAnswer(true);

    if (snapshotTimerRef.current) {
      clearInterval(snapshotTimerRef.current);
      snapshotTimerRef.current = null;
    }

    try {
      // Final keyframe
      try {
        const finalFrame = await captureFrame();
        if (finalFrame) capturedSnapshotsRef.current.push(finalFrame);
      } catch (_) {}

      const { blob: audioBlob, durationSec, liveTranscript: recordedLiveText } = await stopRecording();

      const qId = currentQ.id || currentQ.q_id || (currentQIndex + 1);
      let submitRes = null;

      if (interviewId) {
        try {
          submitRes = await submitQuestionAnswer(
            interviewId,
            qId,
            audioBlob,
            durationSec,
            capturedSnapshotsRef.current,
            recordedLiveText
          );
        } catch (e) {
          console.warn("Submit answer error:", e);
        }
      }

      const isPlaceholder =
        !submitRes?.transcript ||
        submitRes.transcript.includes("Candidate provided spoken answer") ||
        submitRes.transcript.includes("Transcript captured from voice answer");

      const resolvedTranscript =
        !isPlaceholder && submitRes?.transcript?.trim()
          ? submitRes.transcript.trim()
          : recordedLiveText?.trim() || submitRes?.transcript || "Spoken response recorded successfully.";

      // Open review modal with transcript and behavioral observations
      setPendingReview({
        transcript: resolvedTranscript,
        durationSec: durationSec || recDuration,
        behavioralAnalysis: submitRes?.behavioral_analysis || {
          primary_expression: "focused",
          eye_contact_score: 88,
          confidence_level: "high",
          observations: "Steady vocal delivery and camera composure."
        }
      });
    } catch (err) {
      console.error("Failed to stop and process answer:", err);
    } finally {
      setIsSubmittingAnswer(false);
    }
  };

  // Confirm transcript from Review Modal & advance to next question
  const handleConfirmReview = async (confirmedTranscript) => {
    setIsSavingReview(true);
    const qId = currentQ.id || currentQ.q_id || (currentQIndex + 1);
    const duration = pendingReview?.durationSec || recDuration || 45;
    const behavioral = pendingReview?.behavioralAnalysis || null;

    const applicantEntry = {
      q_id: qId,
      speaker: 'Applicant',
      text: confirmedTranscript,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      duration: duration,
      behavioral: behavioral
    };

    const updatedTranscripts = [...transcripts, applicantEntry];
    setTranscripts(updatedTranscripts);

    setIsSavingReview(false);
    setPendingReview(null);

    // Advance to next question or complete interview
    if (currentQIndex + 1 < totalQuestions) {
      const nextIndex = currentQIndex + 1;
      setCurrentQIndex(nextIndex);
    } else {
      // Completed all questions
      await handleCompleteInterview(updatedTranscripts);
    }
  };

  // Skip Question
  const handleSkipQuestion = async () => {
    const qId = currentQ.id || currentQ.q_id || (currentQIndex + 1);
    
    // Add skipped marker entry
    const skippedEntry = {
      q_id: qId,
      speaker: 'Applicant',
      text: "(Question Skipped)",
      status: "skipped",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      duration: 0,
      behavioral: null
    };

    const updatedTranscripts = [...transcripts, skippedEntry];
    setTranscripts(updatedTranscripts);

    if (currentQIndex + 1 < totalQuestions) {
      const nextIndex = currentQIndex + 1;
      setCurrentQIndex(nextIndex);
    } else {
      await handleCompleteInterview(updatedTranscripts);
    }
  };

  // Repeat Question
  const handleRepeatQuestion = () => {
    lastPlayedQIdRef.current = null;
    playQuestionAudio(currentQ);
  };

  // End Call Early
  const handleEndCall = async () => {
    if (window.confirm("Are you sure you want to end the interview now? Completed answers will be compiled.")) {
      await handleCompleteInterview(transcripts);
    }
  };

  // Complete Interview & Trigger Agent 2 Gap Analysis
  const handleCompleteInterview = async (finalTranscriptsList) => {
    const listToSend = finalTranscriptsList || transcripts;
    stopAllAudio();

    if (interviewId) {
      try {
        await finishInterviewSession(interviewId);
      } catch (_) {}
    }

    let evaluationResult = null;
    try {
      evaluationResult = await evaluateInterviewSession(listToSend, interviewId, roleTitle);
    } catch (e) {
      console.warn("Evaluation error:", e);
    }

    if (onFinishInterview) {
      onFinishInterview(listToSend, evaluationResult);
    }

    navigate('interview-processing');
  };

  return (
    <div className="h-screen flex flex-col bg-[#202124] text-white overflow-hidden select-none relative font-sans">
      
      {/* 1. Pre-Interview Countdown Overlay */}
      <AnimatePresence>
        {isCountingDown && (
          <motion.div
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-navy-950/95 backdrop-blur-xl"
          >
            <motion.span
              key={countdown}
              initial={{ scale: 0.5, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 1.5, opacity: 0 }}
              transition={{ duration: 0.5 }}
              className="font-serif text-8xl sm:text-9xl font-bold text-coral drop-shadow-[0_0_35px_rgba(255,128,107,0.5)]"
            >
              {countdown}
            </motion.span>
            <p className="text-slate-400 text-sm mt-6 font-mono tracking-wider">
              CONNECTING TO GOOGLE MEET INTERVIEW ROOM...
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 2. Top Google Meet Header */}
      <MeetHeader
        role={roleTitle}
        currentQIndex={currentQIndex}
        totalQuestions={totalQuestions}
        phase={currentQ.phase}
        questionType={currentQ.type}
        skillTested={currentQ.skill_tested}
        difficulty={currentQ.difficulty || "medium"}
        timeRemainingSec={timeRemainingSec}
        totalLimitSec={currentQ.durationSeconds || currentQ.time_limit_sec || 90}
        onEndCall={handleEndCall}
      />

      {/* 3. Main Call Dual Participant Grid Area */}
      <main className="flex-1 p-3 sm:p-5 flex flex-col justify-between overflow-hidden min-h-0">
        <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-5 min-h-0">
          
          {/* AI Interviewer Tile */}
          <InterviewerTile
            isSpeaking={isAiSpeaking}
            questionText={currentQ.question}
            questionType={currentQ.type}
            phase={currentQ.phase}
          />

          {/* Candidate Webcam Mirror Tile */}
          <CandidateTile
            videoRef={videoRef}
            candidateName={candidateName}
            isCameraOn={isCameraOn}
            isMicOn={isMicOn}
            isAnswering={isRecording}
            hasPermission={hasPermission}
            permissionError={permissionError}
            audioLevel={audioLevel}
            liveTranscript={liveTranscript}
          />

        </div>

        {/* 4. Closed-Captions Question Subtitles Overlay */}
        <QuestionSubtitles
          question={currentQ}
          isSpeaking={isAiSpeaking}
          isRecording={isRecording}
          liveTranscript={liveTranscript}
        />
      </main>

      {/* 5. Google Meet Floating Control Bar */}
      <MeetBottomBar
        isCameraOn={isCameraOn}
        isMicOn={isMicOn}
        isSpeaking={isAiSpeaking}
        isRecording={isRecording}
        recordingDurationSec={recDuration}
        isSubmitting={isSubmittingAnswer}
        onToggleCamera={toggleCamera}
        onToggleMic={toggleMic}
        onStartAnswer={handleStartAnswer}
        onStopAnswer={handleStopAnswer}
        onSkipQuestion={handleSkipQuestion}
        onRepeatQuestion={handleRepeatQuestion}
        onEndCall={handleEndCall}
      />

      {/* 6. Transcript & Demeanor Review Modal */}
      {pendingReview && (
        <TranscriptReview
          initialTranscript={pendingReview.transcript}
          durationSec={pendingReview.durationSec}
          behavioralAnalysis={pendingReview.behavioralAnalysis}
          isSaving={isSavingReview}
          onConfirm={handleConfirmReview}
        />
      )}

    </div>
  );
};
