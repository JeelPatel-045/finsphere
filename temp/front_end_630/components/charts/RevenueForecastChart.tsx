"use client";

import { useForecast } from "@/hooks/useForecast";

import {
  LineChart,
  Line,
  ResponsiveContainer
} from "recharts";

export default function RevenueForecastChart() {
  const { data } = useForecast();

  return (
    <ResponsiveContainer
      width="100%"
      height={300}
    >
      <LineChart data={data}>
        <Line
          dataKey="forecast"
          stroke="#22C55E"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}