/** ReviewDisplay — renders the full review: summary, opening, findings, closing. */

import { useMemo } from "react";
import { PERSONALITY_THEMES, SEVERITY_CONFIG } from "../../lib/constants";
import type { AiReview, Finding, PersonFinding } from "../../types";
import FindingCard from "./FindingCard";
import StreamingText from "./StreamingText";
import ShareButton from "./ShareButton";

interface Props {
  personalityId: string;
  findings: Finding[];
  aiText: string;
  isStreaming: boolean;
  reviewId: string | null;
  shareToken: string | null;
  stats: Record<string, number> | null;
}

export default function ReviewDisplay({
  personalityId,
  findings,
  aiText,
  isStreaming,
  shareToken,
  stats,
}: Props) {
  const theme = PERSONALITY_THEMES[personalityId] || PERSONALITY_THEMES.gordon_ramsay;

  // Try to parse the AI text as structured JSON once streaming is complete.
  const parsed: AiReview | null = useMemo(() => {
    if (isStreaming || !aiText) return null;
    try {
      const cleaned = aiText.replace(/^```(?:json)?\n?|\n?```$/gm, "").trim();
      return JSON.parse(cleaned);
    } catch {
      return null;
    }
  }, [aiText, isStreaming]);

  // Map AI findings by id for quick lookup.
  const aiFindings: Record<string, PersonFinding> = useMemo(() => {
    if (!parsed?.findings) return {};
    const map: Record<string, PersonFinding> = {};
    for (const f of parsed.findings) {
      map[f.id] = f;
    }
    return map;
  }, [parsed]);

  const displayStats = stats || {};

  return (
    <div
      className={`space-y-6 rounded-2xl border ${theme.border} ${theme.bg} p-6 bg-gradient-to-br ${theme.gradient}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-3xl">{theme.emoji}</span>
          <div>
            <h3 className={`text-lg font-bold ${theme.accent}`}>
              {theme.name}
            </h3>
            <p className="text-xs text-zinc-500">
              {findings.length} findings &bull;{" "}
              {Object.entries(displayStats)
                .filter(([_, count]) => count > 0)
                .map(([sev, count]) => `${count} ${sev}`)
                .join(", ") || "analyzing..."}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Grade */}
          {parsed?.overall_grade && (
            <div className="text-center">
              <div className="text-3xl font-black text-zinc-200">
                {parsed.overall_grade.charAt(0)}
              </div>
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider">
                Grade
              </div>
            </div>
          )}

          {shareToken && <ShareButton shareToken={shareToken} />}
        </div>
      </div>

      {/* Stats bar */}
      {Object.keys(displayStats).length > 0 && (
        <div className="flex gap-3">
          {(["critical", "warning", "info", "nitpick"] as const).map((sev) => {
            const count = displayStats[sev] || 0;
            if (count === 0) return null;
            const config = SEVERITY_CONFIG[sev];
            return (
              <div
                key={sev}
                className={`flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium ${config.bg} ${config.text}`}
              >
                {count} {config.label}
              </div>
            );
          })}
        </div>
      )}

      {/* Opening statement */}
      {parsed?.opening && (
        <blockquote
          className={`border-l-4 ${theme.border} pl-4 py-2 text-sm italic text-zinc-300`}
        >
          {parsed.opening}
        </blockquote>
      )}

      {/* Streaming text (while still typing) */}
      {isStreaming && (
        <StreamingText
          text={aiText}
          isStreaming={isStreaming}
          className="text-sm text-zinc-300 font-mono bg-zinc-900/50 rounded-lg p-4"
        />
      )}

      {/* Findings */}
      {findings.length > 0 && (
        <div className="space-y-3">
          {findings.map((f) => (
            <FindingCard
              key={f.id}
              finding={f}
              aiComment={aiFindings[f.id]?.comment}
              severityReaction={aiFindings[f.id]?.severity_reaction}
            />
          ))}
        </div>
      )}

      {/* Closing statement */}
      {parsed?.closing && (
        <blockquote
          className={`border-l-4 ${theme.border} pl-4 py-2 text-sm italic text-zinc-400`}
        >
          {parsed.closing}
        </blockquote>
      )}

      {/* Overall grade justification */}
      {parsed?.overall_grade && parsed.overall_grade.length > 1 && (
        <div className="text-center pt-2 border-t border-zinc-800">
          <p className={`text-sm font-medium ${theme.accent}`}>
            {parsed.overall_grade}
          </p>
        </div>
      )}
    </div>
  );
}
