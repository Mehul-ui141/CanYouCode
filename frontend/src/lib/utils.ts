/** Utility helpers for the frontend. */

import { PERSONALITY_THEMES } from "./constants";

export function getTheme(personalityId: string) {
  return PERSONALITY_THEMES[personalityId] || PERSONALITY_THEMES.gordon_ramsay;
}

export function formatRelativeTime(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function getShareUrl(token: string): string {
  const origin = typeof window !== "undefined" ? window.location.origin : "";
  return `${origin}/review/share/${token}`;
}

export function copyToClipboard(text: string): Promise<void> {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(text);
  }
  // Fallback for older browsers.
  const textarea = document.createElement("textarea");
  textarea.value = text;
  textarea.style.position = "fixed";
  textarea.style.opacity = "0";
  document.body.appendChild(textarea);
  textarea.select();
  return new Promise((resolve, reject) => {
    try {
      document.execCommand("copy");
      resolve();
    } catch (e) {
      reject(e);
    } finally {
      document.body.removeChild(textarea);
    }
  });
}

export function gradeColor(grade: string): string {
  const letter = grade.charAt(0).toUpperCase();
  const map: Record<string, string> = {
    A: "text-emerald-400",
    B: "text-sky-400",
    C: "text-amber-400",
    D: "text-orange-400",
    F: "text-rose-500",
  };
  return map[letter] || "text-zinc-400";
}
