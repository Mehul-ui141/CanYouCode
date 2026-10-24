/**
 * HomePage — the main page that ties everything together:
 * 1. Code input panel (paste code, pick mode/language)
 * 2. Personality picker (12 cards)
 * 3. Submit button
 * 4. Review display (streaming results)
 */

import { useEffect, useRef, useState } from "react";
import Container from "../components/layout/Container";
import CodeInputPanel from "../components/code-input/CodeInputPanel";
import PersonalityPicker from "../components/personality/PersonalityPicker";
import ReviewDisplay from "../components/review/ReviewDisplay";
import Spinner from "../components/ui/Spinner";
import { useStreamingReview } from "../hooks/useStreamingReview";
import { useReviewHistory } from "../hooks/useReviewHistory";
import { PERSONALITY_THEMES } from "../lib/constants";
import type { Language } from "../types";

export default function HomePage() {
  const [code, setCode] = useState("");
  const [inputMode, setInputMode] = useState<"raw" | "diff">("raw");
  const [language, setLanguage] = useState<Language>("python");
  const [personality, setPersonality] = useState<string | null>(null);

  const { state, submit, reset } = useStreamingReview();
  const { addEntry } = useReviewHistory();

  const canSubmit =
    code.trim().length > 0 &&
    personality !== null &&
    state.status !== "analyzing" &&
    state.status !== "streaming";

  const handleSubmit = async (targetPersonality?: string) => {
    const activePersonality = targetPersonality || personality;
    if (!activePersonality || !code.trim()) return;

    await submit({
      code,
      input_mode: inputMode,
      language,
      personality_id: activePersonality,
    });
  };

  const handleRandomSubmit = async (chosenPersonality: string) => {
    setPersonality(chosenPersonality);
    if (!code.trim()) return;
    await submit({
      code,
      input_mode: inputMode,
      language,
      personality_id: chosenPersonality,
    });
  };

  // Once a review completes, save it to localStorage history.
  const savedReviewRef = useRef<string | null>(null);
  useEffect(() => {
    if (state.status === "complete" && state.reviewId && state.reviewId !== savedReviewRef.current) {
      savedReviewRef.current = state.reviewId;
      addEntry({
        id: state.reviewId,
        personalityId: personality!,
        language,
        codePreview: code.slice(0, 80),
        createdAt: new Date().toISOString(),
      });
    }
  }, [state.status, state.reviewId]);

  const theme = personality
    ? PERSONALITY_THEMES[personality]
    : null;

  const isActive = state.status === "analyzing" || state.status === "streaming";

  return (
    <Container>
      <div className="space-y-10">
        {/* Hero */}
        <div className="text-center space-y-2 pt-4">
          <h1 className="text-4xl sm:text-5xl font-black tracking-tight">
            <span className="text-zinc-100">Can You</span>
            <span className="text-luxury-champagne">Code</span>
          </h1>
          <p className="text-zinc-400 text-lg max-w-xl mx-auto">
            Paste your code. Pick a personality. Get roasted{" "}
            <span className="text-zinc-500">(or cheered on)</span> by AI.
          </p>
        </div>

        {/* Code input */}
        <CodeInputPanel
          code={code}
          setCode={setCode}
          inputMode={inputMode}
          setInputMode={setInputMode}
          language={language}
          setLanguage={setLanguage}
        />

        {/* Personality picker */}
        <PersonalityPicker
          selected={personality}
          onSelect={setPersonality}
          onRandomSubmit={handleRandomSubmit}
          disabled={isActive}
        />

        {/* Submit button */}
        <div className="flex justify-center">
          <button
            onClick={() => handleSubmit()}
            disabled={!canSubmit}
            className={`
              px-8 py-3 rounded-xl text-base font-bold transition-all duration-200
              disabled:opacity-40 disabled:cursor-not-allowed
              ${
                theme
                  ? `${theme.button} text-white shadow-lg`
                  : "bg-red-600 hover:bg-red-700 text-white"
              }
              ${canSubmit ? "hover:scale-[1.03] active:scale-[0.98]" : ""}
            `}
          >
            {isActive ? (
              <span className="flex items-center gap-2">
                <Spinner />
                {state.status === "analyzing"
                  ? "Analyzing..."
                  : "Generating review..."}
              </span>
            ) : (
              <span>
                {personality === "encouraging_mentor"
                  ? "✨ Review My Code"
                  : "🔥 Roast My Code"}
              </span>
            )}
          </button>
        </div>

        {/* New review button (when complete) */}
        {state.status === "complete" && (
          <div className="flex justify-center">
            <button
              onClick={() => {
                reset();
                setCode("");
                setPersonality(null);
              }}
              className="text-sm text-zinc-400 hover:text-zinc-200 underline underline-offset-4 transition-colors"
            >
              Start a new review
            </button>
          </div>
        )}

        {/* Error */}
        {state.status === "error" && (
          <div className="rounded-xl border border-rose-800 bg-rose-950/20 p-4 text-rose-300 text-sm">
            <p className="font-medium">Something went wrong</p>
            <p className="text-rose-400 mt-1">{state.error}</p>
            <button
              onClick={reset}
              className="mt-2 text-xs text-rose-500 hover:text-rose-300 underline"
            >
              Try again
            </button>
          </div>
        )}

        {/* Review display */}
        {(state.status === "streaming" || state.status === "complete") &&
          personality && (
            <ReviewDisplay
              personalityId={personality}
              findings={state.findings}
              aiText={state.aiText}
              isStreaming={state.status === "streaming"}
              reviewId={state.reviewId}
              shareToken={state.shareToken}
              stats={state.stats}
            />
          )}
      </div>
    </Container>
  );
}
