"use client";

import { useState } from "react";

import { useChat } from "@/hooks/useChat";

import { useChatStore } from "@/store/chatStore";

export default function PromptInput() {
  const [prompt, setPrompt] = useState("");

  const { sendMessage } = useChat();

  const { addMessage } = useChatStore();

  const handleSubmit = async () => {
    if (!prompt.trim()) return;

    addMessage({
      role: "user",
      content: prompt
    });

    const response = await sendMessage(
      prompt
    );

    addMessage({
      role: "assistant",
      content: response.response
    });

    setPrompt("");
  };

  return (
    <div className="flex gap-4 mt-6">
      <input
        value={prompt}
        onChange={(e) =>
          setPrompt(e.target.value)
        }
        placeholder="Ask FinSphere AI..."
        className="flex-1 bg-slate-900 rounded-xl p-4"
      />

      <button
        onClick={handleSubmit}
        className="bg-blue-600 px-6 rounded-xl"
      >
        Send
      </button>
    </div>
  );
}