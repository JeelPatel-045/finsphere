"use client";

export default function TypingIndicator() {
  return (
    <div className="flex justify-start">
      
      <div className="bg-slate-900 border border-slate-800 rounded-2xl px-5 py-4 flex gap-2">
        
        <span className="h-2 w-2 rounded-full bg-slate-400 animate-bounce" />

        <span
          className="h-2 w-2 rounded-full bg-slate-400 animate-bounce"
          style={{ animationDelay: "0.2s" }}
        />

        <span
          className="h-2 w-2 rounded-full bg-slate-400 animate-bounce"
          style={{ animationDelay: "0.4s" }}
        />
      </div>
    </div>
  );
}