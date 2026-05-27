import "./globals.css";
import React from "react";
import { Inter } from "next/font/google";
import Sidebar from "@/components/layout/Sidebar";
import TopNavbar from "@/components/layout/TopNavbar";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "FinSphere AI",
  description: "Multi-Model Agentic Finance Copilot"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.className} bg-background text-foreground`}
      >
        <div className="flex h-screen overflow-hidden">
          
          <Sidebar />

          <div className="flex flex-1 flex-col">
            <TopNavbar />

            <main className="flex-1 overflow-y-auto p-6">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}