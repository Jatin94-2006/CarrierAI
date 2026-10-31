import React from 'react';
import { motion } from 'framer-motion';

export const ProgressBar = ({
  value = 0,
  max = 100,
  label = '',
  sublabel = '',
  color = 'coral', // coral | emerald | amber | rose | blue
  showPercentage = true,
  height = 'h-2.5',
  className = ''
}) => {
  const percentage = Math.min(Math.max(Math.round((value / max) * 100), 0), 100);

  const colorGradients = {
    coral: 'from-coral to-rose-400',
    emerald: 'from-emerald-400 to-teal-500',
    amber: 'from-amber-400 to-orange-500',
    rose: 'from-rose-500 to-pink-500',
    blue: 'from-sky-400 to-indigo-500'
  };

  return (
    <div className={`w-full ${className}`}>
      {(label || showPercentage) && (
        <div className="flex justify-between items-center text-xs font-medium mb-1.5">
          <span className="text-slate-300 flex items-center gap-1.5">
            {label}
            {sublabel && <span className="text-slate-500 text-[11px]">({sublabel})</span>}
          </span>
          {showPercentage && (
            <span className="text-slate-200 font-mono font-semibold">{percentage}%</span>
          )}
        </div>
      )}
      <div className={`w-full bg-navy-950/70 border border-white/5 rounded-full overflow-hidden ${height}`}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 1.2, ease: "easeOut" }}
          className={`h-full rounded-full bg-gradient-to-r ${colorGradients[color] || colorGradients.coral}`}
        />
      </div>
    </div>
  );
};

export const ScoreRing = ({
  score = 78,
  maxScore = 100,
  size = 140,
  strokeWidth = 10,
  color = '#ff806b',
  label = "Score",
  sublabel = "",
  className = ""
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const progress = (score / maxScore) * circumference;
  const dashoffset = circumference - progress;

  return (
    <div className={`relative flex items-center justify-center ${className}`} style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="#102235"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Animated Progress ring */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: dashoffset }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          strokeLinecap="round"
          fill="transparent"
        />
      </svg>
      {/* Inner Score text */}
      <div className="absolute flex flex-col items-center justify-center text-center">
        <motion.span
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-2xl sm:text-3xl font-bold font-mono tracking-tight text-white"
        >
          {score}
          <span className="text-xs text-slate-400 font-sans font-normal ml-0.5">/{maxScore}</span>
        </motion.span>
        {label && <span className="text-[10px] uppercase tracking-wider text-slate-400 font-medium">{label}</span>}
        {sublabel && <span className="text-[9px] text-coral font-medium">{sublabel}</span>}
      </div>
    </div>
  );
};

export const AIOrb = ({ size = "lg", pulsing = true, speaking = false }) => {
  const sizeMap = {
    sm: "w-20 h-20",
    md: "w-36 h-36",
    lg: "w-48 h-48",
    xl: "w-64 h-64"
  };

  return (
    <div className={`relative flex items-center justify-center ${sizeMap[size] || sizeMap.lg}`}>
      {/* Outer Glow Halo */}
      <div
        className={`absolute inset-0 rounded-full blur-2xl transition-all duration-700 ${
          speaking
            ? 'bg-gradient-to-r from-coral/60 via-purple-500/40 to-sky-400/60 scale-125 animate-pulse'
            : 'bg-gradient-to-r from-coral/30 to-sky-500/30'
        }`}
      />

      {/* Rotating orbit rings */}
      <div className="absolute inset-1 rounded-full border border-coral/30 border-dashed animate-spin-cw" />
      <div className="absolute inset-4 rounded-full border border-sky-400/20 animate-spin-ccw" />

      {/* Core Orb */}
      <motion.div
        animate={
          speaking
            ? { scale: [1, 1.12, 0.96, 1.08, 1], rotate: [0, 90, 180, 270, 360] }
            : pulsing
            ? { scale: [1, 1.05, 1] }
            : {}
        }
        transition={{
          repeat: Infinity,
          duration: speaking ? 3 : 5,
          ease: "easeInOut"
        }}
        className="relative z-10 w-full h-full rounded-full bg-gradient-to-tr from-navy-900 via-coral/80 to-amber-300 p-1 shadow-2xl flex items-center justify-center overflow-hidden"
      >
        <div className="w-full h-full rounded-full bg-navy-900/90 backdrop-blur-md flex items-center justify-center">
          <div className="relative flex items-center justify-center">
            {/* Inner dynamic core */}
            <div className={`rounded-full filter blur-[2px] transition-all duration-500 ${
              speaking ? 'w-16 h-16 bg-coral animate-ping opacity-60' : 'w-10 h-10 bg-coral/40'
            }`} />
            <span className="absolute text-coral text-lg font-mono font-bold tracking-widest">
              AI
            </span>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
