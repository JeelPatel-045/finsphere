import MainLayout from "@/components/layout/MainLayout";

import AgentActivityFeed from "@/components/agents/AgentActivityFeed";
import AgentStatusCard from "@/components/agents/AgentStatusCard";
import WorkflowTimeline from "@/components/agents/WorkflowTimeline";
import AgentExecutionGraph from "@/components/agents/AgentExecutionGraph";

export default function AgentsPage() {
  return (
    <MainLayout
      title="AI Agent Orchestration"
      description="Multi-agent autonomous workflow execution system"
    >
      <div className="space-y-6">
        
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <AgentStatusCard />
          <AgentActivityFeed />
        </div>

        <WorkflowTimeline />

        <AgentExecutionGraph />
      </div>
    </MainLayout>
  );
}