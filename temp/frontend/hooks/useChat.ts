"use client";

import { useState } from "react";

import { sendChatMessage } from "@/services/chat.service";

export const useChat = () => {
  const [loading, setLoading] =
    useState(false);

  const sendMessage = async (
    message: string
  ) => {
    try {
      setLoading(true);

      const response =
        await sendChatMessage(message);

      return response;
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return {
    sendMessage,
    loading
  };
};