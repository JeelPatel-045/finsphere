"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
  LayoutDashboard,
  MessageSquare,
  ShieldAlert,
  TrendingUp,
  Database,
  FileText,
  Bot,
  Settings
} from "lucide-react";

const menuItems = [
  {
    label: "Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard
  },
  {
    label: "AI Chat",
    href: "/chat",
    icon: MessageSquare
  },
  {
    label: "Audit Center",
    href: "/audit",
    icon: ShieldAlert
  },
  {
    label: "Forecasting",
    href: "/forecasting",
    icon: TrendingUp
  },
  {
    label: "SQL Agent",
    href: "/sql-agent",
    icon: Database
  },
  {
    label: "Documents",
    href: "/documents",
    icon: FileText
  },
  {
    label: "Agents",
    href: "/agents",
    icon: Bot
  },
  {
    label: "Settings",
    href: "/settings",
    icon: Settings
  }
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[260px] bg-[#111827] border-r border-slate-800 flex flex-col">
      
      {/* LOGO */}
      <div className="h-20 flex items-center px-6 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-bold text-white">
            FinSphere AI
          </h1>

          <p className="text-xs text-slate-400 mt-1">
            Finance Copilot
          </p>
        </div>
      </div>

      {/* MENU */}
      <nav className="flex-1 px-4 py-6 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon;

          const active = pathname === item.href;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200
              
              ${
                active
                  ? "bg-blue-600 text-white shadow-lg"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              <Icon size={20} />

              <span className="font-medium">
                {item.label}
              </span>
            </Link>
          );
        })}
      </nav>

      {/* FOOTER */}
      <div className="p-4 border-t border-slate-800">
        <div className="rounded-2xl bg-slate-900 p-4">
          
          <p className="text-sm text-slate-400">
            Active Agents
          </p>

          <h2 className="text-2xl font-bold mt-2">
            6
          </h2>

          <div className="mt-4 flex gap-2">
            <span className="h-3 w-3 rounded-full bg-green-500" />
            <span className="text-xs text-slate-400">
              All Systems Operational
            </span>
          </div>
        </div>
      </div>
    </aside>
  );
}