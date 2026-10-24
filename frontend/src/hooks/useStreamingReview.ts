/**
 * useStreamingReview — manages the entire review lifecycle:
 * idle → analyzing → streaming → complete | error
 *
 * Consumes the SSE stream from POST /api/review and progressively updates
 * the UI state so the user sees findings immediately and the AI commentary
 * types in live.
 */

import { useCallback, useRef, useState } from "react";
import type { Finding, Language, StreamEvent } from "../types";

export type StreamStatus = "idle" | "analyzing" | "streaming" | "complete" | "error";

export interface StreamState {
  status: StreamStatus;
  /** Static-analysis findings (available as soon as analysis completes). */
  findings: Finding[];
  /** Accumulated AI personality text (grows as chunks arrive). */
  aiText: string;
  /** Review ID once saved to the DB. */
  reviewId: string | null;
  /** Share token for shareable links. */
  shareToken: string | null;
  /** Summary stats by severity. */
  stats: Record<string, number> | null;
  /** Error message if something went wrong. */
  error: string | null;
}

const INITIAL: StreamState = {
  status: "idle",
  findings: [],
  aiText: "",
  reviewId: null,
  shareToken: null,
  stats: null,
  error: null,
};

export interface ReviewSubmitPayload {
  code: string;
  input_mode: "raw" | "diff";
  language: Language;
  personality_id: string;
}

export function useStreamingReview() {
  const [state, setState] = useState<StreamState>(INITIAL);
  const abortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    setState(INITIAL);
  }, []);

  const submit = useCallback(async (payload: ReviewSubmitPayload) => {
    // Cancel any in-flight request.
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setState({
      ...INITIAL,
      status: "analyzing",
    });

    try {
      const res = await fetch("/api/review", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      if (!res.ok) {
        const text = await res.text().catch(() => "");
        setState((s) => ({
          ...s,
          status: "error",
          error: `Request failed: ${res.status} ${text}`,
        }));
        return;
      }

      const reader = res.body?.getReader();
      if (!reader) {
        setState((s) => ({
          ...s,
          status: "error",
          error: "No response body",
        }));
        return;
      }

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // SSE events are separated by double newlines.
        const parts = buffer.split("\n\n");
        buffer = parts.pop() || "";

        for (const part of parts) {
          const line = part.trim();
          if (!line.startsWith("data: ")) continue;

          try {
            const event: StreamEvent = JSON.parse(line.slice(6));

            switch (event.type) {
              case "analysis":
                setState((s) => ({
                  ...s,
                  status: "streaming",
                  reviewId: event.review_id,
                  findings: event.findings,
                }));
                break;

              case "text":
                setState((s) => ({
                  ...s,
                  status: "streaming",
                  aiText: s.aiText + event.content,
                }));
                break;

              case "complete":
                setState((s) => ({
                  ...s,
                  status: "complete",
                  reviewId: event.review_id,
                  shareToken: event.share_token,
                  stats: event.stats,
                }));
                break;

              case "error":
                setState((s) => ({
                  ...s,
                  status: "error",
                  error: event.content,
                }));
                break;
            }
          } catch {
            // Malformed SSE line; skip it.
          }
        }
      }
    } catch (err: unknown) {
      if ((err as Error).name === "AbortError") return; // user cancelled
      setState((s) => ({
        ...s,
        status: "error",
        error: (err as Error).message || "Unknown error",
      }));
    }
  }, []);

  return { state, submit, reset };
}
