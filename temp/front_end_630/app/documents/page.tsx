import MainLayout from "@/components/layout/MainLayout";

import UploadZone from "@/components/upload/UploadZone";
import UploadedDocuments from "@/components/upload/UploadedDocuments";
import OCRResultsCard from "@/components/upload/OCRResultsCard";
import InvoiceInsights from "@/components/upload/InvoiceInsights";

import AgentActivityFeed from "@/components/agents/AgentActivityFeed";

export default function DocumentsPage() {
  return (
    <MainLayout
      title="Document Intelligence Center"
      description="Multi-modal AI-powered invoice and financial document processing"
    >
      <div className="space-y-6">
        
        <UploadZone />

        <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
          
          {/* LEFT */}
          <div className="xl:col-span-2 space-y-6">
            
            <UploadedDocuments />

            <OCRResultsCard />
          </div>

          {/* RIGHT */}
          <div className="space-y-6">
            
            <InvoiceInsights />

            <AgentActivityFeed />
          </div>
        </div>
      </div>
    </MainLayout>
  );
}