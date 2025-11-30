'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Sparkles, Search } from 'lucide-react';

export default function Header() {
  const pathname = usePathname();
  const isDashboard = pathname === '/';
  
  const navItems = [
    { icon: Sparkles, label: 'AI Co-Pilot', href: '/chat' },
    { icon: Search, label: 'Fund Explorer', href: '/funds' },
  ];

  const isActive = (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname.startsWith(href);
  };

  const isDashboardActive = pathname === '/';

  return (
    <header className="w-full fixed top-0 left-0 z-50 bg-transparent">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          
          <Link 
            href="/" 
            className={`flex items-center gap-3 font-bold text-xl tracking-tight transition-all duration-200 rounded-lg px-3 py-2 ${
              isDashboardActive
                ? 'text-white'
                : 'text-white hover:opacity-80'
            }`}
          >
            <div className={`w-8 h-8 rounded-lg bg-gradient-to-tr from-indigo-600 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20 ring-1 ring-white/10 transition-all ${
              isDashboardActive ? 'ring-2 ring-indigo-500/50' : ''
            }`}>
              <span className="text-white font-mono">Q</span>
            </div>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
              Qonfido
            </span>
          </Link>

          {isDashboard && (
            <nav className="hidden md:flex items-center gap-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`group flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 border border-transparent ${
                      active
                        ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20 shadow-[0_0_15px_-3px_rgba(99,102,241,0.2)]'
                        : 'text-slate-500 hover:text-slate-200 hover:bg-white/5'
                    }`}
                  >
                    <Icon size={18} className={active ? 'text-indigo-400' : 'text-slate-500 group-hover:text-slate-300'} />
                    <span className="font-medium text-sm">{item.label}</span>
                  </Link>
                );
              })}
            </nav>
          )}

          {!isDashboard && <div className="hidden md:block w-[120px]"></div>}
        </div>
      </div>
    </header>
  );
}
