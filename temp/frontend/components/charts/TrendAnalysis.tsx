"use client";

const trends = [
  {
    metric: "Revenue Growth",
    value: "+21%"
  },
  {
    metric: "Operational Costs",
    value: "-8%"
  },
  {
    metric: "Vendor Risk Exposure",
    value: "+12%"
  },
  {
    metric: "Cash Reserve Stability",
    value: "+18%"
  }
];

export default function TrendAnalysis() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          AI Trend Analysis
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          Autonomous business intelligence insights
        </p>
      </div>

      <div className="space-y-4">
        
        {trends.map((trend) => (
          <div
            key={trend.metric}
            className="bg-slate-900 rounded-xl p-4 flex items-center justify-between"
          >
            <div>
              <h3 className="font-medium">
                {trend.metric}
              </h3>

              <p className="text-sm text-slate-400 mt-1">
                AI-generated predictive insight
              </p>
            </div>

            <span className="text-green-400 font-semibold">
              {trend.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}