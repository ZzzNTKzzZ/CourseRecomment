import React, { useState, useCallback, useEffect } from 'react';
import { Navbar } from './components/layout/Navbar';
import { HeroSearch } from './components/search/HeroSearch';
import { CourseCard } from './components/courses/CourseCard';
import { GlassCard } from './components/ui';
import {
  LayoutGrid, List, Sparkles, Filter, ChevronDown,
  Loader2, AlertCircle, User, Users, BookOpen, LogIn,
  TrendingUp, Star, RefreshCw
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// ─── User Login Modal ────────────────────────────────────────────────────────

function LoginModal({ onLogin }) {
  const [name, setName] = useState('');
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-md">
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        className="tonal-card p-10 max-w-md w-full mx-4 space-y-8"
      >
        <div className="text-center space-y-2">
          <div className="w-16 h-16 bg-primary-gradient rounded-full flex items-center justify-center text-white mx-auto shadow-lg">
            <Sparkles size={32} />
          </div>
          <h2 className="font-manrope font-extrabold text-3xl text-on-background">Welcome</h2>
          <p className="text-on-background/50 font-inter text-sm leading-relaxed">
            Enter a username to get <strong className="text-primary">personalised AI recommendations</strong> based on your learning history.
          </p>
        </div>

        <div className="space-y-4">
          <label className="block text-xs font-manrope font-bold uppercase tracking-widest text-on-background/40">
            Your Name / Username
          </label>
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && name.trim() && onLogin(name.trim())}
            placeholder="e.g. alex_dev"
            className="w-full bg-surface-container-low border border-outline-variant/20 rounded-standard px-5 py-3 text-on-background font-inter focus:outline-none focus:border-primary/60 transition-colors placeholder:text-on-background/20"
          />
          <button
            disabled={!name.trim()}
            onClick={() => onLogin(name.trim())}
            className="w-full py-3.5 rounded-standard bg-primary text-white font-manrope font-bold text-sm tracking-wide hover:opacity-90 transition-opacity disabled:opacity-30 flex items-center justify-center gap-2"
          >
            <LogIn size={18} />
            Get Started
          </button>
        </div>
      </motion.div>
    </div>
  );
}

// ─── Mode Tab ────────────────────────────────────────────────────────────────

function ModeTab({ active, onClick, icon: Icon, label, badge }) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-2.5 px-5 py-2.5 rounded-full font-manrope font-bold text-sm transition-all ${
        active
          ? 'bg-primary text-white shadow-md'
          : 'text-on-background/50 hover:text-on-background hover:bg-surface-container-high'
      }`}
    >
      <Icon size={16} />
      <span>{label}</span>
      {badge && (
        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${active ? 'bg-white/20 text-white' : 'bg-primary/10 text-primary'}`}>
          {badge}
        </span>
      )}
    </button>
  );
}

// ─── Star Rating ─────────────────────────────────────────────────────────────

export function StarRating({ value, onChange, readonly = false }) {
  const [hovered, setHovered] = useState(0);
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(n => (
        <button
          key={n}
          type="button"
          disabled={readonly}
          onClick={() => !readonly && onChange && onChange(n)}
          onMouseEnter={() => !readonly && setHovered(n)}
          onMouseLeave={() => !readonly && setHovered(0)}
          className={`transition-transform ${!readonly ? 'hover:scale-110 cursor-pointer' : 'cursor-default'}`}
        >
          <Star
            size={16}
            className={`transition-colors ${
              n <= (hovered || value)
                ? 'fill-tertiary text-tertiary'
                : 'fill-transparent text-on-background/20'
            }`}
          />
        </button>
      ))}
    </div>
  );
}

// ─── App ─────────────────────────────────────────────────────────────────────

