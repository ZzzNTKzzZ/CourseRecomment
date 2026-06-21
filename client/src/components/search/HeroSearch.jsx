

import React, { useState } from 'react';
import { Search, Sparkles, Wand2, Loader2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const HeroSearch = ({ onSearch, isCompact, isLoading }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    onSearch(query);
  };

  return (
    <section className="relative px-8 flex flex-col items-center">
      <div className="max-w-4xl w-full text-center space-y-6">
        <AnimatePresence>
          {!isCompact && (
            <motion.div 
              initial={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0, marginBottom: 0 }}
              className="space-y-4 overflow-hidden"
            >
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-tertiary-container/10 text-tertiary font-manrope font-bold text-[10px] uppercase tracking-widest">
                <Sparkles size={12} />
                <span>AI-Powered Discovery</span>
              </div>
              <h2 className="text-6xl md:text-7xl font-manrope font-extrabold tracking-tight text-on-background leading-[1.1]">
                Find your <span className="text-primary italic">academic</span> destiny.
              </h2>
              <p className="text-lg text-on-background/60 font-inter max-w-2xl mx-auto">
                Beyond the database. Our AI understands your aspirations to curate a bespoke educational path from global prestige institutions.
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        <motion.div 
          layout
          className="relative group max-w-2xl mx-auto"
        >
          <div className="absolute inset-0 bg-primary/5 rounded-2xl blur-xl group-focus-within:bg-primary/10 transition-all duration-500" />
          <form 
            onSubmit={handleSubmit}
            className="relative flex items-center bg-surface-container-lowest rounded-2xl ambient-shadow p-2 focus-glow"
          >
            <div className="pl-4 text-on-background/40">
              <Search size={22} />
            </div>
            <input 
              type="text" 
              value={query}
              disabled={isLoading}
              placeholder={isCompact ? "Search for another course..." : "What do you want to master today?"}
              className="flex-1 bg-transparent border-none py-4 px-4 text-xl font-manrope font-semibold text-on-background placeholder:text-on-background/30 focus:outline-none disabled:opacity-50"
              onChange={(e) => setQuery(e.target.value)}
            />
            <button 
              type="submit"
              disabled={isLoading || !query.trim()}
              className="bg-primary-gradient text-white px-8 py-4 rounded-xl font-manrope font-bold flex items-center gap-2 group/btn active:scale-95 transition-transform disabled:opacity-50 disabled:grayscale"
            >
              {isLoading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Wand2 size={20} className="group-hover/btn:rotate-12 transition-transform" />
              )}
              <span>{isCompact ? 'Search' : 'Curate'}</span>
            </button>
          </form>
        </motion.div>

        {!isCompact && (
          <motion.div 
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex flex-wrap items-center justify-center gap-3 pt-4"
          >
            <span className="text-sm font-manrope font-bold text-on-background/40 uppercase tracking-tighter mr-2">Propelling:</span>
            {['Finance', 'Python', 'React', 'Java'].map((tag) => (
              <button 
                key={tag} 
                onClick={() => { setQuery(tag); onSearch(tag); }}
                className="px-4 py-2 rounded-full bg-surface-container-low text-on-background/60 text-sm font-manrope font-semibold hover:bg-primary/10 hover:text-primary transition-all"
              >
                {tag}
              </button>
            ))}
          </motion.div>
        )}
      </div>
    </section>
  );
};
