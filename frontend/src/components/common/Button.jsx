import React from 'react';

export const Button = ({
  children,
  variant = 'primary', // primary | secondary | outline | ghost | danger
  size = 'md', // sm | md | lg
  onClick,
  disabled = false,
  loading = false,
  className = '',
  icon: Icon,
  type = 'button',
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-coral/40 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none cursor-pointer';

  const variants = {
    primary: 'bg-coral text-navy-950 font-semibold shadow-glow-coral hover:bg-coral-hover hover:shadow-lg hover:-translate-y-0.5',
    secondary: 'bg-navy-800 text-slate-200 border border-slate-700/60 hover:bg-navy-700 hover:text-white hover:border-coral/40 hover:-translate-y-0.5',
    outline: 'border border-coral/60 text-coral bg-transparent hover:bg-coral/10 hover:border-coral',
    ghost: 'text-slate-300 hover:text-white hover:bg-white/5',
    danger: 'bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:bg-rose-500/30'
  };

  const sizes = {
    sm: 'text-xs px-3 py-1.5 gap-1.5',
    md: 'text-sm px-5 py-2.5 gap-2',
    lg: 'text-base px-6 py-3.5 gap-2.5 font-semibold'
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={`${baseStyles} ${variants[variant] || variants.primary} ${sizes[size]} ${className}`}
      {...props}
    >
      {loading ? (
        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : Icon ? (
        <Icon className={size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
      ) : null}
      {children}
    </button>
  );
};

export const Card = ({
  children,
  className = '',
  hover = true,
  glow = false,
  dark = true,
  ...props
}) => {
  return (
    <div
      className={`rounded-2xl transition-all duration-300 ${
        dark
          ? 'bg-navy-800/80 backdrop-blur-md border border-white/10 text-white'
          : 'bg-white border border-stone-200/80 text-navy-950 shadow-subtle'
      } ${hover ? 'hover:-translate-y-1 hover:border-coral/40 hover:shadow-premium' : ''} ${
        glow ? 'shadow-glow-coral border-coral/30' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
