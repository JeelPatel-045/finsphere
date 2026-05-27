"use client";

import {
  LineChart,
  Line,
  XAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from "recharts";

const data = [
  { month: "Jan", actual: 40000, forecast: 42000 },
  { month: "Feb", actual: 52000, forecast: 54000 },
  { month: "Mar", actual: 61000, forecast: 64000 },
  { month: "Apr", actual: 70000, forecast: 76000 },
  { month: "May", actual: 82000, forecast: 88000 },
  { month: "Jun", actual: 91000, forecast: 98000 }
];

export default function RevenueForecastChart() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          Revenue Forecasting Engine
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          AI-generated financial trend prediction
        </p>
      </div>

      <div className="h-[350px]">
        
        <ResponsiveContainer width="100%" height="100%">
          
          <LineChart data={data}>
            
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#1E293B"
            />

            <XAxis
              dataKey="month"
              stroke="#94A3B8"
            />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="actual"
              stroke="#3B82F6"
              strokeWidth={3}
            />

            <Line
              type="monotone"
              dataKey="forecast"
              stroke="#22C55E"
              strokeWidth={3}
              strokeDasharray="5 5"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}