"use client";

import { useEffect, useState } from "react";

import {
  fetchForecastData
} from "@/services/forecast.service";

export const useForecast = () => {
  const [data, setData] = useState([]);

  const [loading, setLoading] =
    useState(false);

  useEffect(() => {
    loadForecast();
  }, []);

  const loadForecast = async () => {
    try {
      setLoading(true);

      const response =
        await fetchForecastData();

      setData(response);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return {
    data,
    loading
  };
};