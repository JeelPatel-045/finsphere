import { create } from "zustand";

interface AgentActivity {
  agent: string;
  action: string;
  timestamp: string;
}

interface AgentState {
  activities: AgentActivity[];

  addActivity: (
    activity: AgentActivity
  ) => void;
}

export const useAgentStore = create<AgentState>(
  (set) => ({
    activities: [],

    addActivity: (activity) =>
      set((state) => ({
        activities: [
          activity,
          ...state.activities
        ]
      }))
  })
);