function App() {
  const [userId, setUserId] = useState(null);
  const [showLogin, setShowLogin] = useState(true);

  const [mode, setMode] = useState('explore'); // 'explore' | 'foryou'
  const [courses, setCourses] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [viewMode, setViewMode] = useState('grid');
  const [lastQuery, setLastQuery] = useState('');

  const [cfStatus, setCfStatus] = useState(null);    // 'ok' | 'cold_start' | 'popular_fallback'
  const [cfMessage, setCfMessage] = useState('');

  const [userHistory, setUserHistory] = useState([]);// enrolled/rated courses
  const [enrolledSet, setEnrolledSet] = useState(new Set());
  const [userRatings, setUserRatings] = useState({});// courseIdx -> rating

  // ── Login ──
  const handleLogin = (name) => {
    setUserId(name);
    setShowLogin(false);
  };

  // ── Fetch user profile on login ──
  const refreshProfile = useCallback(async (uid) => {
    if (!uid) return;
    try {
      const res = await fetch(`/api/profile?user_id=${encodeURIComponent(uid)}`);
      if (!res.ok) return;
      const data = await res.json();
      setUserHistory(data.history || []);
      const set = new Set(data.history.map(h => h.course_idx));
      setEnrolledSet(set);
      const ratings = {};
      data.history.forEach(h => { if (h.user_rating != null) ratings[h.course_idx] = h.user_rating; });
      setUserRatings(ratings);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { refreshProfile(userId); }, [userId, refreshProfile]);

  // ── Content-based search ──
  const handleSearch = useCallback(async (query) => {
    if (!query.trim()) return;
    setMode('explore');
    setIsLoading(true);
    setError(null);
    setLastQuery(query);

    try {
      const res = await fetch(`/api/recommend?course_name=${encodeURIComponent(query)}`);
      if (!res.ok) {
        if (res.status === 404) throw new Error("Course not found in our database.");
        throw new Error("Failed to fetch recommendations.");
      }
      const data = await res.json();
      setCourses(data.recommendations || []);
      setHasSearched(true);
    } catch (err) {
      setError(err.message);
      setCourses([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ── User-based CF ──
  const handleForYou = useCallback(async () => {
    if (!userId) return;
    setMode('foryou');
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`/api/recommend/user?user_id=${encodeURIComponent(userId)}`);
      if (!res.ok) throw new Error("Failed to fetch personalised recommendations.");
      const data = await res.json();
      setCourses(data.recommendations || []);
      setCfStatus(data.status);
      setCfMessage(data.message || '');
      setHasSearched(true);
    } catch (err) {
      setError(err.message);
      setCourses([]);
    } finally {
      setIsLoading(false);
    }
  }, [userId]);

  // ── Enroll ──
  const handleEnroll = useCallback(async (courseIdx) => {
    if (!userId) return;
    try {
      await fetch('/api/enroll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, course_idx: courseIdx })
      });
      setEnrolledSet(prev => new Set([...prev, courseIdx]));
      await refreshProfile(userId);
    } catch { /* ignore */ }
  }, [userId, refreshProfile]);

  // ── Rate ──
  const handleRate = useCallback(async (courseIdx, rating) => {
    if (!userId) return;
    try {
      await fetch('/api/rate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, course_idx: courseIdx, rating })
      });
      setUserRatings(prev => ({ ...prev, [courseIdx]: rating }));
      setEnrolledSet(prev => new Set([...prev, courseIdx]));
      await refreshProfile(userId);
    } catch { /* ignore */ }
  }, [userId, refreshProfile]);

  return (
    <div className="min-h-screen pb-20 bg-background text-on-background">
      {showLogin && <LoginModal onLogin={handleLogin} />}

      <Navbar userId={userId} enrolledCount={enrolledSet.size} onForYou={handleForYou} />

      <main className="relative">
        {/* Hero + Mode Tabs */}
        <motion.div
          animate={{
            paddingTop: hasSearched ? '2rem' : '10vh',
            paddingBottom: hasSearched ? '1rem' : '4rem'
          }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <HeroSearch onSearch={handleSearch} isCompact={hasSearched} isLoading={isLoading && mode === 'explore'} />

          {/* Mode Tabs (show after first interaction) */}
          {hasSearched && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center justify-center gap-3 mt-6"
            >
              <ModeTab
                active={mode === 'explore'}
                onClick={() => setMode('explore')}
                icon={BookOpen}
                label="Explore"
                badge={mode === 'explore' && courses.length ? courses.length : null}
              />
              <ModeTab
                active={mode === 'foryou'}
                onClick={handleForYou}
                icon={Users}
                label="For You"
                badge={enrolledSet.size > 0 ? `${enrolledSet.size} saved` : null}
              />
            </motion.div>
          )}
        </motion.div>

        <section className="max-w-[1600px] mx-auto px-8">
          <AnimatePresence mode="wait">
            {isLoading && (
              <motion.div
                key="loading"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="py-20 flex flex-col items-center justify-center space-y-4"
              >
                <Loader2 className="w-12 h-12 text-primary animate-spin" />
                <p className="font-manrope font-bold text-primary/60 uppercase tracking-widest text-sm">
                  {mode === 'foryou' ? 'Analysing your learning DNA...' : 'AI is curating your destiny...'}
                </p>
              </motion.div>
            )}

            {error && !isLoading && (
              <motion.div
                key="error"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="py-12 flex flex-col items-center text-center space-y-4"
              >
                <div className="p-4 bg-error-container/10 rounded-full text-error">
                  <AlertCircle size={32} />
                </div>
                <div className="space-y-1">
                  <h3 className="font-manrope font-bold text-xl text-on-background">Curation Interrupted</h3>
                  <p className="text-on-background/60">{error}</p>
                </div>
                <button
                  onClick={() => mode === 'foryou' ? handleForYou() : handleSearch(lastQuery)}
                  className="text-primary font-manrope font-bold hover:underline flex items-center gap-2"
                >
                  <RefreshCw size={14} /> Try again
                </button>
              </motion.div>
            )}

            {hasSearched && !isLoading && !error && (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
              >
                {/* Results Header */}
                <div className="flex items-center justify-between mb-10">
                  <div className="flex items-center gap-6">
                    <div className="space-y-0.5">
                      <h3 className="font-manrope font-extrabold text-2xl text-on-background">
                        {mode === 'foryou' ? (
                          <>
                            <span className="text-primary">Personalised</span> For You
                            <span className="text-on-background/20 font-medium ml-2">({courses.length})</span>
                          </>
                        ) : (
                          <>
                            Top Recommendations
                            <span className="text-on-background/20 font-medium ml-2">({courses.length})</span>
                          </>
                        )}
                      </h3>
                      {mode === 'foryou' && cfStatus === 'cold_start' && (
                        <p className="text-xs text-on-background/40 font-inter">
                          💡 Rate or enroll in courses to unlock collaborative recommendations
                        </p>
                      )}
                      {mode === 'foryou' && cfStatus === 'popular_fallback' && (
                        <p className="text-xs text-secondary/70 font-inter">
                          🔥 Showing trending courses — add more ratings to improve suggestions
                        </p>
                      )}
                    </div>

                    {mode === 'explore' && (
                      <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-surface-container-low text-on-background/60 text-sm font-manrope font-semibold cursor-pointer hover:bg-surface-container-high transition-colors">
                        <Filter size={16} />
                        <span>Similarity Score</span>
                        <ChevronDown size={14} />
                      </div>
                    )}
                  </div>

                  <div className="flex items-center bg-surface-container-low p-1 rounded-standard">
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`p-2 rounded-micro transition-all ${viewMode === 'grid' ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-on-background/40 hover:text-on-background'}`}
                    >
                      <LayoutGrid size={18} />
                    </button>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`p-2 rounded-micro transition-all ${viewMode === 'list' ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-on-background/40 hover:text-on-background'}`}
                    >
                      <List size={18} />
                    </button>
                  </div>
                </div>

                <motion.div
                  layout
                  className={`grid gap-8 ${viewMode === 'grid' ? 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4' : 'grid-cols-1'}`}
                >
                  {courses.map((course, idx) => (
                    <CourseCard
                      key={idx}
                      course={course}
                      mode={mode}
                      isEnrolled={enrolledSet.has(course.course_idx)}
                      userRating={userRatings[course.course_idx] || 0}
                      onEnroll={() => handleEnroll(course.course_idx)}
                      onRate={(r) => handleRate(course.course_idx, r)}
                    />
                  ))}
                </motion.div>
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      </main>

      {/* Floating AI Toast */}
      {hasSearched && (
        <div className="fixed bottom-8 right-8 z-50">
          <GlassCard className="p-4 ambient-shadow flex items-center gap-4 border-primary/20 bg-primary/5">
            <div className="w-10 h-10 bg-primary-gradient rounded-full flex items-center justify-center text-white">
              {mode === 'foryou' ? <TrendingUp size={20} /> : <Sparkles size={20} />}
            </div>
            <div>
              <p className="text-sm font-manrope font-bold text-on-background">
                {mode === 'foryou' ? `Hi, ${userId}!` : 'AI Engine Synced'}
              </p>
              <p className="text-[10px] text-on-background/40 font-manrope font-bold uppercase tracking-wider">
                {mode === 'foryou' ? `${enrolledSet.size} courses tracked` : 'Analysis complete'}
              </p>
            </div>
          </GlassCard>
        </div>
      )}
    </div>
  );
}

export default App;
