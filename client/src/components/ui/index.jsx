import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export const GlassCard = ({ children, className }) => (
  <div className={cn(
    "bg-surface-container-lowest/60 backdrop-blur-xl border border-outline-variant/10 rounded-large",
    className
  )}>
    {children}
  </div>
);

export const TagChip = ({ label, variant = 'secondary' }) => {
  const styles = {
    secondary: "bg-secondary-container/10 text-secondary-on-container",
    primary: "bg-primary-container/10 text-primary-on-container",
    tertiary: "bg-tertiary-container/10 text-tertiary-on-container",
  };
  
  return (
    <span className={cn(
      "px-3 py-1 rounded-full text-xs font-manrope font-semibold tracking-tight uppercase",
      styles[variant]
    )}>
      {label}
    </span>
  );
};
