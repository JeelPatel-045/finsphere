"use client";

interface MessageBubbleProps {
  role: "user" | "assistant";
  message: string;
}

export default function MessageBubble({
  role,
  message
}: MessageBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      }`}
    >
      <div
        className={`
          max-w-[75%]
          rounded-2xl
          px-5
          py-4
          text-sm
          leading-7
          ${
            isUser
              ? "bg-blue-600 text-white"
              : "bg-slate-900 border border-slate-800 text-slate-200"
          }
        `}
      >
        {message}
      </div>
    </div>
  );
}