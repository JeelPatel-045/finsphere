"use client";

const agents = [
  {
    name: "Supervisor Agent",
    status: "Active"
  },
  {
    name: "SQL Agent",
    status: "Running"
  },
  {
    name: "Audit Agent",
    status: "Active"
  },
  {
    name: "Forecast Agent",
    status: "Idle"
  },
  {
    name: "OCR Agent",
    status: "Active"
  },
  {
    name: "Report Agent",
    status: "Running"
  }
];

export default function AgentStatusCard() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        <h2 className="text-xl font-semibold">
          AI Agent Status
        </h2>

        <p className="text-slate-400 text-sm mt-1">
          Real-time orchestration monitoring
        </p>
      </div>

      <div className="space-y-4">
        
        {agents.map((agent) => (
          <div
            key={agent.name}
            className="flex items-center justify-between bg-slate-900 rounded-xl p-4"
          >
            <div>
              <h3 className="font-medium">
                {agent.name}
              </h3>
            </div>

            <div className="flex items-center gap-2">
              
              <span className="h-3 w-3 rounded-full bg-green-500 animate-pulse" />

              <span className="text-sm text-slate-300">
                {agent.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}