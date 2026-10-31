import React, { useState } from 'react';
import { 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  Radar 
} from 'recharts';
import { BarChart3, Radar as RadarIcon } from 'lucide-react';

export const SkillGapChart = ({ skillsData }) => {
  const [chartType, setChartType] = useState('bar'); // 'bar' | 'radar'

  // Flatten skills data for chart
  const formattedData = [
    ...(skillsData?.strongSkills || []).map(s => ({ name: s.name, yourLevel: s.level, required: s.required, gap: 0 })),
    ...(skillsData?.needsImprovement || []).map(s => ({ name: s.name, yourLevel: s.level, required: s.required, gap: s.gap })),
    ...(skillsData?.missingSkills || []).map(s => ({ name: s.name, yourLevel: s.level, required: s.required, gap: s.gap }))
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-navy-900 border border-slate-700 p-3 rounded-xl shadow-2xl text-xs space-y-1">
          <p className="font-semibold text-white mb-1.5">{label}</p>
          <p className="text-emerald-400">Your Level: <span className="font-mono font-bold">{payload[0]?.value}%</span></p>
          <p className="text-coral">Target Required: <span className="font-mono font-bold">{payload[1]?.value}%</span></p>
          {payload[1]?.value > payload[0]?.value && (
            <p className="text-rose-400 font-mono text-[11px] pt-1 border-t border-white/10">
              Gap: -{payload[1]?.value - payload[0]?.value}%
            </p>
          )}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="bg-navy-800/80 backdrop-blur-md border border-white/10 rounded-2xl p-6 shadow-subtle">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <h3 className="text-base sm:text-lg font-bold text-white font-sans flex items-center gap-2">
            Skill Level vs. Role Requirement
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Direct benchmark of your verified capabilities against Nexus Innovations' Full Stack JD
          </p>
        </div>

        {/* Toggle Chart View */}
        <div className="flex items-center gap-1 bg-navy-950 p-1 rounded-xl border border-white/5 self-start sm:self-auto">
          <button
            onClick={() => setChartType('bar')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              chartType === 'bar' ? 'bg-coral text-navy-950 font-semibold shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" /> Bar View
          </button>
          <button
            onClick={() => setChartType('radar')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              chartType === 'radar' ? 'bg-coral text-navy-950 font-semibold shadow-sm' : 'text-slate-400 hover:text-white'
            }`}
          >
            <RadarIcon className="w-3.5 h-3.5" /> Radar View
          </button>
        </div>
      </div>

      <div className="w-full h-72 sm:h-80">
        {chartType === 'bar' ? (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={formattedData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
              <XAxis 
                dataKey="name" 
                tick={{ fill: '#94a3b8', fontSize: 11 }} 
                angle={-25} 
                textAnchor="end"
                interval={0}
              />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} domain={[0, 100]} />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                wrapperStyle={{ fontSize: 12, paddingTop: 15 }} 
                formatter={(value) => <span className="text-slate-300 font-medium">{value}</span>}
              />
              <Bar dataKey="yourLevel" name="Your Current Level" fill="#34d399" radius={[6, 6, 0, 0]} />
              <Bar dataKey="required" name="Job Required Benchmark" fill="#ff806b" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={formattedData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="name" tick={{ fill: '#cbd5e1', fontSize: 11 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#475569" />
              <Radar name="Your Current Level" dataKey="yourLevel" stroke="#34d399" fill="#34d399" fillOpacity={0.4} />
              <Radar name="Job Requirement" dataKey="required" stroke="#ff806b" fill="#ff806b" fillOpacity={0.25} />
              <Legend 
                wrapperStyle={{ fontSize: 12, paddingTop: 10 }} 
                formatter={(value) => <span className="text-slate-300 font-medium">{value}</span>}
              />
              <Tooltip content={<CustomTooltip />} />
            </RadarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
};
