import { BookMarked, BookOpen, List, Minus, Moon, Network, Plus, Search, Sun, Type } from 'lucide-react'
import type { DocMeta } from '../types'
import type { Theme } from '../App'

export type View = 'reading' | 'concepts'

interface Props {
  meta: DocMeta
  view: View
  setView: (v: View) => void
  hasConcepts: boolean
  theme: Theme
  setTheme: (t: Theme) => void
  scale: number
  setScale: (s: number) => void
  onToggleSidebar: () => void
  onOpenSearch: () => void
}

const THEMES: { id: Theme; icon: typeof Sun }[] = [
  { id: 'light', icon: Sun },
  { id: 'sepia', icon: BookMarked },
  { id: 'dark', icon: Moon },
]

export function TopBar({
  meta, view, setView, hasConcepts, theme, setTheme, scale, setScale, onToggleSidebar, onOpenSearch,
}: Props) {
  const iconBtn = 'flex h-9 w-9 items-center justify-center rounded-lg opacity-70 transition-opacity hover:opacity-100'
  return (
    <header
      className="surface sticky top-0 z-20 flex h-14 items-center gap-2 border-b px-3 sm:px-5"
      style={{ background: 'color-mix(in srgb, var(--surface) 86%, transparent)', backdropFilter: 'blur(10px)' }}
    >
      {view === 'reading' && (
        <button className={`${iconBtn} lg:hidden`} onClick={onToggleSidebar} aria-label="Estructura">
          <List size={20} />
        </button>
      )}

      <div className="min-w-0 flex-1">
        <div className="truncate font-bold leading-tight">{meta.title}</div>
        {meta.subtitle && <div className="truncate text-xs text-soft">{meta.subtitle}</div>}
      </div>

      {/* Tamaño de letra */}
      <div className="surface-2 hidden items-center rounded-lg sm:flex">
        <button className={iconBtn} onClick={() => setScale(Math.max(0.8, +(scale - 0.1).toFixed(2)))} aria-label="Reducir letra"><Minus size={16} /></button>
        <Type size={15} className="opacity-60" />
        <button className={iconBtn} onClick={() => setScale(Math.min(1.6, +(scale + 0.1).toFixed(2)))} aria-label="Aumentar letra"><Plus size={16} /></button>
      </div>

      {/* Tema */}
      <div className="surface-2 flex items-center rounded-lg p-0.5">
        {THEMES.map(({ id, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setTheme(id)}
            aria-pressed={theme === id}
            className="flex h-8 w-8 items-center justify-center rounded-md transition-colors"
            style={theme === id ? { background: 'var(--accent-soft)', color: 'var(--accent)' } : { opacity: 0.6 }}
          >
            <Icon size={16} />
          </button>
        ))}
      </div>

      {/* Vistas: lectura / mapa conceptual */}
      {hasConcepts && (
        <div className="surface-2 flex items-center rounded-lg p-0.5">
          <button
            onClick={() => setView('reading')}
            aria-label="Lectura"
            aria-pressed={view === 'reading'}
            className="flex h-8 w-8 items-center justify-center rounded-md"
            style={view === 'reading' ? { background: 'var(--accent-soft)', color: 'var(--accent)' } : { opacity: 0.6 }}
          >
            <BookOpen size={16} />
          </button>
          <button
            onClick={() => setView('concepts')}
            aria-label="Mapa conceptual"
            aria-pressed={view === 'concepts'}
            className="flex h-8 w-8 items-center justify-center rounded-md"
            style={view === 'concepts' ? { background: 'var(--accent-soft)', color: 'var(--accent)' } : { opacity: 0.6 }}
          >
            <Network size={16} />
          </button>
        </div>
      )}

      <button className={iconBtn} onClick={onOpenSearch} aria-label="Buscar"><Search size={18} /></button>
    </header>
  )
}
