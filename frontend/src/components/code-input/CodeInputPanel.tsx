/** Code input panel — textarea and input mode toggle with typing placeholder animation. Language is auto-detected. */

import { useEffect, useState } from "react";
import { INPUT_MODES } from "../../lib/constants";
import type { Language } from "../../types";

interface Props {
  code: string;
  setCode: (code: string) => void;
  inputMode: "raw" | "diff";
  setInputMode: (mode: "raw" | "diff") => void;
  language: Language;
  setLanguage: (lang: Language) => void;
}

const PLACEHOLDERS = [
  "Drop your messy code here and let's see how bad it really is...",
  "Paste your script here — don't worry, we won't judge (much)...",
  "Got some questionable code? Dump it right here...",
  "Paste your code here and prepare to get roasted...",
  "Throw your code in here and let the AI find all your bugs...",
];

export default function CodeInputPanel({
  code,
  setCode,
  inputMode,
  setInputMode,
}: Props) {
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const [displayedPlaceholder, setDisplayedPlaceholder] = useState("");
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (code.length > 0) return; // Stop typing animation when user types

    const currentFullText = PLACEHOLDERS[placeholderIndex];
    const typingSpeed = isDeleting ? 25 : 50;

    const timer = setTimeout(() => {
      if (!isDeleting) {
        setDisplayedPlaceholder(currentFullText.substring(0, charIndex + 1));
        setCharIndex(charIndex + 1);
        if (charIndex + 1 === currentFullText.length) {
          setTimeout(() => setIsDeleting(true), 2000); // Wait before deleting
        }
      } else {
        setDisplayedPlaceholder(currentFullText.substring(0, charIndex - 1));
        setCharIndex(charIndex - 1);
        if (charIndex - 1 === 0) {
          setIsDeleting(false);
          setPlaceholderIndex((prev) => (prev + 1) % PLACEHOLDERS.length);
        }
      }
    }, typingSpeed);

    return () => clearTimeout(timer);
  }, [charIndex, isDeleting, placeholderIndex, code]);

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Drop your code below</h2>
        <div className="flex items-center gap-3 text-sm">
          {/* Input mode toggle */}
          <div className="flex rounded-lg bg-zinc-800 p-0.5">
            {INPUT_MODES.map((mode) => (
              <button
                key={mode.value}
                onClick={() => setInputMode(mode.value)}
                className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                  inputMode === mode.value
                    ? "bg-zinc-600 text-zinc-100"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {mode.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="relative">
        <textarea
          value={code}
          onChange={(e) => setCode(e.target.value)}
          placeholder={inputMode === "raw" ? displayedPlaceholder : "Paste your git diff here..."}
          className="w-full border border-zinc-800 rounded-xl p-4
            font-mono text-sm text-zinc-200 placeholder-zinc-500
            focus:outline-none focus:ring-2 focus:ring-zinc-600 focus:border-transparent
            resize-y transition-all duration-200"
          spellCheck={false}
          style={{
            minHeight: code.length > 0 ? '80px' : '64px',
            maxHeight: code.length > 20 ? '200px' : code.length > 50 ? '300px' : '300px',
          }}
        />
        {code.length > 0 && (
          <div className="absolute bottom-2 right-2 text-xs text-zinc-500">
            {code.split('\n').length} lines
          </div>
        )}
      </div>

      <p className="text-xs text-zinc-500">
        {code.length === 0 && "Language is automatically detected"}
      </p>
    </div>
  );
}
