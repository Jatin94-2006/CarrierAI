import React, { useState } from 'react';
import { 
  FileText, 
  LayoutDashboard, 
  Bell, 
  User, 
  Settings, 
  LogOut, 
  Menu, 
  X, 
  ChevronRight,
  ShieldCheck,
  Check,
  RotateCcw
} from 'lucide-react';

export const Navbar = ({ 
  currentPath = 'dashboard', 
  navigate, 
  user = { name: "Candidate", role: "Software Engineer" },
  showNotificationToast,
  onResetProfile,
  onLogout
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userDropdownOpen, setUserDropdownOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);

  // STRICT REQUIREMENT: Only Dashboard and Resume Analysis in main nav
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'resume-analysis', label: 'Resume Analysis', icon: FileText }
  ];

  const notifications = [
    { id: 1, title: "Resume analysis algorithm updated", time: "10m ago" },
    { id: 2, title: "Full Stack Developer requirements refreshed", time: "1h ago" },
    { id: 3, title: "Mock interview evaluation system online", time: "Yesterday" }
  ];

  return (
    <nav className="sticky top-0 z-40 w-full bg-[#07121e]/95 backdrop-blur-md border-b border-white/10 transition-all select-none">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          
          {/* Left: Brand Logo (No emojis, Lucide/CSS diamond shape) */}
          <div 
            onClick={() => navigate('dashboard')}
            className="flex items-center gap-3 cursor-pointer group"
          >
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-coral to-amber-400 p-[2px] shadow-glow-coral group-hover:scale-105 transition-transform duration-300">
              <div className="w-full h-full bg-[#07121e] rounded-[10px] flex items-center justify-center">
                <div className="w-4 h-4 border-2 border-coral rounded-sm rotate-45 flex items-center justify-center">
                  <div className="w-1.5 h-1.5 bg-coral rounded-full" />
                </div>
              </div>
            </div>
            <div>
              <span className="text-xl sm:text-2xl font-bold font-serif tracking-tight text-white">
                Career<span className="text-coral">AI</span>
              </span>
              <p className="text-[10px] text-slate-400 tracking-tight hidden sm:block">From Resume to Job-Ready.</p>
            </div>
          </div>

          {/* Center Navigation Links: ONLY Dashboard and Resume Analysis */}
          <div className="hidden md:flex items-center gap-1.5 bg-[#0b1928]/80 p-1.5 rounded-2xl border border-white/5">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPath === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => navigate(item.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-medium transition-all duration-200 cursor-pointer ${
                    isActive
                      ? 'bg-coral text-navy-950 font-semibold shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-navy-950' : 'text-slate-400'}`} />
                  {item.label}
                </button>
              );
            })}
          </div>

          {/* Right Controls: Notifications, User Profile, Settings */}
          <div className="flex items-center gap-2.5 sm:gap-3">
            
            {/* Notifications Button */}
            <div className="relative">
              <button
                onClick={() => {
                  setNotificationsOpen(!notificationsOpen);
                  setUserDropdownOpen(false);
                  setSettingsOpen(false);
                }}
                className="relative p-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 border border-transparent hover:border-white/10 transition-colors cursor-pointer"
                aria-label="Notifications"
              >
                <Bell className="w-4 h-4 sm:w-5 sm:h-5" />
                <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-coral" />
              </button>

              {/* Notification Popover */}
              {notificationsOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-[#0b1928] border border-slate-700/80 rounded-2xl shadow-2xl p-4 z-50 animate-in fade-in zoom-in-95 duration-150">
                  <div className="flex items-center justify-between pb-3 border-b border-white/10">
                    <span className="text-xs font-semibold text-white uppercase tracking-wider">System Notifications</span>
                    <span className="text-[10px] text-coral bg-coral/10 px-2 py-0.5 rounded-full font-mono">Live</span>
                  </div>
                  <div className="divide-y divide-white/5 mt-2">
                    {notifications.map((n) => (
                      <div key={n.id} className="py-2.5 px-2 hover:bg-white/5 rounded-lg transition-colors cursor-pointer">
                        <p className="text-xs font-medium text-slate-200">{n.title}</p>
                        <span className="text-[10px] text-slate-500">{n.time}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Settings Button */}
            <div className="relative">
              <button
                onClick={() => {
                  setSettingsOpen(!settingsOpen);
                  setNotificationsOpen(false);
                  setUserDropdownOpen(false);
                }}
                className="p-2.5 rounded-xl text-slate-400 hover:text-white hover:bg-white/5 border border-transparent hover:border-white/10 transition-colors cursor-pointer"
                aria-label="Settings"
              >
                <Settings className="w-4 h-4 sm:w-5 sm:h-5" />
              </button>

              {settingsOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-[#0b1928] border border-slate-700/80 rounded-2xl shadow-2xl p-3 z-50 text-xs text-slate-300 space-y-2">
                  <div className="px-2 py-1 font-semibold text-white border-b border-white/10 pb-2">
                    Platform Preferences
                  </div>
                  <div className="p-2 rounded-xl bg-navy-950 flex items-center justify-between">
                    <span>AI Model Engine</span>
                    <span className="font-mono text-coral font-bold">FastAPI v2</span>
                  </div>
                  <div className="p-2 rounded-xl bg-navy-950 flex items-center justify-between">
                    <span>Audio / Video Feed</span>
                    <span className="text-emerald-400">Calibrated</span>
                  </div>
                </div>
              )}
            </div>

            {/* Profile Menu */}
            <div className="relative">
              <button
                onClick={() => {
                  setUserDropdownOpen(!userDropdownOpen);
                  setNotificationsOpen(false);
                  setSettingsOpen(false);
                }}
                className="flex items-center gap-2 p-1.5 pr-2.5 sm:pr-3 rounded-2xl bg-[#0b1928] border border-white/10 hover:border-coral/30 transition-all cursor-pointer"
              >
                <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-xl bg-gradient-to-tr from-coral to-amber-500 flex items-center justify-center font-bold text-navy-950 text-xs shadow-sm">
                  KS
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-xs font-semibold text-white leading-tight">{user.name}</p>
                  <p className="text-[10px] text-coral font-medium leading-none">Full Stack Track</p>
                </div>
              </button>

              {/* User Dropdown */}
              {userDropdownOpen && (
                <div className="absolute right-0 mt-2 w-56 bg-[#0b1928] border border-slate-700/80 rounded-2xl shadow-2xl p-2 z-50">
                  <div className="px-3 py-2 border-b border-white/10">
                    <p className="text-xs font-semibold text-white">{user.name}</p>
                    <p className="text-[10px] text-slate-400 truncate">{user.email || 'candidate@example.com'}</p>
                  </div>
                  <div className="py-1">
                    <button
                      onClick={() => { navigate('dashboard'); setUserDropdownOpen(false); }}
                      className="w-full text-left px-3 py-2 text-xs text-slate-300 hover:text-white hover:bg-white/5 rounded-xl flex items-center gap-2"
                    >
                      <User className="w-3.5 h-3.5 text-slate-400" /> Candidate Profile
                    </button>
                    <button
                      onClick={() => { navigate('resume-analysis'); setUserDropdownOpen(false); }}
                      className="w-full text-left px-3 py-2 text-xs text-slate-300 hover:text-white hover:bg-white/5 rounded-xl flex items-center gap-2"
                    >
                      <FileText className="w-3.5 h-3.5 text-coral" /> Run Resume Analysis
                    </button>
                    {onResetProfile && (
                      <button
                        onClick={() => { onResetProfile(); setUserDropdownOpen(false); }}
                        className="w-full text-left px-3 py-2 text-xs text-amber-400 hover:bg-amber-500/10 rounded-xl flex items-center gap-2"
                        title="Clear local assessment history and start as a fresh user"
                      >
                        <RotateCcw className="w-3.5 h-3.5 text-amber-400" /> Start Fresh Assessment
                      </button>
                    )}
                    <button
                      onClick={async () => {
                        if (onLogout) await onLogout();
                        else navigate('landing');
                        setUserDropdownOpen(false);
                      }}
                      className="w-full text-left px-3 py-2 text-xs text-rose-400 hover:bg-rose-500/10 rounded-xl flex items-center gap-2 cursor-pointer"
                    >
                      <LogOut className="w-3.5 h-3.5" /> Sign Out
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Mobile Hamburger Toggle */}
            <div className="md:hidden">
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/5 border border-white/10"
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>

          </div>
        </div>
      </div>

      {/* Mobile Drawer Navigation: ONLY Dashboard & Resume Analysis */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-[#07121e] border-b border-white/10 px-4 pt-3 pb-6 space-y-2 animate-in slide-in-from-top-4 duration-200">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  navigate(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-coral text-navy-950 font-semibold'
                    : 'text-slate-300 hover:bg-white/5'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </div>
                <ChevronRight className="w-4 h-4 opacity-50" />
              </button>
            );
          })}
        </div>
      )}
    </nav>
  );
};
