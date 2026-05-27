"use client";

import { useChatStore } from "@/store/chatStore";

export default function ChatWindow() {
  const { messages } = useChatStore();

  return (
    <div className="space-y-4 h-[500px] overflow-y-auto">
      {messages.map((msg, index) => (
        <div
          key={index}
          className={`p-4 rounded-xl ${
            msg.role === "user"
              ? "bg-blue-600"
              : "bg-slate-900"
          }`}
        >
          {msg.content}
        </div>
      ))}
    </div>
  );
}