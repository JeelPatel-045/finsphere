"use client";

import { DatabaseZap } from "lucide-react";

interface SQLQueryCardProps {
  question: string;
  sql: string;
}

export default function SQLQueryCard({
  question,
  sql
}: SQLQueryCardProps) {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      {/* HEADER */}
      <div className="flex items-center gap-3 mb-6">
        
        <div className="h-12 w-12 rounded-2xl bg-blue-600/20 flex items-center justify-center">
          <DatabaseZap className="text-blue-400" />
        </div>

        <div>
          <h2 className="text-xl font-semibold">
            AI SQL Generation
          </h2>

          <p className="text-sm text-slate-400">
            Natural language to SQL conversion
          </p>
        </div>
      </div>

      {/* QUESTION */}
      <div className="mb-5">
        
        <p className="text-sm text-slate-400 mb-2">
          User Question
        </p>

        <div className="bg-slate-900 rounded-xl p-4 text-slate-200">
          {question}
        </div>
      </div>

      {/* SQL */}
      <div>
        
        <p className="text-sm text-slate-400 mb-2">
          Generated SQL Query
        </p>

        <pre className="bg-black rounded-xl p-5 overflow-x-auto text-green-400 text-sm">
{sql}
        </pre>
      </div>
    </div>
  );
}