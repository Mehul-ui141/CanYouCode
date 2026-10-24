/** Finding card — displays a single finding with severity, code, and AI commentary. */

import SeverityBadge from "./SeverityBadge";
import type { Finding } from "../../types";

interface Props {
  finding: Finding;
  aiComment?: string;
  severityReaction?: string;
}

export default function FindingCard({ finding, aiComment, severityReaction }: Props) {
  return (
    <div className="border border-zinc-800 rounded-xl overflow-hidden bg-zinc-900/50">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2.5 border-b border-zinc-800 bg-zinc-900/80">
        <div className="flex items-center gap-2">
          <SeverityBadge severity={finding.severity} />
          <span className="text-xs text-zinc-500 font-mono">{finding.rule}</span>
          {finding.line_start && (
            <span className="text-xs text-zinc-600">
              Line {finding.line_start}
              {finding.line_end && finding.line_end !== finding.line_start
                ? `–${finding.line_end}`
                : ""}
            </span>
          )}
        </div>
        {severityReaction && (
          <span className="text-xs text-zinc-400 italic">{severityReaction}</span>
        )}
      </div>

      {/* Code snippet */}
      {finding.code_snippet && (
        <pre className="px-4 py-2 text-xs font-mono text-zinc-300 bg-zinc-950/50 border-b border-zinc-800 overflow-x-auto">
          {finding.code_snippet}
        </pre>
      )}

      {/* AI commentary or original message */}
      <div className="px-4 py-3 space-y-2">
        {aiComment ? (
          <p className="text-sm text-zinc-200 leading-relaxed">{aiComment}</p>
        ) : (
          <p className="text-sm text-zinc-300">{finding.message}</p>
        )}

        {/* Suggestion */}
        {finding.suggestion && (
          <p className="text-xs text-zinc-500 mt-1">
            <span className="text-zinc-400 font-medium">💡 Fix: </span>
            {finding.suggestion}
          </p>
        )}
      </div>
    </div>
  );
}
