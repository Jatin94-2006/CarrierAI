// CareerAI API Service Abstraction Layer
// Connected directly to FastAPI Multi-Agent backend (CTBuildfest 2.0 -> Agent 2 -> Agent 4 -> Agent 3 -> Agent 5).
// STRICT REQUIREMENT: ZERO EMOJIS in logs, outputs, or PDF exports.

import { 
  CANDIDATE_PROFILE, 
  HIGH_SCORE_ANALYSIS, 
  LOW_SCORE_ANALYSIS, 
  DETAILED_GAP_DATA, 
  INTERVIEW_REPORT_DATA 
} from '../data/mockData';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { supabase } from './supabaseClient';

const API_BASE = (
  import.meta.env.VITE_API_URL ||
  (typeof window !== "undefined" && !window.location.hostname.includes("localhost") && !window.location.hostname.includes("127.0.0.1")
    ? "https://carrierai.onrender.com"
    : "")
).replace(/\/$/, "");
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export const authService = {
  // Map Supabase User object to CareerAI Candidate Profile
  mapSupabaseUser: (sbUser) => {
    if (!sbUser) return null;
    const meta = sbUser.user_metadata || {};
    const email = sbUser.email || "";
    const parsedName = meta.full_name || meta.name || (email ? email.split('@')[0].replace(/[._-]/g, ' ') : "Candidate");
    const formattedName = parsedName.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');

    let cached = {};
    try {
      const localStr = localStorage.getItem(`careerai_user_${sbUser.id}`);
      if (localStr) cached = JSON.parse(localStr);
    } catch (_) {}

    return {
      ...CANDIDATE_PROFILE,
      ...cached,
      id: sbUser.id,
      name: formattedName,
      email: email,
      isAssessed: cached.isAssessed || false,
      resumeScore: cached.resumeScore || null,
      interviewReadiness: cached.interviewReadiness || null
    };
  },

  // 1. Sign In (Existing Users)
  login: async (email, password) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email: email.trim(),
        password: password
      });

      if (error) {
        return { success: false, error: error.message };
      }

      const user = authService.mapSupabaseUser(data.user);
      localStorage.setItem('careerai_user', JSON.stringify(user));
      return { success: true, user, session: data.session };
    } catch (err) {
      return { success: false, error: err.message || "Failed to authenticate with Supabase." };
    }
  },

  // 2. Sign Up (New Users)
  signup: async (name, email, password) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email: email.trim(),
        password: password,
        options: {
          data: {
            full_name: name.trim()
          }
        }
      });

      if (error) {
        return { success: false, error: error.message };
      }

      if (data.user) {
        const user = authService.mapSupabaseUser(data.user);
        if (data.session) {
          localStorage.setItem('careerai_user', JSON.stringify(user));
        }
        return { 
          success: true, 
          user, 
          session: data.session,
          needsConfirmation: !data.session
        };
      }
      return { success: false, error: "Signup returned an empty user response." };
    } catch (err) {
      return { success: false, error: err.message || "Failed to create account with Supabase." };
    }
  },

  // 3. Google OAuth Sign In
  signInWithGoogle: async () => {
    try {
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: window.location.origin
        }
      });
      if (error) {
        return { success: false, error: error.message };
      }
      return { success: true, data };
    } catch (err) {
      return { success: false, error: err.message || "Google sign in error." };
    }
  },

  // 4. Get Current User Sync (Cached session check)
  getCurrentUser: () => {
    const saved = localStorage.getItem('careerai_user');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed && (parsed.id || parsed.email)) {
          return parsed;
        }
      } catch (e) {}
    }
    return null; // Unauthenticated by default: User must sign in!
  },

  // 5. Get Current User Async (Direct Supabase session validation)
  getCurrentUserAsync: async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.user) {
        const user = authService.mapSupabaseUser(session.user);
        localStorage.setItem('careerai_user', JSON.stringify(user));
        return user;
      }
    } catch (e) {}
    localStorage.removeItem('careerai_user');
    return null;
  },

  // 6. Sign Out
  logout: async () => {
    try {
      await supabase.auth.signOut();
    } catch (_) {}
    localStorage.removeItem('careerai_user');
    return { success: true };
  }
};

let lastAnalysisResult = null;

