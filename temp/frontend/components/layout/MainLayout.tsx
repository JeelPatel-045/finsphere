"use client";

interface MainLayoutProps {
  title: string;
  description?: string;
  children: React.ReactNode;
}

export default function MainLayout({
  title,
  description,
  children
}: MainLayoutProps) {
  return (
    <div className="space-y-6">
      
      {/* PAGE HEADER */}
      <div>
        <h1 className="text-3xl font-bold text-white">
          {title}
        </h1>

        {description && (
          <p className="text-slate-400 mt-2">
            {description}
          </p>
        )}
      </div>

      {/* CONTENT */}
      <div>
        {children}
      </div>
    </div>
  );
}