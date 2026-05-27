"use client";

const schema = [
  {
    table: "journal_entries",
    columns: [
      "transaction_id",
      "account_name",
      "debit",
      "credit",
      "quarter"
    ]
  },
  {
    table: "vendors",
    columns: [
      "vendor_id",
      "vendor_name",
      "payment_amount"
    ]
  },
  {
    table: "audit_logs",
    columns: [
      "audit_id",
      "risk_score",
      "compliance_status"
    ]
  }
];

export default function DatabaseSchemaCard() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          Database Schema
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          Available financial tables for AI querying
        </p>
      </div>

      <div className="space-y-5">
        
        {schema.map((table) => (
          <div
            key={table.table}
            className="bg-slate-900 rounded-xl p-5"
          >
            <h3 className="font-semibold text-blue-400 mb-4">
              {table.table}
            </h3>

            <div className="flex flex-wrap gap-3">
              
              {table.columns.map((column) => (
                <span
                  key={column}
                  className="
                    px-3
                    py-2
                    rounded-lg
                    bg-slate-800
                    text-sm
                    text-slate-300
                  "
                >
                  {column}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}