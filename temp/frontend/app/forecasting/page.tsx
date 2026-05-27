import MainLayout from "@/components/layout/MainLayout";

import ForecastKPIs from "@/components/charts/ForecastKPIs";
import RevenueForecastChart from "@/components/charts/RevenueForecastChart";
import CashFlowForecast from "@/components/charts/CashFlowForecast";
import TrendAnalysis from "@/components/charts/TrendAnalysis";
import AIRecommendations from "@/components/charts/AIRecommendations";

import AgentActivityFeed from "@/components/agents/AgentActivityFeed";

export default function ForecastingPage() {
  return (
    <MainLayout
      title="Forecasting Studio"
      description="AI-powered financial forecasting and predictive analytics"
    >
      <div className="space-y-6">
        
        <ForecastKPIs />

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <RevenueForecastChart />
          <CashFlowForecast />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <TrendAnalysis />
          <AIRecommendations />
        </div>

        <AgentActivityFeed />
      </div>
    </MainLayout>
  );
}