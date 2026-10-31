import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Common Components
import { Navbar } from './components/common/Navbar';
import { Footer } from './components/common/Footer';
import { Toast } from './components/common/Toast';

// Pages
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { Dashboard } from './pages/Dashboard';
import { ResumeAnalysisFlow } from './pages/ResumeAnalysisFlow';
import { InterviewSetup } from './pages/InterviewSetup';
import { InterviewRoom } from './pages/InterviewRoom';
import { InterviewProcessing } from './pages/InterviewProcessing';
import { InterviewReport } from './pages/InterviewReport';

// Data & Services
import { authService } from './utils/apiService';
import { supabase } from './utils/supabaseClient';
import { CANDIDATE_PROFILE } from './data/mockData';

export default function App() {
  const [currentRoute, setCurrentRoute] = useState('landing');
  const [currentUser, setCurrentUser] = useState(() => authService.getCurrentUser());
  const [interviewSessionData, setInterviewSessionData] = useState(null);
  const [interviewReportData, setInterviewReportData] = useState(null);

  // Toast System
  const [toast, setToast] = useState({
    isVisible: false,
    message: '',
    type: 'success'
  });

  const showToast = (message, type = 'success') => {
    setToast({ isVisible: true, message, type });
  };

  const hideToast = () => {
    setToast(prev => ({ ...prev, isVisible: false }));
  };

  // Navigation Helper with Route Guard
  const navigate = (route) => {
    const protectedRoutes = [
      'dashboard', 
      'resume-analysis', 
      'resume-upload', 
      'gap-analysis', 
      'roadmap', 
      'interview-setup', 
      'interview', 
      'interview-room', 
      'interview-processing', 
      'report'
    ];

    if (protectedRoutes.includes(route) && !currentUser) {
      showToast("Access restricted: Please sign in or create an account to proceed.", "warning");
      setCurrentRoute('login');
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    setCurrentRoute(route);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Check Supabase session on startup and subscribe to auth state changes
  useEffect(() => {
    const checkInitialAuth = async () => {
      const user = await authService.getCurrentUserAsync();
      setCurrentUser(user);
    };
    checkInitialAuth();

    const { data: authListener } = supabase.auth.onAuthStateChange((event, session) => {
      if (session?.user) {
        const mapped = authService.mapSupabaseUser(session.user);
        setCurrentUser(mapped);
      } else if (event === 'SIGNED_OUT') {
        setCurrentUser(null);
        setCurrentRoute('landing');
      }
    });

    return () => {
      if (authListener?.subscription) {
        authListener.subscription.unsubscribe();
      }
    };
  }, []);

  // Cursor Glow follower (as in user's design reference)
  useEffect(() => {
    const cursor = document.getElementById('cursor-glow');
    if (!cursor) return;

    const handleMouseMove = (e) => {
      cursor.style.left = `${e.clientX}px`;
      cursor.style.top = `${e.clientY}px`;
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleLoginSuccess = (user) => {
    setCurrentUser(user);
    showToast(`Welcome back, ${user.name.split(' ')[0]}!`, 'success');
  };

  const handleLogout = async () => {
    await authService.logout();
    setCurrentUser(null);
    setInterviewSessionData(null);
    setInterviewReportData(null);
    showToast("Signed out successfully.", "info");
    navigate('landing');
  };

  const handleResetProfile = () => {
    try {
      localStorage.removeItem('careerai_user');
    } catch (e) {}
    setCurrentUser(null);
    setInterviewSessionData(null);
    setInterviewReportData(null);
    showToast("Dashboard reset. Please sign in to begin fresh assessment.", "info");
    navigate('login');
  };

  // Hide Navbar & Footer in full-screen interview room & auth screens
  const isInterviewRoom = currentRoute === 'interview' || currentRoute === 'interview-room' || currentRoute === 'interview-processing';
  const isAuthPage = currentRoute === 'login' || currentRoute === 'signup';
  const isLanding = currentRoute === 'landing';

  return (
    <div className="min-h-screen bg-navy-900 text-slate-100 flex flex-col font-sans selection:bg-coral selection:text-navy-950 relative overflow-x-hidden">
      
      {/* Interactive Cursor Glow Effect from reference design */}
      <div
        id="cursor-glow"
        className="cursor-glow-dot pointer-events-none"
      />

      {/* Global Toast Alert */}
      <Toast
        isVisible={toast.isVisible}
        message={toast.message}
        type={toast.type}
        onClose={hideToast}
      />

      {/* Top Navbar */}
      {!isInterviewRoom && !isAuthPage && !isLanding && (
        <Navbar
          currentPath={currentRoute}
          navigate={navigate}
          user={currentUser}
          showNotificationToast={showToast}
          onResetProfile={handleResetProfile}
          onLogout={handleLogout}
        />
      )}

      {/* Main View Router */}
      <main className="flex-1">
        <AnimatePresence mode="wait">
          {currentRoute === 'landing' && (
            <motion.div
              key="landing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Landing navigate={navigate} />
            </motion.div>
          )}

          {currentRoute === 'login' && (
            <motion.div
              key="login"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <Login navigate={navigate} onLoginSuccess={handleLoginSuccess} />
            </motion.div>
          )}

          {currentRoute === 'signup' && (
            <motion.div
              key="signup"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              <Signup navigate={navigate} onLoginSuccess={handleLoginSuccess} />
            </motion.div>
          )}

          {currentRoute === 'dashboard' && (
            <motion.div
              key="dashboard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <Dashboard navigate={navigate} user={currentUser} />
            </motion.div>
          )}

          {(currentRoute === 'resume-analysis' || currentRoute === 'resume-upload') && (
            <motion.div
              key="resume-analysis"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <ResumeAnalysisFlow
                navigate={navigate}
                onCandidateUpdate={(profile) => {
                  if (profile && profile.name) {
                    const scoreVal = profile.score != null ? profile.score : 80;
                    const roleVal = profile.role || currentUser.role || "Software Engineer";
                    const updated = {
                      ...currentUser,
                      name: profile.name,
                      email: profile.email || currentUser.email,
                      phone: profile.phone || currentUser.phone,
                      role: roleVal,
                      skills: profile.skills || currentUser.skills,
                      resumeScore: scoreVal,
                      isAssessed: true,
                      recentActivity: [
                        {
                          title: `Resume Analyzed: ${scoreVal}/100 ATS Score (${roleVal})`,
                          time: "Just now",
                          type: "analysis"
                        },
                        ...(currentUser.recentActivity || [])
                      ]
                    };
                    setCurrentUser(updated);
                    try {
                      localStorage.setItem('careerai_user', JSON.stringify(updated));
                    } catch (e) {}
                    setInterviewSessionData(prev => ({
                      ...prev,
                      candidateName: profile.name,
                      role: roleVal
                    }));
                    showToast(`Resume evaluated for ${profile.name}!`, "success");
                  }
                }}
              />
            </motion.div>
          )}

          {currentRoute === 'interview-setup' && (
            <motion.div
              key="interview-setup"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <InterviewSetup
                navigate={navigate}
                currentUser={currentUser}
                onEnterInterview={(config) => setInterviewSessionData({
                  ...config,
                  candidateName: currentUser?.name || "Candidate",
                  role: currentUser?.role || "Software Engineer"
                })}
              />
            </motion.div>
          )}

          {(currentRoute === 'interview' || currentRoute === 'interview-room') && (
            <motion.div
              key="interview-room"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <InterviewRoom
                navigate={navigate}
                currentUser={currentUser}
                sessionConfig={interviewSessionData}
                onFinishInterview={(transcripts, evalData) => {
                  const rep = evalData?.report || evalData;
                  if (rep && (rep.overallScore != null || rep.interviewScore != null)) {
                    setInterviewReportData(rep);
                    const finalScore = rep.overallScore ?? rep.interviewScore;
                    const roleTitle = rep.targetRole || currentUser.role || "Software Engineer";
                    const updatedUser = {
                      ...currentUser,
                      interviewReadiness: finalScore,
                      recentActivity: [
                        {
                          title: `Mock Interview Evaluated: ${finalScore}/100 (${roleTitle})`,
                          time: "Just now",
                          type: "interview"
                        },
                        ...(currentUser.recentActivity || [])
                      ]
                    };
                    setCurrentUser(updatedUser);
                    try {
                      localStorage.setItem('careerai_user', JSON.stringify(updatedUser));
                    } catch (e) {}
                  }
                  showToast("Interview completed! Generating scorecard...", "info");
                }}
              />
            </motion.div>
          )}

          {currentRoute === 'interview-processing' && (
            <motion.div
              key="interview-processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <InterviewProcessing
                navigate={navigate}
                onProcessingComplete={() => showToast("Interview Scorecard Ready!", "success")}
              />
            </motion.div>
          )}

          {(currentRoute === 'report' || currentRoute === 'interview-report') && (
            <motion.div
              key="report"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
            >
              <InterviewReport 
                navigate={navigate} 
                reportData={interviewReportData} 
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Global Footer (Visible on core app views) */}
      {!isInterviewRoom && !isAuthPage && !isLanding && (
        <Footer navigate={navigate} />
      )}

    </div>
  );
}
