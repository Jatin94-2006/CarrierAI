import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Sparkles, Brain, Cpu } from 'lucide-react';
import { AIOrb } from '../components/common/AIOrb';

export const InterviewProcessing = ({ navigate, onProcessingComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [progress, setProgress] = useState(14);
  const [stepText, setStepText] = useState('Interview completed');

  const timelineSteps = [
    { id: 1, text: "Interview completed" },
    { id: 2, text: "Transcribing responses" },
    { id: 3, text: "Evaluating technical answers" },
    { id: 4, text: "Analyzing communication" },
    { id: 5, text: "Evaluating confidence" },
    { id: 6, text: "Calculating final score" },
    { id: 7, text: "Generating final report" }
  ];

  useEffect(() => {
    let isMounted = true;
    let stepIndex = 0;

    const interval = setInterval(() => {
      if (!isMounted) return;
      stepIndex += 1;
      if (stepIndex < timelineSteps.length) {
        setCurrentStep(stepIndex + 1);
        setProgress(Math.round(((stepIndex + 1) / timelineSteps.length) * 100));
        setStepText(timelineSteps[stepIndex].text);
      } else {
        clearInterval(interval);
        setTimeout(() => {
          if (onProcessingComplete) onProcessingComplete();
          navigate('report');
        }, 700);
      }
    }, 600);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [navigate, onProcessingComplete]);

  return (
    <div className="min-h-screen bg-navy-950 text-white flex flex-col items-center justify-center p-6 relative overflow-hidden bg-grid-pattern">
      {/* Background glow orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-coral/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-xl bg-navy-900/90 backdrop-blur-xl border border-slate-700/80 rounded-3xl p-8 sm:p-10 shadow-2xl text-center space-y-6 relative z-10"
      >
        <div className="flex justify-center mb-2">
          <AIOrb size="md" speaking={true} />
        </div>

        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-coral/10 border border-coral/25 text-coral text-xs font-mono font-medium mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>NEURAL EVALUATION AGENT</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-serif font-bold text-white tracking-tight">
            Analyzing Your Interview
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-md mx-auto">
            Our AI is reviewing your technical answers, communication, confidence and problem-solving approach.
          </p>
        </div>

        {/* Progress Bar */}
        <div className="space-y-1.5 text-left">
          <div className="flex justify-between text-xs font-mono font-medium">
            <span className="text-slate-400 truncate pr-2">{stepText}</span>
            <span className="text-coral">{progress}%</span>
          </div>
          <div className="w-full bg-navy-950 h-3 rounded-full overflow-hidden border border-white/5">
            <motion.div
              animate={{ width: `${progress}%` }}
              transition={{ ease: "easeOut", duration: 0.4 }}
              className="h-full bg-gradient-to-r from-coral via-amber-400 to-coral rounded-full"
            />
          </div>
        </div>

        {/* Live Timeline List */}
        <div className="space-y-3 text-left text-xs bg-navy-950/70 p-5 rounded-2xl border border-white/5">
          {timelineSteps.map((step) => {
            const isDone = currentStep > step.id;
            const isCurrent = currentStep === step.id;
            return (
              <div key={step.id} className="flex items-center gap-3">
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                ) : isCurrent ? (
                  <span className="w-4 h-4 rounded-full border-2 border-coral border-t-transparent animate-spin shrink-0" />
                ) : (
                  <span className="w-4 h-4 rounded-full border border-slate-700 shrink-0" />
                )}
                <span className={`${isDone ? 'text-slate-300' : isCurrent ? 'text-coral font-semibold' : 'text-slate-500'}`}>
                  {step.text}
                </span>
              </div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
};
