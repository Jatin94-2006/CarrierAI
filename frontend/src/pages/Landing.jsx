import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { Check, FileText, Target, BookOpen, Mic, Compass, Star } from 'lucide-react';

export const Landing = ({ navigate }) => {
  const resumeCardRef = useRef(null);
  const futureCardRef = useRef(null);

  // 3D Card Tilt Effect on mouse movement
  const handleCardMouseMove = (e, ref) => {
    if (!ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const rotateY = ((x / rect.width) - 0.5) * 10;
    const rotateX = ((y / rect.height) - 0.5) * -10;
    ref.current.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-6px)`;
  };

  const handleCardMouseLeave = (ref) => {
    if (!ref.current) return;
    ref.current.style.transform = '';
  };

  return (
    <div className="min-h-screen bg-[#07121e] text-[#17212c] overflow-x-hidden selection:bg-[#ff806b] selection:text-[#101820]">
      
      {/* =====================================================
           TOP NAVBAR (Exact Match to Image)
      ===================================================== */}
      <header className="w-full bg-[#07121e] border-b border-white/[0.06] sticky top-0 z-50">
        <div className="max-w-[1400px] mx-auto px-6 sm:px-10 h-[72px] flex items-center justify-between">
          
          {/* Logo */}
          <div 
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            className="flex items-center gap-2.5 cursor-pointer select-none"
          >
            {/* Hexagonal/Diamond Orange Icon */}
            <div className="w-[26px] h-[26px] border-[2.5px] border-[#ff806b] rounded-[7px] rotate-45 relative flex items-center justify-center shadow-[0_0_12px_rgba(255,128,107,0.3)]">
              <div className="w-2 h-2 bg-[#ff806b] rounded-full" />
            </div>
            <span className="text-white text-lg font-bold tracking-tight font-sans">
              CareerTech<span className="text-[#ff806b]">.AI</span>
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center gap-7 text-[13px] font-medium text-[#b0bac5]">
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#how" className="hover:text-white transition-colors">How It Works</a>
            <button onClick={() => navigate('gap-analysis')} className="hover:text-white transition-colors cursor-pointer">Pricing</button>
            <div className="px-3.5 py-1 rounded-full bg-[#152332] text-white text-[12px] border border-white/[0.08]">
              About
            </div>
          </nav>

          {/* Right Action Buttons */}
          <div className="flex items-center gap-5">
            <button
              onClick={() => navigate('login')}
              className="text-[#b0bac5] hover:text-white text-[13px] font-medium transition-colors cursor-pointer"
            >
              Login
            </button>
            <button
              onClick={() => navigate('signup')}
              className="bg-[#ff806b] hover:bg-[#ff725a] text-[#101820] font-semibold text-xs px-5 py-2.5 rounded-full shadow-[0_6px_20px_rgba(255,128,107,0.25)] hover:shadow-[0_10px_25px_rgba(255,128,107,0.4)] transition-all duration-200 cursor-pointer"
            >
              Get Started
            </button>
          </div>

        </div>
      </header>

      {/* =====================================================
           HERO SECTION (Diagonal Cut matching screenshot)
      ===================================================== */}
      <section className="relative overflow-hidden bg-[#f7f3ed] min-h-[580px]">
        
        {/* The Dark Navy Left Section with Diagonal SVG Cut */}
        <div className="grid grid-cols-1 lg:grid-cols-[50%_50%] min-h-[580px] relative">
          
          {/* HERO LEFT PANEL */}
          <div className="relative bg-[#07121e] px-8 sm:px-14 lg:pl-16 lg:pr-10 pt-16 pb-20 flex flex-col justify-center z-10">
            
            {/* Smooth Diagonal Curve Divider overlay on right edge */}
            <div className="hidden lg:block absolute top-0 -right-[78px] bottom-0 w-[80px] overflow-hidden z-20 pointer-events-none">
              <svg 
                viewBox="0 0 100 100" 
                preserveAspectRatio="none" 
                className="w-full h-full text-[#07121e] fill-current"
              >
                <path d="M0,0 L90,0 Q60,40 30,70 Q10,88 0,100 Z" />
              </svg>
            </div>

            <div className="max-w-[480px]">
              
              {/* Eyebrow */}
              <p className="text-[#aab4bf] text-[10px] font-mono uppercase tracking-[2px] font-medium mb-3">
                AI CAREER GUIDANCE PLATFORM
              </p>

              {/* Title */}
              <h1 className="text-white font-serif text-[42px] sm:text-[54px] lg:text-[58px] font-normal leading-[1.05] tracking-[-1.5px] mb-4">
                Turn Your <br />
                Resume Into <br />
                <span className="text-[#ff806b] drop-shadow-[0_0_20px_rgba(255,128,107,0.35)]">
                  Real Opportunities
                </span>
              </h1>

              {/* Subtitle */}
              <p className="text-[#a8b4bf] text-[13px] leading-[1.7] max-w-[420px] mb-8 font-normal">
                Get personalized job recommendations, identify your skill gaps, learn what to study, and prepare for interviews — all powered by AI.
              </p>

              {/* Action Buttons */}
              <div className="flex flex-wrap items-center gap-3.5 mb-11">
                <button
                  onClick={() => navigate('resume-upload')}
                  className="bg-[#ff806b] hover:bg-[#ff725a] text-[#111820] px-6 py-3.5 rounded-xl text-xs font-bold transition-all duration-300 shadow-[0_10px_25px_rgba(255,128,107,0.25)] hover:-translate-y-0.5 cursor-pointer flex items-center gap-1.5"
                >
                  Upload Resume →
                </button>

                <a
                  href="#how"
                  className="px-5 py-3.5 rounded-xl border border-white/20 bg-white/[0.04] text-[#d3dbe2] hover:text-white hover:border-[#ff806b]/50 text-xs font-medium transition-all duration-200 flex items-center gap-2"
                >
                  <span className="w-4 h-4 rounded-full border border-[#ff806b] text-[#ff806b] text-[9px] flex items-center justify-center font-bold">▶</span>
                  See How It Works
                </a>
              </div>

              {/* Social Proof Stats */}
              <div className="flex items-center gap-10 pt-2 border-t border-white/[0.08]">
                <div>
                  <strong className="block text-white font-serif text-2xl font-normal leading-tight">
                    50K+
                  </strong>
                  <span className="text-[#7d8995] text-[11px] block mt-0.5">
                    Students & Job Seekers
                  </span>
                </div>

                <div>
                  <strong className="block text-white font-serif text-2xl font-normal leading-tight flex items-center gap-1">
                    4.8 <Star className="w-4 h-4 fill-[#ff806b] text-[#ff806b]" />
                  </strong>
                  <span className="text-[#7d8995] text-[11px] block mt-0.5">
                    User Rating
                  </span>
                </div>

                <div>
                  <strong className="block text-white font-serif text-2xl font-normal leading-tight">
                    95%
                  </strong>
                  <span className="text-[#7d8995] text-[11px] block mt-0.5">
                    Career Match Accuracy
                  </span>
                </div>
              </div>

            </div>

          </div>

          {/* HERO RIGHT PANEL (Warm Cream with Glowing Rings & Floating Cards) */}
          <div className="relative bg-[#f7f3ed] flex items-center justify-center p-8 sm:p-12 overflow-hidden min-h-[460px]">
            
            {/* Glowing Concentric Orbits in Background */}
            <div className="absolute w-[380px] h-[380px] rounded-full border-2 border-[#ff806b]/35 shadow-[0_0_60px_rgba(255,128,107,0.22)] animate-spin-cw pointer-events-none" />
            <div className="absolute w-[290px] h-[290px] rounded-full border border-[#ff806b]/25 border-dashed animate-spin-ccw pointer-events-none" />
            <div className="absolute w-[200px] h-[200px] rounded-full bg-gradient-to-tr from-[#ffe1d9]/50 to-transparent blur-xl pointer-events-none" />

            {/* Floating Visual Cards */}
            <div className="relative z-10 flex items-center gap-4 sm:gap-6">
              
              {/* Card 1: Your Resume */}
              <motion.div
                ref={resumeCardRef}
                onMouseMove={(e) => handleCardMouseMove(e, resumeCardRef)}
                onMouseLeave={() => handleCardMouseLeave(resumeCardRef)}
                onClick={() => navigate('resume-upload')}
                whileHover={{ scale: 1.02 }}
                className="w-[155px] sm:w-[170px] min-h-[200px] p-5 bg-white border border-[#eae3d9] rounded-2xl shadow-[0_20px_50px_rgba(48,37,27,0.12)] cursor-pointer select-none transition-all duration-300"
              >
                {/* Document Icon Box */}
                <div className="w-10 h-10 rounded-xl bg-[#eef3f8] text-[#334e68] flex items-center justify-center mx-auto mb-3">
                  <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                    <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
                  </svg>
                </div>

                <div className="text-center font-bold text-[13px] text-[#17212c] mb-4">
                  Your Resume
                </div>

                {/* Skeleton preview bars */}
                <div className="space-y-2">
                  <div className="h-1 bg-[#d5dde4] rounded-full w-full" />
                  <div className="h-1 bg-[#d5dde4] rounded-full w-[70%]" />
                  <div className="h-1 bg-[#d5dde4] rounded-full w-[85%]" />
                  <div className="h-1 bg-[#d5dde4] rounded-full w-[45%]" />
                </div>
              </motion.div>

              {/* Animated Floating Arrow */}
              <div 
                onClick={() => navigate('gap-analysis')}
                className="w-8 h-8 rounded-full bg-[#17212c] text-white flex items-center justify-center text-sm font-bold shadow-md cursor-pointer shrink-0 animate-arrow-move"
              >
                →
              </div>

              {/* Card 2: Your Future */}
              <motion.div
                ref={futureCardRef}
                onMouseMove={(e) => handleCardMouseMove(e, futureCardRef)}
                onMouseLeave={() => handleCardMouseLeave(futureCardRef)}
                onClick={() => navigate('resume-analysis')}
                whileHover={{ scale: 1.02 }}
                className="w-[170px] sm:w-[195px] min-h-[215px] p-5 bg-white border border-[#eae3d9] rounded-2xl shadow-[0_20px_50px_rgba(48,37,27,0.12)] cursor-pointer select-none transition-all duration-300"
              >
                <div className="font-bold text-sm text-[#17212c] mb-3.5">
                  Your Future
                </div>

                <ul className="space-y-2.5 text-[11px] text-[#334155] font-medium">
                  <li className="flex items-center gap-2">
                    <span className="w-4 h-4 rounded-full bg-[#1e293b] text-white flex items-center justify-center text-[9px] font-bold shrink-0">
                      <Check className="w-2.5 h-2.5 text-white" />
                    </span>
                    Better Skills
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-4 h-4 rounded-full bg-[#1e293b] text-white flex items-center justify-center text-[9px] font-bold shrink-0">
                      <Check className="w-2.5 h-2.5 text-white" />
                    </span>
                    Job Matches
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-4 h-4 rounded-full bg-[#1e293b] text-white flex items-center justify-center text-[9px] font-bold shrink-0">
                      <Check className="w-2.5 h-2.5 text-white" />
                    </span>
                    Interview Ready
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="w-4 h-4 rounded-full bg-[#1e293b] text-white flex items-center justify-center text-[9px] font-bold shrink-0">
                      <Check className="w-2.5 h-2.5 text-white" />
                    </span>
                    Skill Improvement
                  </li>
                </ul>
              </motion.div>

            </div>

          </div>

        </div>

      </section>

      {/* =====================================================
           FEATURES SECTION (Exact 5 columns matching screenshot)
      ===================================================== */}
      <section id="features" className="py-16 px-6 sm:px-10 bg-[#f7f3ed] text-[#17212c] text-center border-t border-[#e8e1d6]">
        <div className="max-w-[1240px] mx-auto">
          
          <h2 className="text-[#17212c] font-serif text-2xl sm:text-[32px] font-normal tracking-[-0.5px]">
            Everything You Need for Career Success
          </h2>
          <p className="text-[#64748b] text-xs sm:text-[13px] mt-1.5 mb-12 font-normal">
            One platform. Complete career support.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 divide-y sm:divide-y-0 lg:divide-x divide-[#ded6ca]">
            
            {/* Feature 1: Smart Resume Analysis */}
            <div 
              onClick={() => navigate('resume-analysis')}
              className="py-6 px-4 hover:-translate-y-1.5 transition-all duration-300 cursor-pointer group"
            >
              <div className="w-11 h-11 rounded-xl bg-[#ffece6] text-[#ff806b] flex items-center justify-center mx-auto mb-3.5 group-hover:scale-110 transition-transform">
                <FileText className="w-5 h-5 text-[#ff806b]" />
              </div>
              <h3 className="text-[#17212c] font-bold text-[13px] sm:text-sm leading-tight mb-1.5">
                Smart Resume<br />Analysis
              </h3>
              <p className="text-[#64748b] text-[11px] leading-relaxed">
                Get ATS-friendly<br />improvements
              </p>
            </div>

            {/* Feature 2: Skill Gap Detection */}
            <div 
              onClick={() => navigate('resume-analysis')}
              className="py-6 px-4 hover:-translate-y-1.5 transition-all duration-300 cursor-pointer group"
            >
              <div className="w-11 h-11 rounded-xl bg-[#ffece6] text-[#ff806b] flex items-center justify-center mx-auto mb-3.5 group-hover:scale-110 transition-transform">
                <Target className="w-5 h-5 text-[#ff806b]" />
              </div>
              <h3 className="text-[#17212c] font-bold text-[13px] sm:text-sm leading-tight mb-1.5">
                Skill Gap<br />Detection
              </h3>
              <p className="text-[#64748b] text-[11px] leading-relaxed">
                Know what to learn<br />next
              </p>
            </div>

            {/* Feature 3: AI Learning Recommendations */}
            <div 
              onClick={() => navigate('resume-analysis')}
              className="py-6 px-4 hover:-translate-y-1.5 transition-all duration-300 cursor-pointer group"
            >
              <div className="w-11 h-11 rounded-xl bg-[#ffece6] text-[#ff806b] flex items-center justify-center mx-auto mb-3.5 group-hover:scale-110 transition-transform">
                <BookOpen className="w-5 h-5 text-[#ff806b]" />
              </div>
              <h3 className="text-[#17212c] font-bold text-[13px] sm:text-sm leading-tight mb-1.5">
                AI Learning<br />Recommendations
              </h3>
              <p className="text-[#64748b] text-[11px] leading-relaxed">
                Personalized &<br />role-specific
              </p>
            </div>

            {/* Feature 4: Interview Preparation */}
            <div 
              onClick={() => navigate('resume-analysis')}
              className="py-6 px-4 hover:-translate-y-1.5 transition-all duration-300 cursor-pointer group"
            >
              <div className="w-11 h-11 rounded-xl bg-[#ffece6] text-[#ff806b] flex items-center justify-center mx-auto mb-3.5 group-hover:scale-110 transition-transform">
                <Mic className="w-5 h-5 text-[#ff806b]" />
              </div>
              <h3 className="text-[#17212c] font-bold text-[13px] sm:text-sm leading-tight mb-1.5">
                Interview<br />Preparation
              </h3>
              <p className="text-[#64748b] text-[11px] leading-relaxed">
                Practice with real<br />questions & feedback
              </p>
            </div>

            {/* Feature 5: Targeted Action Plan */}
            <div 
              onClick={() => navigate('resume-analysis')}
              className="py-6 px-4 hover:-translate-y-1.5 transition-all duration-300 cursor-pointer group"
            >
              <div className="w-11 h-11 rounded-xl bg-[#ffece6] text-[#ff806b] flex items-center justify-center mx-auto mb-3.5 group-hover:scale-110 transition-transform">
                <Compass className="w-5 h-5 text-[#ff806b]" />
              </div>
              <h3 className="text-[#17212c] font-bold text-[13px] sm:text-sm leading-tight mb-1.5">
                Targeted<br />Action Plan
              </h3>
              <p className="text-[#64748b] text-[11px] leading-relaxed">
                Structured plan<br />to get hired
              </p>
            </div>

          </div>

        </div>
      </section>

      {/* =====================================================
           HOW IT WORKS SECTION (Exact Match to screenshot)
      ===================================================== */}
      <section id="how" className="py-20 px-6 sm:px-10 bg-[#07121e] text-white border-t border-white/[0.06]">
        <div className="max-w-[1240px] mx-auto">
          
          <h2 className="text-white font-serif text-2xl sm:text-[32px] font-normal">
            How It Works
          </h2>
          <p className="text-[#8b98a5] text-xs sm:text-[13px] mt-1 mb-10">
            Just 4 simple steps to get on the right track.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            
            {/* Step 1 */}
            <div 
              onClick={() => navigate('resume-upload')}
              className="p-6 rounded-2xl bg-[#0b1928] border border-white/[0.08] hover:border-[#ff806b]/40 hover:-translate-y-1.5 transition-all duration-300 cursor-pointer"
            >
              <div className="w-7 h-7 rounded-full bg-[#ff806b] text-[#101820] flex items-center justify-center text-xs font-bold mb-5">
                1
              </div>
              <h3 className="text-white font-bold text-[15px] mb-2 font-sans">
                Upload Resume
              </h3>
              <p className="text-[#8d9aa7] text-xs leading-[1.6]">
                Add your resume or create one.
              </p>
            </div>

            {/* Step 2 */}
            <div 
              onClick={() => navigate('resume-upload')}
              className="p-6 rounded-2xl bg-[#0b1928] border border-white/[0.08] hover:border-[#ff806b]/40 hover:-translate-y-1.5 transition-all duration-300 cursor-pointer"
            >
              <div className="w-7 h-7 rounded-full bg-[#ff806b] text-[#101820] flex items-center justify-center text-xs font-bold mb-5">
                2
              </div>
              <h3 className="text-white font-bold text-[15px] mb-2 font-sans">
                Set Target Role
              </h3>
              <p className="text-[#8d9aa7] text-xs leading-[1.6]">
                Choose your dream job position.
              </p>
            </div>

            {/* Step 3 */}
            <div 
              onClick={() => navigate('gap-analysis')}
              className="p-6 rounded-2xl bg-[#0b1928] border border-white/[0.08] hover:border-[#ff806b]/40 hover:-translate-y-1.5 transition-all duration-300 cursor-pointer"
            >
              <div className="w-7 h-7 rounded-full bg-[#ff806b] text-[#101820] flex items-center justify-center text-xs font-bold mb-5">
                3
              </div>
              <h3 className="text-white font-bold text-[15px] mb-2 font-sans">
                Get AI Insights
              </h3>
              <p className="text-[#8d9aa7] text-xs leading-[1.6]">
                See skill gaps, learning plan & roadmap.
              </p>
            </div>

            {/* Step 4 */}
            <div 
              onClick={() => navigate('roadmap')}
              className="p-6 rounded-2xl bg-[#0b1928] border border-white/[0.08] hover:border-[#ff806b]/40 hover:-translate-y-1.5 transition-all duration-300 cursor-pointer"
            >
              <div className="w-7 h-7 rounded-full bg-[#ff806b] text-[#101820] flex items-center justify-center text-xs font-bold mb-5">
                4
              </div>
              <h3 className="text-white font-bold text-[15px] mb-2 font-sans">
                Start Learning
              </h3>
              <p className="text-[#8d9aa7] text-xs leading-[1.6]">
                Follow your plan and track progress.
              </p>
            </div>

          </div>

        </div>
      </section>

      {/* =====================================================
           FOOTER (Exact Match to screenshot)
      ===================================================== */}
      <footer className="py-6 px-6 sm:px-10 bg-[#050c14] border-t border-white/[0.05] text-[#7d8995] text-xs">
        <div className="max-w-[1240px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div>
            © 2026 CareerTech.AI
          </div>
          <div>
            AI-Powered Career Guidance
          </div>
          <div className="text-slate-400">
            Resume → Skills → Interview → Job Ready
          </div>
        </div>
      </footer>

    </div>
  );
};
