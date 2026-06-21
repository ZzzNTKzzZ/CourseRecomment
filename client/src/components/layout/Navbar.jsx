import React from 'react';
import { Search, Sparkles, User, GraduationCap, Users, BookmarkCheck } from 'lucide-react';

export const Navbar = ({ userId, enrolledCount = 0, onForYou }) => {
  return (
    <nav className="glass-nav">
      <div className="max-w-[1600px] mx-auto px-8 h-20 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center gap-3 group cursor-pointer">
          <div className="w-10 h-10 bg-primary-gradient rounded-standard flex items-center justify-center text-white shadow-lg transition-transform group-hover:scale-110">
            <GraduationCap size={24} />
          </div>
          <div>
            <h1 className="font-manrope font-extrabold text-xl tracking-tight text-primary">
              STUDIO<span className="text-on-background/40 font-medium">CURATE</span>
            </h1>
            <p className="text-[10px] uppercase tracking-[0.2em] font-manrope font-bold text-secondary/60 -mt-1">
              Course AI Finder
            </p>
          </div>
        </div>

        {/* Nav Links */}
        <div className="hidden md:flex items-center gap-10">
          {['Explore', 'Institutions', 'AI Insights', 'Support'].map((item) => (
            <a
              key={item}
              href="#"
              className="text-sm font-manrope font-semibold text-on-background/60 hover:text-primary transition-colors relative group"
            >
              {item}
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-primary transition-all group-hover:w-full" />
            </a>
          ))}
        </div>

        {/* Right actions */}
        <div className="flex items-center gap-4">
          <button className="p-2 text-on-background/60 hover:text-primary transition-colors">
            <Search size={20} />
          </button>

          <div className="w-px h-6 bg-outline-variant/20 mx-2" />

          {/* For You button — shows enrolled badge */}
          {userId && (
            <button
              onClick={onForYou}
              className="flex items-center gap-2 px-4 py-2 rounded-standard bg-secondary/5 text-secondary text-sm font-manrope font-semibold hover:bg-secondary/10 transition-colors relative"
            >
              <Users size={16} />
              <span>For You</span>
              {enrolledCount > 0 && (
                <span className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-secondary text-white rounded-full text-[10px] font-bold flex items-center justify-center">
                  {enrolledCount}
                </span>
              )}
            </button>
          )}

          <button className="flex items-center gap-2 px-4 py-2 rounded-standard bg-primary/5 text-primary text-sm font-manrope font-semibold hover:bg-primary/10 transition-colors">
            <Sparkles size={16} />
            <span>AI Advisor</span>
          </button>

          {/* User avatar / name */}
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-full bg-primary-gradient flex items-center justify-center text-white font-manrope font-bold text-sm shadow">
              {userId ? userId.charAt(0).toUpperCase() : <User size={18} />}
            </div>
            {userId && (
              <span className="hidden lg:block text-sm font-manrope font-semibold text-on-background/70">
                {userId}
              </span>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};
