/** Personality picker — grid of 12 selectable personality cards with random selection and auto-submit. */

import { useState } from "react";
import { PERSONALITY_THEMES, type PersonalityTheme } from "../../lib/constants";

interface Props {
  selected: string | null;
  onSelect: (id: string) => void;
  onRandomSubmit?: (selectedId: string) => void;
  disabled?: boolean;
}

export default function PersonalityPicker({ selected, onSelect, onRandomSubmit, disabled }: Props) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [randomSelected, setRandomSelected] = useState<string | null>(null);
  const [isRandomizing, setIsRandomizing] = useState(false);

  const entries = Object.entries(PERSONALITY_THEMES);

  const handleRandomSelection = () => {
    if (isRandomizing || disabled) return;

    setIsRandomizing(true);
    const duration = 2000; // 2 seconds
    const startTime = Date.now();
    const baseSpeed = 100; // ms per card at start
    const endSpeed = 300;  // ms per card at end

    const cycle = () => {
      const elapsed = Date.now() - startTime;
      const progress = elapsed / duration;

      const easedProgress = 1 - Math.pow(1 - progress, 3);
      const currentSpeed = baseSpeed + (endSpeed - baseSpeed) * easedProgress;

      if (elapsed < duration) {
        const randomIndex = Math.floor(Math.random() * entries.length);
        setRandomSelected(entries[randomIndex][0]);
        setTimeout(cycle, currentSpeed);
      } else {
        const finalIndex = Math.floor(Math.random() * entries.length);
        const finalId = entries[finalIndex][0];
        setRandomSelected(finalId);
        onSelect(finalId);
        setIsRandomizing(false);

        // Automatically trigger roast if callback provided
        if (onRandomSubmit) {
          onRandomSubmit(finalId);
        }
      }
    };

    setTimeout(cycle, baseSpeed);
  };

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">
        Pick your reviewer
      </h2>
      <div className="flex items-center justify-between mb-4">
        <div className="text-sm text-zinc-400">Select a personality or randomize</div>
        <button
          onClick={handleRandomSelection}
          disabled={isRandomizing || disabled}
          className={`px-3.5 py-1.5 rounded-lg border border-luxury-champagne/40 bg-luxury-obsidian hover:bg-luxury-champagne/10 text-luxury-champagne text-xs font-semibold transition-all hover:scale-105 cursor-pointer flex items-center gap-1.5 shadow-sm ${isRandomizing || disabled ? "opacity-50 cursor-not-allowed" : ""}`}
        >
          {isRandomizing ? (
            <span className="inline-block animate-spin">🎲</span>
          ) : (
            <span>🎲</span>
          )}
          <span>{isRandomizing ? "Randomizing..." : "Random & Roast"}</span>
        </button>
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {entries.map(([id, theme], index) => {
          const isHovered = hoveredIndex === index;
          const isRandomSelected = randomSelected === id;
          const isActuallySelected = selected === id;
          return (
            <PersonalityCard
              key={id}
              id={id}
              theme={theme}
              isSelected={isActuallySelected}
              isHovered={isHovered}
              isRandomSelected={isRandomSelected}
              onSelect={onSelect}
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            />
          );
        })}
      </div>
    </div>
  );
}

function PersonalityCard({
  id,
  theme,
  isSelected,
  isHovered,
  isRandomSelected,
  onSelect,
  onMouseEnter,
  onMouseLeave,
}: {
  id: string;
  theme: PersonalityTheme;
  isSelected: boolean;
  isHovered: boolean;
  isRandomSelected: boolean;
  onSelect: (id: string) => void;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}) {
  return (
    <button
      onClick={() => onSelect(id)}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className={`
        relative flex flex-col items-center gap-1.5 p-4 rounded-xl border
        transition-all duration-200 cursor-pointer text-center
        hover:scale-[1.02] active:scale-[0.98]
        ${isRandomSelected
          ? "border-luxury-champagne bg-luxury-champagne/10 shadow-md"
          : isHovered
            ? "border-luxury-champagne/40 bg-luxury-card/80"
            : isSelected
              ? "border-luxury-champagne bg-luxury-card shadow-sm"
              : "border-zinc-800 bg-zinc-900/50 hover:border-zinc-700"
        }
      `}
    >
      <span className="text-2xl">{theme.emoji}</span>
      <span
        className={`text-sm font-medium leading-tight ${
          isSelected || isRandomSelected ? "text-luxury-champagne font-semibold" : isHovered ? "text-luxury-champagne/90" : "text-zinc-300"
        }`}
      >
        {theme.name}
      </span>
      {isRandomSelected && (
        <div className="absolute -top-1 -right-1 w-2 h-2 bg-luxury-champagne rounded-full animate-pulse" />
      )}
    </button>
  );
}