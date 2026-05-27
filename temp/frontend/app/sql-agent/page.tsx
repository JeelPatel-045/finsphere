import MainLayout from "@/components/layout/MainLayout";

import SQLQueryCard from "@/components/tables/SQLQueryCard";
import QueryResultsTable from "@/components/tables/QueryResultsTable";
import DatabaseSchemaCard from "@/components/tables/DatabaseSchemaCard";

import AgentActivityFeed from "@/components/agents/AgentActivityFeed";

export default function SQLAgentPage() {
  return (
    <MainLayout
      title="AI SQL Agent"
      description="Natural language financial database querying powered by autonomous agents"
    >
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* LEFT */}
        <div className="xl:col-span-2 space-y-6">
          
          <SQLQueryCard
            question="Show top Q4 vendor payments with high-risk transactions"
            sql={`
SELECT
  vendor_name,
  payment_amount,
  risk_score
FROM vendor_transactions
WHERE quarter = 'Q4'
ORDER BY payment_amount DESC
LIMIT 10;
            `}
          />

          <QueryResultsTable />
        </div>

        {/* RIGHT */}
        <div className="space-y-6">
          
          <DatabaseSchemaCard />

          <AgentActivityFeed />
        </div>
      </div>
    </MainLayout>
  );
}