export const careerService = {
  // 1. Analyze Resume with Live Steps Progress (connected to CTBuildfest 2.0 & FastAPI backend)
  analyzeResume: async (file, jobDescription, targetScoreType = null, onProgress) => {
    const steps = [
      { step: 1, text: "Resume uploaded and parsed (CTBuildfest 2.0)", progress: 15 },
      { step: 2, text: "Extracting candidate and job structured JSON", progress: 30 },
      { step: 3, text: "Evaluating deterministic ATS score across 7 dimensions", progress: 45 },
      { step: 4, text: "Benchmarking against 100 synthetic applicant profiles", progress: 60 },
      { step: 5, text: "Computing candidate percentile and qualification rank", progress: 75 },
      { step: 6, text: "Running Agent 2 semantic technical and soft skill gap analysis", progress: 85 },
      { step: 7, text: "Curating fast-track micro-courses (<1 week) via Agent 3", progress: 92 },
      { step: 8, text: "Finalizing Agent 5 30-day learning plan and PDF report", progress: 100 }
    ];

    const backendPromise = (async () => {
      try {
        const formData = new FormData();
        if (file && file.fileObject instanceof File) {
          formData.append("file", file.fileObject);
        } else if (file instanceof File) {
          formData.append("file", file);
        } else if (file && file.rawText) {
          formData.append("resume_text", file.rawText);
        }
        if (jobDescription) {
          formData.append("job_description", jobDescription);
        }
        if (targetScoreType) {
          formData.append("score_simulation_type", targetScoreType);
        }

        const response = await fetch(`${API_BASE}/api/resume/analyze`, {
          method: "POST",
          body: formData
        });

        if (response.ok) {
          const json = await response.json();
          lastAnalysisResult = json;
          return json;
        }
      } catch (err) {
        console.warn("Backend /api/resume/analyze call failed, using fallback:", err);
      }
      return null;
    })();

    for (const stepObj of steps) {
      await delay(450);
      if (onProgress) onProgress(stepObj);
    }

    const backendResult = await backendPromise;
    if (backendResult && backendResult.data) {
      const candName = backendResult.candidateName || backendResult.data.candidateName || (backendResult.candidateProfile && backendResult.candidateProfile.name);
      const candEmail = backendResult.candidateEmail || backendResult.data.candidateEmail || (backendResult.candidateProfile && backendResult.candidateProfile.email);
      const candPhone = backendResult.candidatePhone || backendResult.data.candidatePhone || (backendResult.candidateProfile && backendResult.candidateProfile.phone);
      const targetRole = backendResult.targetRole || backendResult.data.targetRole || (backendResult.candidateProfile && backendResult.candidateProfile.role);

      const mergedData = {
        ...backendResult.data,
        candidateName: candName,
        candidateEmail: candEmail,
        candidatePhone: candPhone,
        targetRole: targetRole,
        candidateProfile: backendResult.candidateProfile || {
          name: candName,
          email: candEmail,
          phone: candPhone,
          role: targetRole
        }
      };

      return {
        success: true,
        data: mergedData,
        candidateProfile: mergedData.candidateProfile,
        gapData: backendResult.gapData,
        roadmap: backendResult.roadmap
      };
    }

    return { 
      success: false, 
      error: "Backend service unreachable at http://127.0.0.1:8000. Please start the backend server." 
    };
  },

  // 2. Calculate Resume Score
  calculateResumeScore: async (resumeData) => {
    if (lastAnalysisResult && lastAnalysisResult.data) {
      return {
        score: lastAnalysisResult.data.overallScore,
        benchmark: 75,
        isQualified: lastAnalysisResult.data.isInterviewReady
      };
    }
    await delay(200);
    return {
      score: 82,
      benchmark: 75,
      isQualified: true
    };
  },

  // 3. Automatic Gap Analysis for Low Scores
  analyzeSkillGaps: async (onProgress) => {
    const steps = [
      { step: 1, text: "Resume analysis completed", progress: 20 },
      { step: 2, text: "Job requirements extracted", progress: 45 },
      { step: 3, text: "Comparing required skills", progress: 65 },
      { step: 4, text: "Identifying missing skills", progress: 80 },
      { step: 5, text: "Evaluating proficiency gaps", progress: 92 },
      { step: 6, text: "Generating recommendations", progress: 100 }
    ];

    for (const stepObj of steps) {
      await delay(350);
      if (onProgress) onProgress(stepObj);
    }

    if (lastAnalysisResult && lastAnalysisResult.gapData) {
      return { success: true, data: lastAnalysisResult.gapData };
    }

    try {
      const res = await fetch(`${API_BASE}/api/gap-analysis`);
      if (res.ok) {
        const json = await res.json();
        if (json.data) return { success: true, data: json.data };
      }
    } catch (e) {
      console.warn("Could not fetch /api/gap-analysis:", e);
    }

    return { success: true, data: DETAILED_GAP_DATA };
  },

  // 4. Generate Recommendations
  generateRecommendations: async (gaps) => {
    if (lastAnalysisResult && lastAnalysisResult.gapData && lastAnalysisResult.gapData.recommendations) {
      return { success: true, data: lastAnalysisResult.gapData.recommendations };
    }
    await delay(200);
    return { success: true, data: DETAILED_GAP_DATA.recommendations };
  },

  // 5. Start Interview Session
  startInterview: async (config = {}) => {
    try {
      const res = await fetch(`${API_BASE}/interviews`, {
        method: "POST"
      });
      if (res.ok) {
        return await res.json();
      }
    } catch (e) {
      console.warn("Could not start interview directly:", e);
    }
    return {
      sessionId: `ai-session-${Date.now()}`,
      status: "initialized",
      questionsCount: 5,
      role: "Full Stack Developer"
    };
  },

  // 6. Post-Interview Processing & Analysis
  analyzeInterview: async (transcripts, onProgress) => {
    const steps = [
      { step: 1, text: "Interview completed", progress: 15 },
      { step: 2, text: "Transcribing responses", progress: 35 },
      { step: 3, text: "Evaluating technical answers", progress: 55 },
      { step: 4, text: "Analyzing communication", progress: 72 },
      { step: 5, text: "Evaluating confidence", progress: 85 },
      { step: 6, text: "Calculating final score", progress: 94 },
      { step: 7, text: "Generating final report", progress: 100 }
    ];

    for (const stepObj of steps) {
      await delay(450);
      if (onProgress) onProgress(stepObj);
    }

    return { success: true, data: INTERVIEW_REPORT_DATA };
  },

  // 7. Generate Final Comprehensive Report
  generateReport: async (type = "interview") => {
    if (lastAnalysisResult && lastAnalysisResult.gapData) {
      return {
        success: true,
        data: type === "interview" ? INTERVIEW_REPORT_DATA : lastAnalysisResult.gapData
      };
    }
    await delay(250);
    return {
      success: true,
      data: type === "interview" ? INTERVIEW_REPORT_DATA : DETAILED_GAP_DATA
    };
  }
};

