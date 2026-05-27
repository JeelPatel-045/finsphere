"use client";

import { useEffect, useState } from "react";

import API from "@/lib/api";

export default function AgentStatusCard() {
  const [agents, setAgents] =
    useState([]);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    const response =
      await API.get("/agents/status");

    setAgents(response.data);
  };

  return (
    <div className="space-y-4">
      {agents.map((agent: any) => (
        <div
          key={agent.name}
          className="bg-slate-900 p-4 rounded-xl"
        >
          <h3>{agent.name}</h3>

          <p>{agent.status}</p>
        </div>
      ))}
    </div>
  );
}