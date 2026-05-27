import API from "@/lib/api";

export const fetchForecastData = async () => {
  const response = await API.get("/forecast");

  return response.data;
};

export const fetchRevenuePredictions = async () => {
  const response = await API.get(
    "/forecast/revenue"
  );

  return response.data;
};