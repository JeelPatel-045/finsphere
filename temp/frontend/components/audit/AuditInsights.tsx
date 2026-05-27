"use client";

const insights = [
  "14 high-risk journal entries identified in Q4",
  "Vendor duplication patterns detected in AP transactions",
  "3 approval workflows bypassed compliance policy",
  "Cash flow variance increased by 18.4%",
  "AI confidence score for audit review: 92%"
];

export default function AuditInsights() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          AI Audit Insights
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          Autonomous reasoning and compliance analysis
        </p>
      </div>

      <div className="space-y-4">
        
        {insights.map((insight, index) => (
          <div
            key={index}
            className="bg-slate-900 rounded-xl p-4 flex gap-4"
          >
            <div className="h-3 w-3 rounded-full bg-blue-500 mt-2" />

            <p className="text-slate-300">
              {insight}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}