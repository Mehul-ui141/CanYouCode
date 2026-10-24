/** Severity badge — a small color-coded pill. */

import { SEVERITY_CONFIG, SEVERITY_ICONS } from "../../lib/constants";
import type { Severity } from "../../types";

export default function SeverityBadge({ severity }: { severity: Severity }) {
  const config = SEVERITY_CONFIG[severity];
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}
    >
      <span>{SEVERITY_ICONS[severity]}</span>
      {config.label}
    </span>
  );
}
