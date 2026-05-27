"use client";

const prompts = [
  "Analyze suspicious Q4 transactions",
  "Generate cash flow forecast",
  "Find duplicate invoices",
  "Show top expense accounts",
  "Summarize audit compliance risks"
];

export default function SuggestedPrompts() {
  return (
    <div className="flex flex-wrap gap-3">
      
      {prompts.map((prompt) => (
        <button
          key={prompt}
          className="
            bg-slate-900
            border
            border-slate-800
            hover:border-blue-500
            hover:bg-slate-800
            transition-all
            px-4
            py-3
            rounded-xl
            text-sm
            text-slate-300
          "
        >
          {prompt}
        </button>
      ))}
    </div>
  );
}