import React from 'react';

export const Footer = ({ navigate }) => {
  return (
    <footer className="w-full bg-navy-950 border-t border-white/5 py-10 px-4 sm:px-6 lg:px-8 text-slate-400 text-xs">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
        
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-coral/20 border border-coral/40 flex items-center justify-center">
            <div className="w-2.5 h-2.5 bg-coral rounded-sm rotate-45" />
          </div>
          <div>
            <span className="font-serif font-bold text-sm text-white">
              Career<span className="text-coral">AI</span>
            </span>
            <p className="text-[11px] text-slate-500">From Resume to Job-Ready.</p>
          </div>
        </div>

        {/* Links */}
        <div className="flex flex-wrap items-center justify-center gap-6 text-[11px]">
          <button onClick={() => navigate?.('landing')} className="hover:text-coral transition-colors">Overview</button>
          <button onClick={() => navigate?.('resume-upload')} className="hover:text-coral transition-colors">Resume Analysis</button>
          <button onClick={() => navigate?.('gap-analysis')} className="hover:text-coral transition-colors">Skill Gap Engine</button>
          <button onClick={() => navigate?.('interview-setup')} className="hover:text-coral transition-colors">AI Mock Interview</button>
          <button onClick={() => navigate?.('roadmap')} className="hover:text-coral transition-colors">30-Day Roadmap</button>
        </div>

        {/* Copyright */}
        <div className="text-center md:text-right text-[11px] text-slate-500">
          <p>© 2026 CareerAI. All rights reserved.</p>
          <p className="text-[10px] text-slate-600 mt-0.5">Built with React, Vite & Tailwind CSS</p>
        </div>

      </div>
    </footer>
  );
};
