"use client";

import { useForecast } from "@/hooks/useForecast";

export default function ForecastKPIs() {
  const { data } = useForecast();

  if (!data) {
    return null;
  }

  return (
    <div className="grid grid-cols-4 gap-6">
      <div>{data.revenue}</div>

      <div>{data.cashflow}</div>

      <div>{data.accuracy}</div>

      <div>{data.confidence}</div>
    </div>
  );
}