"use client";

import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

const messages = [
  {
    role: "user",
    message:
      "Analyze suspicious Q4 journal entries and identify anomalies."
  },
  {
    role: "assistant",
    message:
      "I analyzed 1,248 journal entries. 14 transactions were flagged as high-risk due to duplicate invoices, unusual approval chains, and abnormal debit-credit ratios."
  },
  {
    role: "assistant",
    message:
      "Audit Agent identified 3 compliance violations related to vendor payment approvals."
  }
];

export default function ChatWindow() {
  return (
    <div
      className="
        bg-[#111827]
        border
        border-slate-800
        rounded-2xl
        p-6
        h-[600px]
        flex
        flex-col
      "
    >
      {/* HEADER */}
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          FinSphere AI Assistant
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          Multi-model finance copilot powered by autonomous agents
        </p>
      </div>

      {/* MESSAGES */}
      <div className="flex-1 overflow-y-auto space-y-5 pr-2">
        
        {messages.map((msg, index) => (
          <MessageBubble
            key={index}
            role={msg.role as "user" | "assistant"}
            message={msg.message}
          />
        ))}

        <TypingIndicator />
      </div>
    </div>
  );
}