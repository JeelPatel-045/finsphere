"use client";

import { UploadCloud } from "lucide-react";

export default function UploadZone() {
  return (
    <div
      className="
        border-2
        border-dashed
        border-slate-700
        rounded-2xl
        p-10
        bg-[#111827]
        text-center
        hover:border-blue-500
        transition-all
        cursor-pointer
      "
    >
      <div className="flex flex-col items-center">
        
        <div className="h-20 w-20 rounded-full bg-blue-600/20 flex items-center justify-center">
          <UploadCloud
            size={36}
            className="text-blue-400"
          />
        </div>

        <h2 className="text-2xl font-semibold mt-6">
          Upload Financial Documents
        </h2>

        <p className="text-slate-400 mt-3 max-w-xl">
          Upload invoices, journal entries, audit reports,
          PDFs, CSVs, or financial statements for AI analysis.
        </p>

        <button
          className="
            mt-6
            px-6
            py-3
            rounded-xl
            bg-blue-600
            hover:bg-blue-700
            transition-all
            font-medium
          "
        >
          Select Files
        </button>
      </div>
    </div>
  );
}