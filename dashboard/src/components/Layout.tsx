import { useState, useEffect, createContext, useContext } from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import {
  LayoutDashboard,
  BarChart3,
  FileText,
  Globe,
  MessageSquare,
  Users,
  Database,
  Shield,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';
import { cn } from '../lib/utils';
import { fetchCycles } from '../lib/api';

interface CycleContextValue {
  cycle: number;
  setCycle: (c: number) => void;
  cycles: number[];
}

export const CycleContext = createContext<CycleContextValue>({
  cycle: 1,
  setCycle: () => {},
  cycles: [],
});

export function useCycle() {
  return useContext(CycleContext);
}

const NAV_ITEMS = [
  { to: '/', icon: LayoutDashboard, label: 'Overview' },
  { to: '/priorities', icon: BarChart3, label: 'Prioridades ANP' },
  { to: '/sector-plans', icon: FileText, label: 'Planes Sectoriales' },
  { to: '/global-plan', icon: Globe, label: 'Plan Consolidado' },
  { to: '/communication', icon: MessageSquare, label: 'Comunicacion' },
  { to: '/segments', icon: Users, label: 'Segmentos' },
  { to: '/corpus', icon: Database, label: 'Corpus' },
  { to: '/audit', icon: Shield, label: 'Auditoria' },
];

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false);
  const [cycles, setCycles] = useState<number[]>([1]);
  const [cycle, setCycle] = useState(1);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  useEffect(() => {
    fetchCycles()
      .then((data) => {
        const arr = Array.isArray(data) ? (data as number[]) : [1];
        setCycles(arr);
        if (arr.length > 0) setCycle(arr[arr.length - 1]);
      })
      .catch(() => {
        setCycles([1]);
      });
  }, []);

  return (
    <CycleContext.Provider value={{ cycle, setCycle, cycles }}>
      <div className="flex h-screen overflow-hidden">
        {/* Sidebar */}
        <aside
          className={cn(
            'glass-card flex flex-col shrink-0 transition-all duration-300 rounded-none border-t-0 border-b-0 border-l-0',
            collapsed ? 'w-16' : 'w-60',
          )}
        >
          {/* Logo area */}
          <div className="flex items-center gap-3 px-4 h-16 border-b border-white/5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center shrink-0">
              <span className="text-white font-bold text-sm">A</span>
            </div>
            {!collapsed && (
              <span className="font-semibold text-[var(--text-primary)] tracking-tight whitespace-nowrap">
                ANPEGT-POL
              </span>
            )}
          </div>

          {/* Nav items */}
          <nav className="flex-1 py-3 flex flex-col gap-0.5 px-2 overflow-y-auto">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                    isActive
                      ? 'bg-blue-500/15 text-blue-400'
                      : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5',
                    collapsed && 'justify-center px-0',
                  )
                }
              >
                <item.icon className="w-5 h-5 shrink-0" />
                {!collapsed && <span className="whitespace-nowrap">{item.label}</span>}
              </NavLink>
            ))}
          </nav>

          {/* Collapse button */}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex items-center justify-center h-12 border-t border-white/5 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </aside>

        {/* Main area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <header className="flex items-center justify-between px-6 h-16 border-b border-white/5 shrink-0">
            <h1 className="text-lg font-semibold text-[var(--text-primary)]">
              Centro de Control Estrategico
            </h1>
            <div className="relative">
              <button
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="flex items-center gap-2 px-4 py-2 rounded-lg glass-card text-sm text-[var(--text-primary)] hover:bg-[var(--bg-card-hover)] transition-colors"
              >
                Ciclo {cycle}
                <ChevronDown className="w-4 h-4 text-[var(--text-secondary)]" />
              </button>
              {dropdownOpen && (
                <div className="absolute right-0 top-full mt-1 glass-card py-1 min-w-[120px] z-50">
                  {cycles.map((c) => (
                    <button
                      key={c}
                      onClick={() => {
                        setCycle(c);
                        setDropdownOpen(false);
                      }}
                      className={cn(
                        'block w-full text-left px-4 py-2 text-sm transition-colors',
                        c === cycle
                          ? 'text-blue-400 bg-blue-500/10'
                          : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-white/5',
                      )}
                    >
                      Ciclo {c}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </header>

          {/* Content */}
          <main className="flex-1 overflow-y-auto p-6">
            <Outlet />
          </main>
        </div>
      </div>
    </CycleContext.Provider>
  );
}
