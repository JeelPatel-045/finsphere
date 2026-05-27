"use client";

import {
  DollarSign,
  TrendingUp,
  ShieldAlert,
  Activity
} from "lucide-react";

const kpis = [
  {
    title: "Revenue",
    value: "$2.4M",
    change: "+18.2%",
    icon: DollarSign
  },
  {
    title: "Forecast Accuracy",
    value: "92%",
    change: "+4.3%",
    icon: TrendingUp
  },
  {
    title: "Risk Alerts",
    value: "14",
    change: "-2.1%",
    icon: ShieldAlert
  },
  {
    title: "AI Agent Tasks",
    value: "1,248",
    change: "+12.5%",
    icon: Activity
  }
];

export default function KPICards() {
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
              </div>

              <div className="h-14 w-14 rounded-2xl bg-blue-600/20 flex items-center justify-center">
                <Icon className="text-blue-400" />
              </div>
            </div>

            <div className="mt-5">
              <span className="text-green-400 text-sm font-medium">
                {item.change}
              </span>

              <span className="text-slate-500 text-sm ml-2">
                vs last month
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}