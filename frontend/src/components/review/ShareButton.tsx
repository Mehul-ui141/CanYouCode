/** Share button — copies the shareable link to clipboard. */

import { useState } from "react";
import { copyToClipboard } from "../../lib/utils";

export default function ShareButton({ shareToken }: { shareToken: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const url = `${window.location.origin}/review/share/${shareToken}`;
    await copyToClipboard(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium
        border border-zinc-700 bg-zinc-800 hover:bg-zinc-700 text-zinc-300
        transition-colors"
    >
      {copied ? (
        <>
          <span>✓</span>
          <span>Copied!</span>
        </>
      ) : (
        <>
          <span>🔗</span>
          <span>Share</span>
        </>
      )}
    </button>
  );
}
