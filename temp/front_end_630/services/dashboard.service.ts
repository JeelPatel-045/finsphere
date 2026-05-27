import API from "@/lib/api";

export const fetchDashboardKPIs = async () => {
  const response = await API.get("/dashboard/kpis");
  return response.data;
};

export const fetchRevenueAnalytics = async () => {
  const response = await API.get("/dashboard/revenue");
  return response.data;
};