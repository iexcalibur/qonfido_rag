'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import Sidebar from './Sidebar';
import Header from './Header';

interface ConditionalLayoutProps {
  children: React.ReactNode;
}

export default function ConditionalLayout({ children }: ConditionalLayoutProps) {
  const pathname = usePathname();
  
  // Full-page layouts (no sidebar/header)
  const isFullPage = pathname === '/';

  if (isFullPage) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-slate-950">
      <Sidebar />
      <Header />
      <main className="ml-16 md:ml-64 pt-16 min-h-screen">
        {children}
      </main>
    </div>
  );
}
