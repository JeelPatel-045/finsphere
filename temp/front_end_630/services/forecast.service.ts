import API from "@/lib/api";

export const fetchForecastData = async () => {
  const response = await API.get("/forecast");
  return response.data;
};