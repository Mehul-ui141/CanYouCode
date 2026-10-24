/** API calls for the review flow. */

import { api } from "./client";
import type { Review, ReviewListItem } from "@/types";

export interface ReviewRequestPayload {
  code: string;
  input_mode: "raw" | "diff";
  language: "python";
  personality_id: string;
}

export async function getPersonalities() {
  const res = await api("/api/personalities");
  if (!res.ok) throw new Error("Failed to fetch personalities");
  return res.json();
}

export async function getReview(id: string): Promise<Review> {
  const res = await api(`/api/review/${id}`);
  if (!res.ok) throw new Error("Failed to fetch review");
  return res.json();
}

export async function getSharedReview(token: string): Promise<Review> {
  const res = await api(`/api/review/share/${token}`);
  if (!res.ok) throw new Error("Failed to fetch shared review");
  return res.json();
}

export async function listReviews(skip = 0, limit = 20): Promise<ReviewListItem[]> {
  const res = await api(`/api/reviews?skip=${skip}&limit=${limit}`);
  if (!res.ok) throw new Error("Failed to fetch reviews");
  return res.json();
}