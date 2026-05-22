'use client';
import { useState, useEffect, useCallback, memo } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  ShieldAlert,
  LayoutDashboard,
  ListFilter,
  BarChart3,
  Terminal,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Activity,
  Wifi,
  Globe,
} from 'lucide-react';
import { clearAuth, getUser, AuthUser } from '@/lib/auth';

const NAV = [
  { href: '/dashboard',  label: 'Dashboard',  icon: LayoutDashboard,  desc: 'Overview & stats'     },
  { href: '/events',     label: 'Events',      icon: ListFilter,       desc: 'Anomaly feed'         },
  { href: '/analytics',  label: 'Analytics',   icon: BarChart3,        desc: 'ML insights'          },
  { href: '/agents',     label: 'Agents',      icon: Terminal,         desc: 'Endpoint connectors'  },
  { href: '/settings',   label: 'Settings',    icon: Settings,         desc: 'Platform config'      },
];

function Sidebar() {
  const pathname   = usePathname();
  const router     = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  // Defer localStorage read to client to avoid SSR/hydration mismatch
  const [user, setUser] = useState<AuthUser | null>(null);
  useEffect(() => { setUser(getUser()); }, []);

  const handleLogout = useCallback(() => {
    clearAuth();
    router.replace('/login');
  }, [router]);

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 240 }}
      transition={{ duration: 0.25, ease: 'easeInOut' }}
      className="relative flex flex-col h-screen bg-[#080f1e] border-r border-white/[0.06] shrink-0 overflow-hidden z-20"
    >
      {/* Top logo — click to go home */}
      <Link href="/" className="flex items-center gap-3 px-4 h-16 border-b border-white/[0.06] shrink-0 group hover:bg-white/[0.025] transition-colors">
        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-700 flex items-center justify-center shadow-lg shadow-blue-500/20 shrink-0 group-hover:shadow-blue-500/40 transition-shadow">
          <ShieldAlert size={16} className="text-white" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -8 }}
              transition={{ duration: 0.18 }}
              className="min-w-0 flex-1"
            >
              <p className="text-white font-black text-sm tracking-tight leading-none">
                SENTINEL<span className="text-blue-400">CORE</span>
              </p>
              <p className="text-[9px] text-slate-600 font-mono tracking-wider uppercase mt-0.5 group-hover:text-slate-500 transition-colors">
                ← Back to site
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </Link>

      {/* Nav links */}
      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto overflow-x-hidden">
        {NAV.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(href + '/');
          return (
            <Link key={href} href={href}>
              <motion.div
                whileHover={{ x: collapsed ? 0 : 3 }}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-colors relative group ${
                  active
                    ? 'bg-blue-600/15 text-blue-400'
                    : 'text-slate-500 hover:text-slate-300 hover:bg-white/[0.04]'
                }`}
              >
                {active && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-blue-400 rounded-full"
                  />
                )}
                <Icon size={18} className="shrink-0" />
                <AnimatePresence>
                  {!collapsed && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.15 }}
                      className="text-xs font-semibold tracking-wide whitespace-nowrap"
                    >
                      {label}
                    </motion.span>
                  )}
                </AnimatePresence>

                {/* Tooltip on collapse */}
                {collapsed && (
                  <div className="absolute left-full ml-3 px-2.5 py-1.5 bg-[#0d1b2e] border border-white/10 rounded-lg text-xs text-white font-medium whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 shadow-xl">
                    {label}
                  </div>
                )}
              </motion.div>
            </Link>
          );
        })}
      </nav>

      {/* Bottom section */}
      <div className="px-2 pb-4 space-y-1 border-t border-white/[0.06] pt-3 shrink-0">
        {/* System status */}
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center gap-2 px-3 py-2 mb-1"
            >
              <Wifi size={11} className="text-emerald-400" />
              <span className="text-[10px] text-emerald-400 font-mono tracking-wider">ONLINE</span>
              <Activity size={11} className="text-slate-600 ml-auto" />
            </motion.div>
          )}
        </AnimatePresence>

        {/* User pill */}
        <div className={`flex items-center gap-3 px-3 py-2.5 rounded-xl bg-white/[0.03] ${collapsed ? 'justify-center' : ''}`}>
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-[11px] font-black text-white uppercase shrink-0">
            {user?.username?.[0] ?? 'A'}
          </div>
          <AnimatePresence>
            {!collapsed && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex-1 min-w-0"
              >
                <p className="text-xs font-semibold text-white truncate">{user?.username ?? 'admin'}</p>
                <p className="text-[10px] text-slate-600 uppercase tracking-wider">{user?.role ?? 'analyst'}</p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Back to landing site */}
        <Link
          href="/"
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-500 hover:text-blue-300 hover:bg-blue-500/[0.08] transition-colors group relative ${collapsed ? 'justify-center' : ''}`}
        >
          <Globe size={15} className="shrink-0" />
          <AnimatePresence>
            {!collapsed && (
              <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="text-xs font-semibold">
                Back to Site
              </motion.span>
            )}
          </AnimatePresence>
          {collapsed && (
            <div className="absolute left-full ml-3 px-2.5 py-1.5 bg-[#0d1b2e] border border-white/10 rounded-lg text-xs text-white font-medium whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 shadow-xl">
              Back to Site
            </div>
          )}
        </Link>

        {/* Logout */}
        <button
          onClick={handleLogout}
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-600 hover:text-red-400 hover:bg-red-500/[0.08] transition-colors group relative ${collapsed ? 'justify-center' : ''}`}
        >
          <LogOut size={16} className="shrink-0" />
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-xs font-semibold"
              >
                Sign Out
              </motion.span>
            )}
          </AnimatePresence>
          {collapsed && (
            <div className="absolute left-full ml-3 px-2.5 py-1.5 bg-[#0d1b2e] border border-white/10 rounded-lg text-xs text-white font-medium whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 shadow-xl">
              Sign Out
            </div>
          )}
        </button>
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(v => !v)}
        className="absolute top-[54px] -right-3 w-6 h-6 rounded-full bg-[#0d1b2e] border border-white/10 flex items-center justify-center text-slate-500 hover:text-white hover:border-blue-500/40 transition-colors z-30 shadow-lg"
      >
        {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>
    </motion.aside>
  );
}

// Memoised: Sidebar never re-renders on page navigation unless user/collapsed changes
export default memo(Sidebar);
