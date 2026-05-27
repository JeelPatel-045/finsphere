"use client";

const data = [
  {
    account: "Marketing Expense",
    amount: "$48,000",
    quarter: "Q4",
    risk: "Low"
  },
  {
    account: "Vendor Payments",
    amount: "$92,000",
    quarter: "Q4",
    risk: "High"
  },
  {
    account: "Travel Expense",
    amount: "$24,500",
    quarter: "Q4",
    risk: "Medium"
  },
  {
    account: "Software Licenses",
    amount: "$18,200",
    quarter: "Q4",
    risk: "Low"
  }
];

export default function QueryResultsTable() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          Query Results
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          AI-generated finance analytics dataset
        </p>
      </div>

      <div className="overflow-x-auto">
        
        <table className="w-full">
          
          <thead>
            <tr className="border-b border-slate-800 text-left">
              
              <th className="pb-4 text-slate-400 font-medium">
                Account
              </th>

              <th className="pb-4 text-slate-400 font-medium">
                Amount
              </th>

              <th className="pb-4 text-slate-400 font-medium">
                Quarter
              </th>

              <th className="pb-4 text-slate-400 font-medium">
                Risk Level
              </th>
            </tr>
          </thead>

          <tbody>
            
            {data.map((row, index) => (
              <tr
                key={index}
                className="border-b border-slate-900"
              >
                <td className="py-5 text-slate-200">
                  {row.account}
                </td>

                <td className="py-5 text-slate-200">
                  {row.amount}
                </td>

                <td className="py-5 text-slate-300">
                  {row.quarter}
                </td>

                <td className="py-5">
                  
                  <span
                    className={`
                      px-3
                      py-2
                      rounded-xl
                      text-sm
                      ${
                        row.risk === "High"
                          ? "bg-red-500 text-white"
                          : row.risk === "Medium"
                          ? "bg-yellow-500 text-black"
                          : "bg-green-500 text-white"
                      }
                    `}
                  >
                    {row.risk}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}