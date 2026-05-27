"use client";

const risks = [
  {
    title: "Duplicate Invoices",
    level: "High",
    color: "bg-red-500"
  },
  {
    title: "Expense Spike",
    level: "Medium",
    color: "bg-yellow-500"
  },
  {
    title: "Missing Approvals",
    level: "High",
    color: "bg-red-500"
  },
  {
    title: "Cash Flow Variance",
    level: "Low",
    color: "bg-green-500"
  }
];

export default function RiskHeatmap() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        <h2 className="text-xl font-semibold">
          Audit Risk Heatmap
        </h2>

        <p className="text-slate-400 text-sm mt-1">
          AI-detected financial anomalies
        </p>
      </div>

      <div className="space-y-4">
        
        {risks.map((risk) => (
          <div
            key={risk.title}
            className="flex items-center justify-between bg-slate-900 rounded-xl p-4"
          >
            <div>
              <h3 className="font-medium">
                {risk.title}
              </h3>

              <p className="text-sm text-slate-400 mt-1">
                Financial compliance analysis
              </p>
            </div>

            <div
              className={`px-4 py-2 rounded-xl text-white text-sm ${risk.color}`}
            >
              {risk.level}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}