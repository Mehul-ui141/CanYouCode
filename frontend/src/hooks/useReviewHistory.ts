/**
 * useReviewHistory — persist recent review IDs in localStorage so the
 * user can revisit past reviews without making an account.
 */

import { useCallback, useEffect, useState } from "react";

const STORAGE_KEY = "canyoucode_history";
const MAX_ITEMS = 50;

export interface HistoryEntry {
  id: string;
  personalityId: string;
  language: string;
  codePreview: string;
  createdAt: string;
}

export function useReviewHistory() {
  const [history, setHistory] = useState<HistoryEntry[]>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  });

  // Sync to localStorage whenever history changes.
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  }, [history]);

  const addEntry = useCallback((entry: HistoryEntry) => {
    setHistory((prev) => {
      // Remove duplicate if already exists.
      const filtered = prev.filter((e) => e.id !== entry.id);
      // Prepend the new one; cap at MAX_ITEMS.
      return [entry, ...filtered].slice(0, MAX_ITEMS);
    });
  }, []);

  const clearHistory = useCallback(() => {
    setHistory([]);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return { history, addEntry, clearHistory };
}
