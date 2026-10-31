import React, { useState } from 'react';
import { Check, Edit3, Sparkles, Eye, Loader2 } from 'lucide-react';

export const TranscriptReview = ({
  initialTranscript = "",
  durationSec = 0,
  behavioralAnalysis = null,
  isSaving = false,
  onConfirm
}) => {
  const [transcript, setTranscript] = useState(initialTranscript);

  const eyePct = behavioralAnalysis?.eye_contact_score
    ? Math.round(
        behavioralAnalysis.eye_contact_score > 1
          ? behavioralAnalysis.eye_contact_score
          : behavioralAnalysis.eye_contact_score * 100
      )
    : 85;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-in fade-in duration-200">
      <div className="bg-[#202124] border border-[#3c4043] rounded-2xl w-full max-w-2xl p-6 shadow-2xl flex flex-col space-y-5">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#3c4043] pb-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center border border-blue-500/20">
              <Edit3 className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">Review Your Answer</h2>
              <p className="text-xs text-neutral-400">
                Spoken Duration: {durationSec}s · You can edit any transcription typos before confirming
              </p>
            </div>
          </div>
        </div>

        {/* Behavioral Observations Card */}
        {behavioralAnalysis && (
          <div className="bg-[#28292c] border border-[#3c4043] rounded-xl p-3.5 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-neutral-300 flex items-center space-x-1.5">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                <span>Behavioral & Demeanor Observations</span>
              </span>
              <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 font-medium border border-emerald-500/20">
                Confidence: {(behavioralAnalysis.confidence_level || "HIGH").toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs text-neutral-400 pt-1">
              <div>
                Primary Expression:{" "}
                <span className="text-neutral-200 font-medium capitalize">
                  {behavioralAnalysis.primary_expression || "Focused"}
                </span>
              </div>
              <div>
                Eye Contact Score:{" "}
                <span className="text-neutral-200 font-medium">
                  {eyePct}% Steady
                </span>
              </div>
            </div>

            {behavioralAnalysis.observations && (
              <p className="text-xs text-neutral-300 italic pt-1.5 border-t border-[#3c4043]/60">
                "{behavioralAnalysis.observations}"
              </p>
            )}
          </div>
        )}

        {/* Editable Transcript Area */}
        <div className="space-y-1.5">
          <label className="text-xs font-medium text-neutral-400">
            Transcribed Answer (Editable):
          </label>
          <textarea
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            rows={5}
            className="w-full bg-[#171719] border border-[#3c4043] rounded-xl p-3.5 text-sm text-neutral-100 focus:outline-none focus:border-blue-500 transition-colors resize-none leading-relaxed"
            placeholder="Type your answer transcript here..."
          />
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end space-x-3 pt-2">
          <button
            onClick={() => onConfirm(transcript)}
            disabled={isSaving}
            className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-medium text-xs sm:text-sm flex items-center space-x-2 transition-all shadow-md"
          >
            {isSaving ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Saving Answer...</span>
              </>
            ) : (
              <>
                <Check className="w-4 h-4" />
                <span>Confirm & Next Question</span>
              </>
            )}
          </button>
        </div>

      </div>
    </div>
  );
};

