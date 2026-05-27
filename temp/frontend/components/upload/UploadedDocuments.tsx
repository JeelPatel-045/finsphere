"use client";

import {
  FileText,
  FileSpreadsheet,
  FileImage
} from "lucide-react";

const documents = [
  {
    name: "Q4_Audit_Report.pdf",
    type: "PDF",
    icon: FileText
  },
  {
    name: "Vendor_Transactions.csv",
    type: "CSV",
    icon: FileSpreadsheet
  },
  {
    name: "Invoice_4582.png",
    type: "IMAGE",
    icon: FileImage
  }
];

export default function UploadedDocuments() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          Uploaded Documents
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          Financial files processed by AI agents
        </p>
      </div>

      <div className="space-y-4">
        
        {documents.map((doc) => {
          const Icon = doc.icon;

          return (
            <div
              key={doc.name}
              className="flex items-center justify-between bg-slate-900 rounded-xl p-4"
            >
              <div className="flex items-center gap-4">
                
                <div className="h-12 w-12 rounded-xl bg-slate-800 flex items-center justify-center">
                  <Icon className="text-blue-400" />
                </div>

                <div>
                  <h3 className="font-medium">
                    {doc.name}
                  </h3>

                  <p className="text-sm text-slate-400">
                    {doc.type} Document
                  </p>
                </div>
              </div>

              <span className="text-green-400 text-sm">
                Processed
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}