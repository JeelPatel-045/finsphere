import MainLayout from "@/components/layout/MainLayout";

import DashboardHeader from "@/components/dashboard/DashboardHeader";
import KPICards from "@/components/dashboard/KPICards";
import RevenueChart from "@/components/dashboard/RevenueChart";
import ForecastChart from "@/components/dashboard/ForecastChart";
import RiskHeatmap from "@/components/dashboard/RiskHeatmap";

export default function DashboardPage() {
  return (
    <MainLayout
      title="Dashboard"
      description="AI-powered enterprise financial intelligence"
    >
      <div className="space-y-6">
        
        <DashboardHeader />

        <KPICards />

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <RevenueChart />
          <ForecastChart />
        </div>

        <RiskHeatmap />
      </div>
    </MainLayout>
  );
}