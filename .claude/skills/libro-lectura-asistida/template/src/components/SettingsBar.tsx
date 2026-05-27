import { BookMarked, List, Minus, Moon, Plus, Sun, Type } from 'lucide-react'
import type { Theme } from '../App'

interface Props {
  title: string
  theme: Theme
  setTheme: (t: Theme) => void
  scale: number
  setScale: (s: number) => void
  hasGlossary: boolean
  onToggleSidebar: () => void
  onToggleGlossary: () => void
}

const THEMES: { id: Theme; icon: typeof Sun; label: string }[] = [
  { id: 'light', icon: Sun, label: 'Claro' },
  { id: 'sepia', icon: BookMarked, label: 'Sepia' },
  { id: 'dark', icon: Moon, label: 'Oscuro' },
]

export function SettingsBar({
  title, theme, setTheme, scale, setScale, hasGlossary, onToggleSidebar, onToggleGlossary,
}: Props) {
  const iconBtn = 'flex h-9 w-9 items-center justify-center rounded-lg transition-colors hover:opacity-100 opacity-70'
  return (
    <header
      className="surface sticky top-0 z-20 flex h-14 items-center gap-2 border-b px-3 sm:px-5"
      style={{ background: 'color-mix(in srgb, var(--surface) 86%, transparent)', backdropFilter: 'blur(10px)' }}
    >
      <button className={`${iconBtn} lg:hidden`} onClick={onToggleSidebar} aria-label="Índice">
        <List size={20} />
      </button>

      <div className="min-w-0 flex-1 truncate text-sm font-semibold sm:text-base">{title}</div>

      {/* Tamaño de letra */}
      <div className="surface-2 hidden items-center rounded-lg sm:flex">
        <button className={iconBtn} onClick={() => setScale(Math.max(0.8, +(scale - 0.1).toFixed(2)))} aria-label="Reducir letra">
          <Minus size={16} />
        </button>
        <Type size={15} className="opacity-60" />
        <button className={iconBtn} onClick={() => setScale(Math.min(1.6, +(scale + 0.1).toFixed(2)))} aria-label="Aumentar letra">
          <Plus size={16} />
        </button>
      </div>

      {/* Tema */}
      <div className="surface-2 flex items-center rounded-lg p-0.5">
        {THEMES.map(({ id, icon: Icon, label }) => (
          <button
            key={id}
            onClick={() => setTheme(id)}
            aria-label={label}
            aria-pressed={theme === id}
            className="flex h-8 w-8 items-center justify-center rounded-md transition-colors"
            style={theme === id ? { background: 'var(--accent-soft)', color: 'var(--accent)' } : { opacity: 0.6 }}
          >
            <Icon size={16} />
          </button>
        ))}
      </div>

      {hasGlossary && (
        <button
          onClick={onToggleGlossary}
          className="surface-2 flex h-9 items-center gap-1.5 rounded-lg px-3 text-sm font-medium opacity-80 transition-opacity hover:opacity-100"
          aria-label="Glosario"
        >
          <BookMarked size={16} /> <span className="hidden sm:inline">Glosario</span>
        </button>
      )}
    </header>
  )
}
