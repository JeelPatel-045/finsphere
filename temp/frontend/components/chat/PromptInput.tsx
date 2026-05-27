"use client";

import { SendHorizonal } from "lucide-react";
import { useState } from "react";

export default function PromptInput() {
  const [prompt, setPrompt] = useState("");

  const handleSubmit = () => {
    console.log(prompt);
    setPrompt("");
  };

  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-4">
      
      <div className="flex items-center gap-4">
        
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask FinSphere AI about audits, forecasting, risks, transactions..."
          className="
            flex-1
            bg-transparent
            outline-none
            resize-none
            text-sm
            text-white
            placeholder:text-slate-500
          "
          rows={2}
        />

        <button
          onClick={handleSubmit}
          className="
            h-12
            w-12
            rounded-xl
            bg-blue-600
            hover:bg-blue-700
            transition-all
            flex
            items-center
            justify-center
          "
        >
          <SendHorizonal size={18} />
        </button>
      </div>
    </div>
  );
}