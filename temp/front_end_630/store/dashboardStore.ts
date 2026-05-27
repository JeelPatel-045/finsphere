import { create } from "zustand";

interface DashboardState {
  kpis: any;
  revenueData: any[];

  setKPIs: (data: any) => void;
  setRevenueData: (data: any[]) => void;
}

export const useDashboardStore =
  create<DashboardState>((set) => ({
    kpis: null,
    revenueData: [],

    setKPIs: (data) =>
      set({
        kpis: data
      }),

    setRevenueData: (data) =>
      set({
        revenueData: data
      })
  }));