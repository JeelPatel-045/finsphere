"use client";

const transactions = [
  {
    id: "TXN-8421",
    vendor: "Global Vendor Ltd",
    amount: "₹4,82,000",
    risk: "High"
  },
  {
    id: "TXN-8422",
    vendor: "TechNova Systems",
    amount: "₹8,14,500",
    risk: "Critical"
  },
  {
    id: "TXN-8423",
    vendor: "Apex Consulting",
    amount: "₹2,10,000",
    risk: "Medium"
  }
];

export default function SuspiciousTransactions() {
  return (
    <div className="bg-[#111827] border border-slate-800 rounded-2xl p-6">
      
      <div className="mb-6">
        
        <h2 className="text-xl font-semibold">
          Suspicious Transactions
        </h2>

        <p className="text-sm text-slate-400 mt-1">
          AI anomaly detection engine output
        </p>
      </div>

      <div className="space-y-4">
        
        {transactions.map((txn) => (
          <div
            key={txn.id}
            className="bg-slate-900 rounded-xl p-4"
          >
            <div className="flex items-center justify-between">
              
              <div>
                <h3 className="font-semibold">
                  {txn.id}
                </h3>

                <p className="text-sm text-slate-400 mt-1">
                  {txn.vendor}
                </p>
              </div>

              <div className="text-right">
                
                <h3 className="font-semibold">
                  {txn.amount}
                </h3>

                <span
                  className={`
                    inline-block
                    mt-2
                    px-3
                    py-1
                    rounded-lg
                    text-xs
                    ${
                      txn.risk === "Critical"
                        ? "bg-red-600 text-white"
                        : txn.risk === "High"
                        ? "bg-orange-500 text-white"
                        : "bg-yellow-500 text-black"
                    }
                  `}
                >
                  {txn.risk}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}