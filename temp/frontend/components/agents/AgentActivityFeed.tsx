"use client";

import {
  Bot,
  Database,
  ShieldAlert,
  FileSearch,
  TrendingUp
} from "lucide-react";

const activities = [
  {
    agent: "Supervisor Agent",
    action: "Analyzing user financial request",
    time: "10:21:01",
    icon: Bot,
    color: "bg-blue-500"
  },
  {
    agent: "SQL Agent",
    action: "Fetching Q4 transactions from database",
    time: "10:21:03",
    icon: Database,
    color: "bg-purple-500"
  },
  {
    agent: "Audit Agent",
    action: "Running compliance validation checks",
    time: "10:21:05",
    icon: ShieldAlert,
    color: "bg-red-500"
  },
  {
    agent: "RAG Agent",
    action: "Retrieving accounting policy documents",
    time: "10:21:08",
    icon: FileSearch,
    color: "bg-yellow-500"
  },
  {
    agent: "Forecast Agent",
    action: "Generating financial trend predictions",
    time: "10:21:11",
    icon: TrendingUp,
    color: "bg-green-500"
  }
];

export default function AgentActivityFeed() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        <h2 className="text-xl font-semibold">
          Agent Activity Feed
        </h2>

        <p className="text-slate-400 text-sm mt-1">
          Live orchestration of multi-agent AI workflows
        </p>
      </div>

      <div className="space-y-5">
        
        {activities.map((item, index) => {
          const Icon = item.icon;

          return (
            <div
              key={index}
              className="flex gap-4"
            >
              {/* ICON */}
              <div
                className={`h-12 w-12 rounded-2xl ${item.color} flex items-center justify-center`}
              >
                <Icon size={20} />
              </div>

              {/* CONTENT */}
              <div className="flex-1">
                
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold">
                    {item.agent}
                  </h3>

                  <span className="text-xs text-slate-500">
                    {item.time}
                  </span>
                </div>

                <p className="text-sm text-slate-400 mt-1">
                  {item.action}
                </p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}