"use client";

const violations = [
  {
    issue: "Missing approval workflow",
    severity: "High"
  },
  {
    issue: "Duplicate invoice detected",
    severity: "Critical"
  },
  {
    issue: "Unusual payment pattern",
    severity: "Medium"
  },
  {
    issue: "GST mismatch identified",
    severity: "High"
  }
];

export default function ComplianceViolations() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          Compliance Violations
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          AI-detected accounting policy issues
        </p>
      </div>

      <div className="space-y-4">
        
        {violations.map((item) => (
          <div
            key={item.issue}
            className="bg-slate-900 rounded-xl p-4 flex items-center justify-between"
          >
            <div>
              <h3 className="font-medium">
                {item.issue}
              </h3>

              <p className="text-sm text-slate-400 mt-1">
                Autonomous audit review
              </p>
            </div>

            <span
              className={`
                px-3
                py-2
                rounded-xl
                text-sm
                ${
                  item.severity === "Critical"
                    ? "bg-red-600 text-white"
                    : item.severity === "High"
                    ? "bg-orange-500 text-white"
                    : "bg-yellow-500 text-black"
                }
              `}
            >
              {item.severity}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}