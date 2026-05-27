"use client";

import {
  LineChart,
  Line,
  ResponsiveContainer,
  XAxis,
  CartesianGrid,
  Tooltip
} from "recharts";

import { useDashboard } from "@/hooks/useDashboard";

export default function RevenueChart() {
  const { revenueData, loading } =
    useDashboard();

  if (loading) {
    return <div>Loading chart...</div>;
  }

  return (
    <div className="bg-[#111827] p-6 rounded-2xl">
      <div className="h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={revenueData}>
            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="month" />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#3B82F6"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}