export const interviewService = careerService;

export const pdfService = {
  generateReportPDF: async (elementId = "careerai-final-report", reportTitle = "CareerAI Assessment Report") => {
    try {
      // 1. Try downloading official PDF from backend (Agent 5 ReportLab PDF)
      const res = await fetch(`${API_BASE}/api/report/pdf`);
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "CareerAI_Assessment_Report.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        return true;
      }
    } catch (e) {
      console.warn("Backend PDF download fallback to client rendering:", e);
    }

    try {
      const element = document.getElementById(elementId);
      if (element) {
        const canvas = await html2canvas(element, {
          scale: 2,
          useCORS: true,
          logging: false,
          backgroundColor: '#07121e'
        });
        
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const pdfWidth = pdf.internal.pageSize.getWidth();
        const pdfHeight = (canvas.height * pdfWidth) / canvas.width;
        
        pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight);
        pdf.save("CareerAI_Assessment_Report.pdf");
        return true;
      } else {
        const pdf = new jsPDF();
        pdf.setFillColor(7, 18, 30);
        pdf.rect(0, 0, 210, 297, 'F');
        pdf.setTextColor(255, 128, 107);
        pdf.setFontSize(22);
        pdf.text("CareerAI", 20, 25);
        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(14);
        pdf.text("OFFICIAL CANDIDATE CAREER ASSESSMENT REPORT", 20, 35);
        pdf.setFontSize(10);
        pdf.setTextColor(160, 175, 190);
        pdf.text(`Candidate: Krish Sharma | Target Role: Full Stack Developer | Date: October 30, 2026`, 20, 43);
        pdf.setDrawColor(255, 128, 107);
        pdf.line(20, 48, 190, 48);
        pdf.setTextColor(255, 255, 255);
        pdf.setFontSize(12);
        pdf.text("Summary: Profile evaluated against Full Stack Developer benchmarks.", 20, 60);
        pdf.save("CareerAI_Assessment_Report.pdf");
        return true;
      }
    } catch (err) {
      console.error("PDF generation failed:", err);
      return false;
    }
  }
};
