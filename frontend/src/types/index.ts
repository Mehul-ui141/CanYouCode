/** Shared TypeScript types for the Can You Code frontend. */

export type Severity = "critical" | "warning" | "info" | "nitpick";

export type InputMode = "raw" | "diff";

export type Language = "python" | "java" | "c" | "cpp" | "javascript" | "typescript";

export interface Finding {
  id: string;
  category: "complexity" | "smell" | "bug" | "style";
  rule: string;
  severity: Severity;
  message: string;
  line_start?: number;
  line_end?: number;
  code_snippet?: string;
  suggestion?: string;
}

export interface Personality {
  id: string;
  name: string;
  description: string;
  emoji: string;
  color: string;
  tone_preview: string;
}

export interface AnalysisEvent {
  type: "analysis";
  review_id: string;
  personality_id: string;
  input_mode: InputMode;
  language: Language;
  findings: Finding[];
}

export interface TextEvent {
  type: "text";
  content: string;
}

export interface CompleteEvent {
  type: "complete";
  review_id: string;
  share_token: string;
  share_url: string;
  findings_count: number;
  stats: Record<Severity, number>;
}

export interface ErrorEvent {
  type: "error";
  content: string;
}

export type StreamEvent = AnalysisEvent | TextEvent | CompleteEvent | ErrorEvent;

export interface PersonFinding {
  id: string;
  comment: string;
  severity_reaction: string;
}

export interface AiReview {
  opening: string;
  findings: PersonFinding[];
  closing: string;
  overall_grade: string;
}

export interface Review {
  id: string;
  personality_id: string;
  input_mode: InputMode;
  language: Language;
  findings: Finding[];
  ai_review: string;
  opening: string;
  closing: string;
  overall_grade: string;
  summary_stats: Record<Severity, number>;
  share_url: string;
  created_at: string;
  code_input?: string;
}

export interface ReviewListItem {
  id: string;
  personality_id: string;
  language: Language;
  summary_stats: Record<Severity, number>;
  created_at: string;
  code_preview: string;
}
