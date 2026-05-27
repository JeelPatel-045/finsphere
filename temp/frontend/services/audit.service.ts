import API from "@/lib/api";

export const fetchAuditInsights = async () => {
  const response = await API.get("/audit");

  return response.data;
};

export const fetchRiskTransactions = async () => {
  const response = await API.get(
    "/audit/risk-transactions"
  );

  return response.data;
};