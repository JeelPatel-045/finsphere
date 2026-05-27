import API from "@/lib/api";

export const sendChatMessage = async (
  message: string
) => {
  const response = await API.post("/chat", {
    message
  });

  return response.data;
};