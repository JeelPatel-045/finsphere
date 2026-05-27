"use client";

export default function AgentExecutionGraph() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-8">
        <h2 className="text-xl font-semibold">
          Agent Execution Graph
        </h2>

        <p className="text-slate-400 text-sm mt-1">
          LangGraph-inspired orchestration visualization
        </p>
      </div>

      <div className="flex flex-col items-center gap-6">
        
        {/* SUPERVISOR */}
        <div className="bg-blue-600 px-8 py-4 rounded-2xl font-semibold shadow-lg">
          Supervisor Agent
        </div>

        {/* CONNECTOR */}
        <div className="h-10 w-[2px] bg-slate-700" />

        {/* CHILD AGENTS */}
        <div className="grid grid-cols-2 xl:grid-cols-3 gap-6 w-full">
          
          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5 text-center">
            SQL Agent
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5 text-center">
            Audit Agent
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5 text-center">
            Forecast Agent
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5 text-center">
            OCR Agent
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5 text-center">
            RAG Agent
          </div>

          <div className="bg-slate-900 border border-slate-700 rounded-2xl p-5 text-center">
            Report Agent
          </div>
        </div>
      </div>
    </div>
  );
}