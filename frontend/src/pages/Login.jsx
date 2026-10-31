import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Lock, ArrowRight, Sparkles, CheckCircle2, Bot } from 'lucide-react';
import { Button } from '../components/common/Button';
import { authService } from '../utils/apiService';

export const Login = ({ navigate, onLoginSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setError('Please provide your email address and password.');
      return;
    }
    setIsLoading(true);
    setError('');

    try {
      const res = await authService.login(email, password);
      if (res.success) {
        if (onLoginSuccess) onLoginSuccess(res.user);
        navigate('dashboard');
      } else {
        setError(res.error || 'Invalid email or password. Please verify your credentials.');
      }
    } catch (err) {
      setError(err.message || 'Authentication error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await authService.signInWithGoogle();
      if (!res.success && res.error) {
        setError(res.error);
      }
    } catch (err) {
      setError(err.message || 'Failed to authenticate with Google.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-navy-900 flex flex-col justify-center items-center px-4 py-12 relative overflow-hidden bg-grid-pattern">
      {/* Background Orbs */}
      <div className="absolute top-1/4 left-1/4 w-80 h-80 bg-coral/15 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-sky-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Brand Header */}
      <div 
        onClick={() => navigate('landing')}
        className="flex items-center gap-3 mb-8 cursor-pointer group"
      >
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-coral to-amber-400 p-[2px] shadow-glow-coral group-hover:scale-105 transition-transform">
          <div className="w-full h-full bg-navy-900 rounded-[10px] flex items-center justify-center">
            <div className="w-4 h-4 border-2 border-coral rounded-sm rotate-45 flex items-center justify-center">
              <div className="w-1.5 h-1.5 bg-coral rounded-full" />
            </div>
          </div>
        </div>
        <span className="text-2xl font-bold font-serif tracking-tight text-white">
          Career<span className="text-coral">AI</span>
        </span>
      </div>

      {/* Card Container */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md bg-navy-800/90 backdrop-blur-xl border border-slate-700/80 rounded-3xl p-8 shadow-2xl relative z-10"
      >
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold font-serif text-white">Welcome Back</h2>
          <p className="text-xs text-slate-400 mt-1">
            Access your career roadmap, interview simulator, and skill reports.
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-navy-950 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-coral transition-colors"
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="block text-xs font-medium text-slate-300">
                Password
              </label>
              <a href="#" className="text-[11px] text-coral hover:underline">
                Forgot password?
              </a>
            </div>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-navy-950 border border-slate-700 rounded-xl py-3 pl-10 pr-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-coral transition-colors"
              />
            </div>
          </div>

          <Button
            type="submit"
            size="lg"
            loading={isLoading}
            className="w-full shadow-glow-coral text-navy-950 font-bold mt-2"
          >
            Sign In to Dashboard <ArrowRight className="w-4 h-4 ml-1" />
          </Button>
        </form>

        <div className="relative my-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-white/10" />
          </div>
          <div className="relative flex justify-center text-xs">
            <span className="bg-navy-800 px-3 text-slate-400">or continue with</span>
          </div>
        </div>

        {/* Continue with Google */}
        <button
          type="button"
          onClick={handleGoogleLogin}
          className="w-full flex items-center justify-center gap-3 py-3 px-4 rounded-xl border border-slate-700 bg-navy-950 hover:bg-white/5 text-slate-200 text-sm font-medium transition-colors cursor-pointer"
        >
          <svg className="w-4 h-4" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="#34A853"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="#FBBC05"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
            />
            <path
              fill="#EA4335"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
            />
          </svg>
          Continue with Google
        </button>

        <p className="text-center text-xs text-slate-400 mt-6">
          Don't have an account yet?{' '}
          <button
            onClick={() => navigate('signup')}
            className="text-coral font-semibold hover:underline cursor-pointer"
          >
            Create Free Account
          </button>
        </p>
      </motion.div>
    </div>
  );
};
