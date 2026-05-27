"use client";

const insights = [
  {
    title: "Duplicate Invoice Risk",
    level: "High"
  },
  {
    title: "GST Validation",
    level: "Valid"
  },
  {
    title: "Approval Workflow",
    level: "Pending"
  },
  {
    title: "Vendor Risk Score",
    level: "Medium"
  }
];

export default function InvoiceInsights() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          AI Invoice Insights
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          Autonomous document intelligence analysis
        </p>
      </div>

      <div className="space-y-4">
        
        {insights.map((item) => (
          <div
            key={item.title}
            className="flex items-center justify-between bg-slate-900 rounded-xl p-4"
          >
            <h3 className="font-medium">
              {item.title}
            </h3>

            <span
              className={`
                px-3
                py-2
                rounded-xl
                text-sm
                ${
                  item.level === "High"
                    ? "bg-red-500 text-white"
                    : item.level === "Medium"
                    ? "bg-yellow-500 text-black"
                    : item.level === "Pending"
                    ? "bg-orange-500 text-white"
                    : "bg-green-500 text-white"
                }
              `}
            >
              {item.level}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}