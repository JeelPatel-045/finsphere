"use client";

import { useAudit } from "@/hooks/useAudit";

export default function SuspiciousTransactions() {
  const { transactions, loading } =
    useAudit();

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-4">
      {transactions.map((txn: any) => (
        <div
          key={txn.id}
          className="bg-slate-900 p-4 rounded-xl"
        >
          <h3>{txn.vendor}</h3>

          <p>{txn.amount}</p>

          <span>{txn.risk}</span>
        </div>
      ))}
    </div>
  );
}