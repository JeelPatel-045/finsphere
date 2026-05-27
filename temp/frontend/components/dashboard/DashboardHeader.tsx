"use client";

export default function DashboardHeader() {
  return (
    <div className="flex items-center justify-between">
      
      <div>
        <h1 className="text-3xl font-bold">
          Executive Finance Dashboard
        </h1>

        <p className="text-slate-400 mt-2">
          Multi-Model Agentic AI Financial Intelligence Platform
        </p>
      </div>

      <div className="flex items-center gap-3">
        
        <button className="bg-blue-600 hover:bg-blue-700 transition-all px-5 py-3 rounded-xl font-medium">
          Generate AI Report
        </button>

        <button className="bg-slate-800 hover:bg-slate-700 transition-all px-5 py-3 rounded-xl font-medium">
          Export Analytics
        </button>
      </div>
    </div>
  );
}