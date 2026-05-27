"use client";

import {
  useEffect,
  useState
} from "react";

import {
  fetchDashboardKPIs,
  fetchRevenueAnalytics
} from "@/services/dashboard.service";

export const useDashboard = () => {
  const [kpis, setKPIs] = useState(null);

  const [revenueData, setRevenueData] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);

      const kpiResponse =
        await fetchDashboardKPIs();

      const revenueResponse =
        await fetchRevenueAnalytics();

      setKPIs(kpiResponse);
      setRevenueData(revenueResponse);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return {
    kpis,
    revenueData,
    loading
  };
};