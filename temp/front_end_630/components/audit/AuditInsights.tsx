"use client";

import { useAudit } from "@/hooks/useAudit";

export default function AuditInsights() {
  const { insights } = useAudit();

  return (
    <div className="space-y-4">
      {insights.map(
        (item: any, index: number) => (
          <div
            key={index}
            className="bg-slate-900 p-4 rounded-xl"
          >
            {item.message}
          </div>
        )
      )}
    </div>
  );
}