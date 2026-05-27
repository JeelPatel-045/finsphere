"use client";

const recommendations = [
  "Reduce high-risk vendor dependency by 18%",
  "Increase quarterly cash reserves for projected volatility",
  "Optimize operational expenses in Q4",
  "Review duplicate invoice approval workflows",
  "Implement AI-driven vendor risk monitoring"
];

export default function AIRecommendations() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          AI Strategic Recommendations
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          Autonomous CFO-level financial guidance
        </p>
      </div>

      <div className="space-y-4">
        
        {recommendations.map((item, index) => (
          <div
            key={index}
            className="bg-slate-900 rounded-xl p-4 flex gap-4"
          >
            <div className="h-3 w-3 rounded-full bg-green-500 mt-2" />

            <p className="text-slate-300">
              {item}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}