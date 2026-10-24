/** UI constants: severity levels, input modes, and personality color themes. */

import { Language, Severity } from "@/types";

export const SEVERITY_ORDER: Severity[] = ["critical", "warning", "info", "nitpick"];

export const SEVERITY_CONFIG: Record<
  Severity,
  { label: string; tailwind: string; text: string; bg: string }
> = {
  critical: {
    label: "Critical",
    tailwind: "critical",
    text: "text-rose-400",
    bg: "bg-rose-500/10",
  },
  warning: {
    label: "Warning",
    tailwind: "warning",
    text: "text-amber-400",
    bg: "bg-amber-500/10",
  },
  info: {
    label: "Info",
    tailwind: "info",
    text: "text-sky-400",
    bg: "bg-sky-500/10",
  },
  nitpick: {
    label: "Nitpick",
    tailwind: "nitpick",
    text: "text-violet-400",
    bg: "bg-violet-500/10",
  },
};

export const SEVERITY_ICONS: Record<Severity, string> = {
  critical: "🔥",
  warning: "⚠️",
  info: "ℹ️",
  nitpick: "🔍",
};

export const INPUT_MODES: { value: "raw" | "diff"; label: string }[] = [
  { value: "raw", label: "Raw Code" },
  { value: "diff", label: "Diff (git-style)" },
];

export const LANGUAGES: { value: Language; label: string }[] = [
  { value: "python", label: "Python" },
  { value: "java", label: "Java" },
  { value: "c", label: "C" },
  { value: "cpp", label: "C++" },
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
];

/** Personality-to-Tailwind theme mapping. Colors match the backend personalities. */
export const PERSONALITY_THEMES: Record<string, PersonalityTheme> = {
  brutal_senior: {
    name: "Brutal Senior Engineer",
    emoji: "💀",
    color: "#DC2626",
    accent: "text-luxury-champagne",
    border: "border-luxury-champagne/30",
    bg: "bg-luxury-obsidian/20",
    gradient: "from-luxury-champagne/20 to-luxury-obsidian",
    badge: "bg-luxury-champagne/20 text-luxury-champagne",
    button: "bg-luxury-champagne hover:bg-luxury-champagne-hover text-luxury-obsidian",
  },
  passive_aggressive: {
    name: "Passive-Aggressive Tech Lead",
    emoji: "🙄",
    color: "#7C3AED",
    accent: "text-indigo-400",
    border: "border-indigo-700",
    bg: "bg-indigo-950/20",
    gradient: "from-indigo-900/20 to-luxury-obsidian",
    badge: "bg-indigo-900/40 text-indigo-200",
    button: "bg-indigo-600 hover:bg-indigo-700",
  },
  chaos_goblin: {
    name: "Chaos Goblin Intern",
    emoji: "👺",
    color: "#F59E0B",
    accent: "text-amber-400",
    border: "border-amber-700",
    bg: "bg-amber-950/20",
    gradient: "from-amber-900/20 to-luxury-obsidian",
    badge: "bg-amber-900/40 text-amber-200",
    button: "bg-amber-600 hover:bg-amber-700",
  },
  encouraging_mentor: {
    name: "Encouraging Mentor",
    emoji: "🌟",
    color: "#10B981",
    accent: "text-emerald-400",
    border: "border-emerald-700",
    bg: "bg-emerald-950/20",
    gradient: "from-emerald-900/20 to-luxury-obsidian",
    badge: "bg-emerald-900/40 text-emerald-200",
    button: "bg-emerald-600 hover:bg-emerald-700",
  },
  patient_professor: {
    name: "Patient Professor",
    emoji: "👓",
    color: "#3B82F6",
    accent: "text-sky-400",
    border: "border-sky-700",
    bg: "bg-sky-950/20",
    gradient: "from-sky-900/20 to-luxury-obsidian",
    badge: "bg-sky-900/40 text-sky-200",
    button: "bg-sky-600 hover:bg-sky-700",
  },
  security_paranoid: {
    name: "Security Paranoid",
    emoji: "🔒",
    color: "#EF4444",
    accent: "text-rose-400",
    border: "border-rose-700",
    bg: "bg-rose-950/20",
    gradient: "from-rose-900/20 to-luxury-obsidian",
    badge: "bg-rose-900/40 text-rose-200",
    button: "bg-rose-600 hover:bg-rose-700",
  },
  overengineering_architect: {
    name: "Over-Engineering Architect",
    emoji: "🏗️",
    color: "#6366F1",
    accent: "text-indigo-400",
    border: "border-indigo-700",
    bg: "bg-indigo-950/20",
    gradient: "from-indigo-900/20 to-luxury-obsidian",
    badge: "bg-indigo-900/40 text-indigo-200",
    button: "bg-indigo-600 hover:bg-indigo-700",
  },
  lgtm_speedrunner: {
    name: "LGTM Speedrunner",
    emoji: "⚡",
    color: "#22C55E",
    accent: "text-green-400",
    border: "border-green-700",
    bg: "bg-green-950/20",
    gradient: "from-green-900/20 to-luxury-obsidian",
    badge: "bg-green-900/40 text-green-200",
    button: "bg-green-600 hover:bg-green-700",
  },
  nitpick_perfectionist: {
    name: "Nitpick Perfectionist",
    emoji: "🔍",
    color: "#EC4899",
    accent: "text-pink-400",
    border: "border-pink-700",
    bg: "bg-pink-950/20",
    gradient: "from-pink-900/20 to-luxury-obsidian",
    badge: "bg-pink-900/40 text-pink-200",
    button: "bg-pink-600 hover:bg-pink-700",
  },
  existential_philosopher: {
    name: "Existential Philosopher",
    emoji: "🤔",
    color: "#8B5CF6",
    accent: "text-violet-400",
    border: "border-violet-700",
    bg: "bg-violet-950/20",
    gradient: "from-violet-900/20 to-luxury-obsidian",
    badge: "bg-violet-900/40 text-violet-200",
    button: "bg-violet-600 hover:bg-violet-700",
  },
  stackoverflow_warrior: {
    name: "Stack Overflow Warrior",
    emoji: "📜",
    color: "#F97316",
    accent: "text-orange-400",
    border: "border-orange-700",
    bg: "bg-orange-950/20",
    gradient: "from-orange-900/20 to-luxury-obsidian",
    badge: "bg-orange-900/40 text-orange-200",
    button: "bg-orange-600 hover:bg-orange-700",
  },
  gordon_ramsay: {
    name: "Gordon Ramsay But For Code",
    emoji: "👨‍🍳",
    color: "#B91C1C",
    accent: "text-red-600",
    border: "border-red-800",
    bg: "bg-red-950/20",
    gradient: "from-red-950/20 to-luxury-obsidian",
    badge: "bg-red-950/60 text-red-100",
    button: "bg-red-700 hover:bg-red-800",
  },
};

export interface PersonalityTheme {
  name: string;
  emoji: string;
  color: string;
  accent: string;
  border: string;
  bg: string;
  gradient: string;
  badge: string;
  button: string;
}
