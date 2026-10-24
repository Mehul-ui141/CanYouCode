/**
 * ReviewPage — displays a saved review by ID or share token.
 * Used for shared review links: /review/:reviewId or /review/share/:shareToken
 */

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Container from "../components/layout/Container";
import ReviewDisplay from "../components/review/ReviewDisplay";
import Spinner from "../components/ui/Spinner";
import type { Review } from "../types";
import { getReview, getSharedReview } from "../api/reviews";

export default function ReviewPage() {
  const { reviewId, shareToken } = useParams<{
    reviewId?: string;
    shareToken?: string;
  }>();

  const [review, setReview] = useState<Review | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    const fetch = async () => {
      try {
        let data: Review;
        if (shareToken) {
          data = await getSharedReview(shareToken);
        } else if (reviewId) {
          data = await getReview(reviewId);
        } else {
          throw new Error("No review ID or share token provided");
        }
        if (!cancelled) setReview(data);
      } catch (err: unknown) {
        if (!cancelled) setError((err as Error).message || "Failed to load review");
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    fetch();
    return () => { cancelled = true; };
  }, [reviewId, shareToken]);

  if (loading) {
    return (
      <Container>
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <Spinner />
          <p className="text-zinc-400 text-sm">Loading review...</p>
        </div>
      </Container>
    );
  }

  if (error || !review) {
    return (
      <Container>
        <div className="flex flex-col items-center justify-center py-20 gap-4">
          <span className="text-4xl">😿</span>
          <h2 className="text-xl font-bold text-zinc-200">Review not found</h2>
          <p className="text-zinc-400 text-sm">{error || "This review may have been deleted."}</p>
          <a
            href="/"
            className="text-sm text-red-400 hover:text-red-300 underline underline-offset-4"
          >
            Start a new review
          </a>
        </div>
      </Container>
    );
  }

  // Build the AI text for the display — we pass it as-is since it's already stored.
  const aiText = review.ai_review || "";

  return (
    <Container>
      <div className="space-y-6">
        <div className="text-center space-y-1">
          <h2 className="text-2xl font-bold text-zinc-200">Saved Review</h2>
          <p className="text-xs text-zinc-500">
            Created {new Date(review.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Show the original code if available */}
        {review.code_input && (
          <details className="group">
            <summary className="cursor-pointer text-sm text-zinc-400 hover:text-zinc-200 transition-colors">
              View submitted code
            </summary>
            <pre className="mt-2 bg-zinc-900 border border-zinc-800 rounded-xl p-4 text-xs font-mono text-zinc-300 overflow-x-auto max-h-64 overflow-y-auto">
              {review.code_input}
            </pre>
          </details>
        )}

        <ReviewDisplay
          personalityId={review.personality_id}
          findings={review.findings}
          aiText={aiText}
          isStreaming={false}
          reviewId={review.id}
          shareToken={review.share_url?.split("/").pop() || null}
          stats={review.summary_stats}
        />
      </div>
    </Container>
  );
}
