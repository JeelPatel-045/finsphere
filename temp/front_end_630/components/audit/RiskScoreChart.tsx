"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer
} from "recharts";

const data = [
  { name: "Critical", value: 28 },
  { name: "High", value: 42 },
  { name: "Medium", value: 20 },
  { name: "Low", value: 10 }
];

const COLORS = [
  "#DC2626",
  "#F97316",
  "#EAB308",
  "#22C55E"
];

export default function RiskScoreChart() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          AI Risk Distribution
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          Financial anomaly severity analysis
        </p>
      </div>

      <div className="h-[300px]">
        
        <ResponsiveContainer width="100%" height="100%">
          
          <PieChart>
            
            <Pie
              data={data}
              dataKey="value"
              outerRadius={100}
            >
              {data.map((_, index) => (
                <Cell
                  key={index}
                  fill={COLORS[index]}
                />
              ))}
            </Pie>

            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}