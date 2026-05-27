import { create } from "zustand";

interface KPIState {
  revenue: number;
  forecast: number;
  riskScore: number;

  setKPIs: (
    revenue: number,
    forecast: number,
    riskScore: number
  ) => void;
}

export const useDashboardStore =
  create<KPIState>((set) => ({
    revenue: 0,
    forecast: 0,
    riskScore: 0,

    setKPIs: (
      revenue,
      forecast,
      riskScore
    ) =>
      set({
        revenue,
        forecast,
        riskScore
      })
  }));