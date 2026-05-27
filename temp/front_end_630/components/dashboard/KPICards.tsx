"use client";

import { useDashboard } from "@/hooks/useDashboard";

export default function KPICards() {
  const { kpis, loading } =
    useDashboard();

  if (loading || !kpis) {
    return <div>Loading KPIs...</div>;
  }

  const data = [
    {
      title: "Revenue",
      value: `$${kpis.revenue}`
    },
    {
      title: "Forecast",
      value: `${kpis.forecast}%`
    },
    {
      title: "Risk Score",
      value: `${kpis.riskScore}%`
    },
    {
      title: "Active Agents",
      value: kpis.activeAgents
    }
  ];

  return (
    <div className="grid grid-cols-4 gap-6">
      {data.map((item) => (
        <div
          key={item.title}
          className="bg-[#111827] p-6 rounded-2xl"
        >
          <p>{item.title}</p>

          <h2 className="text-3xl font-bold mt-4">
            {item.value}
          </h2>
        </div>
      ))}
    </div>
  );
}