"use client";

import { useEffect, useState } from "react";

import {
  fetchAuditInsights,
  fetchRiskTransactions
} from "@/services/audit.service";

export const useAudit = () => {
  const [insights, setInsights] =
    useState([]);

  const [transactions, setTransactions] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {
    loadAudit();
  }, []);

  const loadAudit = async () => {
    try {
      setLoading(true);

      const insightResponse =
        await fetchAuditInsights();

      const transactionResponse =
        await fetchRiskTransactions();

      setInsights(insightResponse);

      setTransactions(transactionResponse);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return {
    insights,
    transactions,
    loading
  };
};