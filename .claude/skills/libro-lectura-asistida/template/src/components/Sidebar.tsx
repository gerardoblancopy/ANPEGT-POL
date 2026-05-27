import { useState } from 'react'
import { Search, X } from 'lucide-react'
import type { Chapter } from '../types'

interface Props {
  chapters: Chapter[]
  activeId: string | null
  open: boolean
  onClose: () => void
  onNavigate: (id: string) => void
}

export function Sidebar({ chapters, activeId, open, onClose, onNavigate }: Props) {
  const [query, setQuery] = useState('')
  const q = query.trim().toLowerCase()
  const filtered = q
    ? chapters.filter(
        (c) =>
          c.title.toLowerCase().includes(q) ||
          (c.number ?? '').toLowerCase().includes(q) ||
          (c.summary ?? '').toLowerCase().includes(q),
      )
    : chapters

  return (
    <>
      {open && <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={onClose} />}
      <aside
        className={`surface thin-scroll fixed top-0 z-40 h-dvh w-[19rem] shrink-0 overflow-y-auto border-r p-4 transition-transform lg:sticky lg:top-14 lg:z-0 lg:h-[calc(100dvh-3.5rem)] lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="mb-3 flex items-center justify-between lg:hidden">
          <span className="text-sm font-bold uppercase tracking-wider text-soft">Índice</span>
          <button onClick={onClose} aria-label="Cerrar"><X size={20} /></button>
        </div>

        <div className="surface-2 mb-4 flex items-center gap-2 rounded-lg px-3 py-2">
          <Search size={15} className="opacity-50" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar capítulo…"
            className="w-full bg-transparent text-sm outline-none placeholder:text-soft"
            style={{ color: 'var(--text)' }}
          />
        </div>

        <nav>
          <ul className="m-0 flex list-none flex-col gap-0.5 p-0">
            {filtered.map((c) => {
              const active = c.id === activeId
              return (
                <li key={c.id}>
                  <button
                    onClick={() => onNavigate(c.id)}
                    className="block w-full rounded-lg px-3 py-2 text-left text-sm transition-colors"
                    style={
                      active
                        ? { background: 'var(--accent-soft)', color: 'var(--accent)', fontWeight: 600 }
                        : { color: 'var(--text-soft)' }
                    }
                  >
                    {c.number && <span className="mr-1.5 text-xs opacity-70">{c.number}</span>}
                    {c.title}
                  </button>
                </li>
              )
            })}
            {filtered.length === 0 && (
              <li className="px-3 py-2 text-sm text-soft">Sin resultados.</li>
            )}
          </ul>
        </nav>
      </aside>
    </>
  )
}
