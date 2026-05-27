"use client";

import {
  TrendingUp,
  Wallet,
  BarChart3,
  Activity
} from "lucide-react";

const kpis = [
  {
    title: "Projected Revenue",
    value: "$4.8M",
    growth: "+21%",
    icon: TrendingUp
  },
  {
    title: "Cash Flow Forecast",
    value: "$1.2M",
    growth: "+12%",
    icon: Wallet
  },
  {
    title: "Forecast Accuracy",
    value: "94%",
    growth: "+3%",
    icon: BarChart3
  },
  {
    title: "AI Confidence Score",
    value: "91%",
    growth: "+5%",
    icon: Activity
  }
];

export default function ForecastKPIs() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      
      {kpis.map((item) => {
        const Icon = item.icon;

        return (
          <div
            key={item.title}
            className="bg-[#111827] border border-slate-800 rounded-2xl p-6"
          >
            <div className="flex items-center justify-between">
              
              <div>
                <p className="text-slate-400 text-sm">
                  {item.title}
                </p>

                <h2 className="text-3xl font-bold mt-3">
                  {item.value}
                </h2>

                <p className="text-green-400 text-sm mt-3">
                  {item.growth} predicted growth
                </p>
              </div>

              <div className="h-14 w-14 rounded-2xl bg-green-500/20 flex items-center justify-center">
                <Icon className="text-green-400" />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}