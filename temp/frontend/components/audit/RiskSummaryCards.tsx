"use client";

import {
  ShieldAlert,
  AlertTriangle,
  Activity,
  FileWarning
} from "lucide-react";

const risks = [
  {
    title: "High Risk Transactions",
    value: "14",
    icon: ShieldAlert,
    color: "bg-red-500"
  },
  {
    title: "Compliance Violations",
    value: "6",
    icon: FileWarning,
    color: "bg-orange-500"
  },
  {
    title: "Audit Flags",
    value: "28",
    icon: AlertTriangle,
    color: "bg-yellow-500"
  },
  {
    title: "AI Risk Score",
    value: "82%",
    icon: Activity,
    color: "bg-blue-500"
  }
];

export default function RiskSummaryCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
      
      {risks.map((item) => {
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

              <div
                className={`h-14 w-14 rounded-2xl ${item.color} flex items-center justify-center`}
              >
                <Icon />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}