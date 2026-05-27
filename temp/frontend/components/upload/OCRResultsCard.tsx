"use client";

export default function OCRResultsCard() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          OCR Extraction Results
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          AI-generated invoice field extraction
        </p>
      </div>

      <div className="space-y-5">
        
        <div className="bg-slate-900 rounded-xl p-4">
          
          <p className="text-sm text-slate-400 mb-2">
            Vendor Name
          </p>

          <h3 className="font-semibold">
            Global Tech Solutions Pvt Ltd
          </h3>
        </div>

        <div className="bg-slate-900 rounded-xl p-4">
          
          <p className="text-sm text-slate-400 mb-2">
            Invoice Amount
          </p>

          <h3 className="font-semibold">
            ₹4,82,000
          </h3>
        </div>

        <div className="bg-slate-900 rounded-xl p-4">
          
          <p className="text-sm text-slate-400 mb-2">
            GST Number
          </p>

          <h3 className="font-semibold">
            24ABCDE1234F1Z5
          </h3>
        </div>

        <div className="bg-slate-900 rounded-xl p-4">
          
          <p className="text-sm text-slate-400 mb-2">
            Invoice Date
          </p>

          <h3 className="font-semibold">
            18-May-2026
          </h3>
        </div>
      </div>
    </div>
  );
}