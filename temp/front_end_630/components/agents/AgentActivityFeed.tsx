"use client";

import { useAgentStore } from "@/store/agentStore";

export default function AgentActivityFeed() {
  const { activities } = useAgentStore();

  return (
    <div className="space-y-4">
      {activities.map((activity, index) => (
        <div
          key={index}
          className="bg-slate-900 p-4 rounded-xl"
        >
          <h3>{activity.agent}</h3>

          <p>{activity.action}</p>
        </div>
      ))}
    </div>
  );
}