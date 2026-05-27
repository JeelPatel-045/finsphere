import MainLayout from "@/components/layout/MainLayout";

import RiskSummaryCards from "@/components/audit/RiskSummaryCards";
import ComplianceViolations from "@/components/audit/ComplianceViolations";
import SuspiciousTransactions from "@/components/audit/SuspiciousTransactions";
import AuditInsights from "@/components/audit/AuditInsights";
import RiskScoreChart from "@/components/audit/RiskScoreChart";

import AgentActivityFeed from "@/components/agents/AgentActivityFeed";

export default function AuditPage() {
  return (
    <MainLayout
      title="Audit & Risk Intelligence"
      description="Autonomous AI-powered financial compliance and anomaly detection"
    >
      <div className="space-y-6">
        
        <RiskSummaryCards />

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <ComplianceViolations />
          <RiskScoreChart />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <SuspiciousTransactions />
          <AuditInsights />
        </div>

        <AgentActivityFeed />
      </div>
    </MainLayout>
  );
}