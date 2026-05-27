"use client";

import {
  AreaChart,
  Area,
  ResponsiveContainer,
  XAxis,
  CartesianGrid,
  Tooltip
} from "recharts";

const data = [
  { month: "Jul", cashflow: 120000 },
  { month: "Aug", cashflow: 145000 },
  { month: "Sep", cashflow: 158000 },
  { month: "Oct", cashflow: 172000 },
  { month: "Nov", cashflow: 184000 },
  { month: "Dec", cashflow: 205000 }
];

export default function CashFlowForecast() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          Cash Flow Projection
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          Predictive AI cash movement analysis
        </p>
      </div>

      <div className="h-[320px]">
        
        <ResponsiveContainer width="100%" height="100%">
          
          <AreaChart data={data}>
            
            <defs>
              <linearGradient id="cashFlow" x1="0" y1="0" x2="0" y2="1">
                
                <stop
                  offset="5%"
                  stopColor="#22C55E"
                  stopOpacity={0.8}
                />

                <stop
                  offset="95%"
                  stopColor="#22C55E"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#1E293B"
            />

            <XAxis
              dataKey="month"
              stroke="#94A3B8"
            />

            <Tooltip />

            <Area
              type="monotone"
              dataKey="cashflow"
              stroke="#22C55E"
              fillOpacity={1}
              fill="url(#cashFlow)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}