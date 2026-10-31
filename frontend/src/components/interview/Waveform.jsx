import React, { useEffect, useState } from 'react';

export const Waveform = ({ 
  isActive = false, 
  mode = 'ai', // 'ai' | 'applicant' | 'idle'
  barCount = 28,
  className = "" 
}) => {
  const [bars, setBars] = useState(Array.from({ length: barCount }, () => 20));

  useEffect(() => {
    if (!isActive) {
      setBars(Array.from({ length: barCount }, () => 15));
      return;
    }

    const interval = setInterval(() => {
      setBars(
        Array.from({ length: barCount }, (_, index) => {
          // Dynamic wave pattern
          const base = mode === 'ai' ? 35 : 25;
          const variance = mode === 'ai' ? 55 : 45;
          const wave = Math.sin((Date.now() / 200) + index * 0.4) * 20;
          const randomFactor = Math.random() * variance;
          return Math.min(Math.max(Math.round(base + wave + randomFactor), 12), 100);
        })
      );
    }, 90);

    return () => clearInterval(interval);
  }, [isActive, mode, barCount]);

  const colorClasses = {
    ai: 'bg-coral shadow-glow-coral',
    applicant: 'bg-emerald-400',
    idle: 'bg-slate-700'
  };

  return (
    <div className={`flex items-center justify-center gap-1 sm:gap-1.5 h-12 px-3 py-1 bg-navy-950/70 border border-white/5 rounded-2xl ${className}`}>
      {bars.map((height, i) => (
        <span
          key={i}
          className={`w-1 sm:w-1.5 rounded-full transition-all duration-100 ease-out ${
            colorClasses[mode] || colorClasses.ai
          }`}
          style={{
            height: `${height}%`,
            opacity: isActive ? 0.35 + (height / 100) * 0.65 : 0.25
          }}
        />
      ))}
    </div>
  );
};
