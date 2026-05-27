"use client";

const workflowSteps = [
  "User submits financial analysis request",
  "Supervisor Agent interprets query",
  "SQL Agent retrieves transaction data",
  "Audit Agent checks compliance violations",
  "Risk Agent detects anomalies",
  "Forecast Agent predicts financial trends",
  "Report Agent generates executive summary",
  "Dashboard updates visual insights"
];

export default function WorkflowTimeline() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        <h2 className="text-xl font-semibold">
          Multi-Agent Workflow Timeline
        </h2>

        <p className="text-slate-400 text-sm mt-1">
          Autonomous AI execution pipeline
        </p>
      </div>

      <div className="space-y-5">
        
        {workflowSteps.map((step, index) => (
          <div
            key={index}
            className="flex gap-4"
          >
            {/* STEP NUMBER */}
            <div className="flex flex-col items-center">
              
              <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center font-semibold">
                {index + 1}
              </div>

              {index !== workflowSteps.length - 1 && (
                <div className="w-[2px] h-10 bg-slate-700 mt-2" />
              )}
            </div>

            {/* TEXT */}
            <div className="pt-2">
              <p className="text-slate-300">
                {step}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}