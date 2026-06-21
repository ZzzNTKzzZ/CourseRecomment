import React, { useState } from 'react';
import { TagChip } from '../ui';
import { GraduationCap, Star, ExternalLink, Sparkles, BookmarkPlus, BookmarkCheck, TrendingUp } from 'lucide-react';
import { motion } from 'framer-motion';

// ── Inline star rating (used inside the card) ────────────────────────────────
function InlineStars({ value, onChange }) {
  const [hovered, setHovered] = useState(0);
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map(n => (
        <button
          key={n}
          type="button"
          onClick={(e) => { e.stopPropagation(); onChange(n); }}
          onMouseEnter={() => setHovered(n)}
          onMouseLeave={() => setHovered(0)}
          className="hover:scale-125 transition-transform cursor-pointer"
        >
          <Star
            size={14}
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

// ────────────────────────────────────────────────────────────────────────────

export const CourseCard = ({ course, mode, isEnrolled, userRating, onEnroll, onRate }) => {
  const [localRating, setLocalRating] = useState(userRating || 0);
  const [justEnrolled, setJustEnrolled] = useState(false);

  // Content-based → show cosine score %; User-CF → show predicted rating
  const isUserMode = mode === 'foryou';
  const scoreValue = isUserMode
    ? course.predicted_rating
    : course.score;

  const badgeLabel = isUserMode
    ? `${(scoreValue || 0).toFixed(2)} predicted`
    : `${Math.round((scoreValue || 0) * 100)}% Match`;

  const BadgeIcon = isUserMode ? TrendingUp : Sparkles;

  const handleEnroll = (e) => {
    e.stopPropagation();
    setJustEnrolled(true);
    onEnroll && onEnroll();
  };

  const handleRate = (rating) => {
    setLocalRating(rating);
    onRate && onRate(rating);
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="tonal-card p-6 flex flex-col h-full group cursor-pointer relative overflow-hidden"
    >
      {/* Score Badge */}
      <div className="absolute top-0 right-0 px-3 py-1 bg-primary/10 text-primary font-manrope font-bold text-[10px] uppercase rounded-bl-large flex items-center gap-1">
        <BadgeIcon size={10} />
        <span>{badgeLabel}</span>
      </div>

      {/* Tags Row */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex flex-wrap gap-2">
          <TagChip label={course.level} variant="primary" />
          <TagChip label="Coursera" variant="secondary" />
        </div>
      </div>

      {/* Course Info */}
      <div className="flex-1 space-y-4">
        <div className="space-y-1">
          <div className="flex items-center gap-1.5 text-on-background/40 font-manrope font-bold text-[10px] uppercase tracking-wider">
            <GraduationCap size={12} className="text-secondary" />
            <span>{course.university}</span>
          </div>
          <h3 className="text-xl font-manrope font-extrabold leading-tight text-on-background group-hover:text-primary transition-colors">
            {course.name}
          </h3>
        </div>

        <p className="text-sm font-inter text-on-background/60 line-clamp-3 leading-relaxed">
          {course.description || "No description available for this curated selection."}
        </p>

        {/* Skills */}
        <div className="flex flex-wrap gap-1">
          {course.skills && course.skills.split('  ').slice(0, 3).map((skill, i) => (
            <span key={i} className="text-[10px] bg-surface-container-high px-2 py-0.5 rounded-micro font-medium text-on-surface-variant">
              {skill.trim()}
            </span>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 pt-6 border-t border-outline-variant/10 space-y-4">
        {/* Ratings row */}
        <div className="flex items-center justify-between">
          {/* Course platform rating */}
          <div className="flex items-center gap-1 text-sm font-manrope font-bold text-on-background">
            <Star size={14} className="fill-tertiary text-tertiary" />
            <span>{course.rating}</span>
          </div>

          {/* User personal rating */}
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-manrope font-bold text-on-background/30 uppercase tracking-wider">
              {localRating > 0 ? 'Your rating' : 'Rate it'}
            </span>
            <InlineStars value={localRating} onChange={handleRate} />
          </div>
        </div>

        {/* Actions row */}
        <div className="flex items-center gap-2">
          {/* Enroll / Save button */}
          <button
            onClick={handleEnroll}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-standard text-xs font-manrope font-bold transition-all ${
              isEnrolled || justEnrolled
                ? 'bg-secondary/10 text-secondary'
                : 'bg-surface-container-high text-on-background/60 hover:bg-secondary/10 hover:text-secondary'
            }`}
          >
            {isEnrolled || justEnrolled
              ? <><BookmarkCheck size={13} /> Saved</>
              : <><BookmarkPlus size={13} /> Save</>
            }
          </button>

          {/* View course */}
          <a
            href={course.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-standard bg-primary/5 text-primary text-xs font-manrope font-bold hover:bg-primary hover:text-white transition-all"
            onClick={e => e.stopPropagation()}
          >
            <span>View Course</span>
            <ExternalLink size={14} />
          </a>
        </div>
      </div>
    </motion.div>
  );
};
