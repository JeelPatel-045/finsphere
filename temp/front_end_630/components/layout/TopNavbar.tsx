"use client";

import {
  Bell,
  Search,
  UserCircle2
} from "lucide-react";

export default function TopNavbar() {
  return (
    <header className="h-20 border-b border-slate-800 bg-[#0F172A] px-6 flex items-center justify-between">
      
      {/* SEARCH */}
      <div className="flex items-center bg-slate-900 border border-slate-800 rounded-xl px-4 h-12 w-[400px]">
        
        <Search className="text-slate-400" size={18} />

        <input
          type="text"
          placeholder="Search transactions, agents, reports..."
          className="bg-transparent outline-none text-sm text-white ml-3 w-full"
        />
      </div>

      {/* RIGHT */}
      <div className="flex items-center gap-5">
        
        {/* NOTIFICATIONS */}
        <button className="relative">
          <Bell className="text-slate-300" />

          <span className="absolute -top-1 -right-1 h-2 w-2 rounded-full bg-red-500" />
        </button>

        {/* PROFILE */}
        <div className="flex items-center gap-3">
          
          <UserCircle2
            size={38}
            className="text-slate-300"
          />

          <div>
            <h3 className="text-sm font-semibold">
              Finance Admin
            </h3>

            <p className="text-xs text-slate-400">
              Enterprise Workspace
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}