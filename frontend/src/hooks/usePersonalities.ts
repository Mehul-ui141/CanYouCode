/** Fetch and cache the list of available personalities. */

import { useEffect, useState } from "react";
import { getPersonalities } from "@/api/personalities";
import type { Personality } from "@/types";

export function usePersonalities() {
  const [personalities, setPersonalities] = useState<Personality[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getPersonalities()
      .then((data) => {
        if (!cancelled) setPersonalities(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message || "Failed to load personalities");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { personalities, loading, error };
}