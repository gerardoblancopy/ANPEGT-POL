import { useState } from 'react'
import { Search, X } from 'lucide-react'
import type { BookDoc } from '../types'
import { sectionRange } from '../lib/model'

interface Props {
  doc: BookDoc
  activeId: string | null
  open: boolean
  onClose: () => void
  onNavigate: (id: string) => void
}

export function StructureIndex({ doc, activeId, open, onClose, onNavigate }: Props) {
  const [query, setQuery] = useState('')
  const q = query.trim().toLowerCase()

  return (
    <>
      {open && <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={onClose} />}
      <aside
        className={`surface thin-scroll fixed top-0 z-40 h-dvh w-[20rem] shrink-0 overflow-y-auto border-r p-4 transition-transform lg:sticky lg:top-14 lg:z-0 lg:h-[calc(100dvh-3.5rem)] lg:translate-x-0 ${open ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="mb-3 flex items-center justify-between lg:hidden">
          <span className="text-sm font-bold uppercase tracking-wider text-soft">Estructura</span>
          <button onClick={onClose} aria-label="Cerrar"><X size={20} /></button>
        </div>

        <div className="surface-2 mb-4 flex items-center gap-2 rounded-lg px-3 py-2">
          <Search size={15} className="opacity-50" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar sección…"
            className="w-full bg-transparent text-sm outline-none placeholder:text-soft"
            style={{ color: 'var(--text)' }}
          />
        </div>

        <nav className="flex flex-col gap-4">
          {doc.chapters.map((chapter) => {
            const sections = q
              ? chapter.sections.filter((s) => s.title.toLowerCase().includes(q))
              : chapter.sections
            if (sections.length === 0) return null
            return (
              <div key={chapter.id}>
                {(chapter.title || chapter.number) && (
                  <div className="mb-1 px-3 text-xs font-bold uppercase tracking-wider text-soft">
                    {chapter.number ? `${chapter.number} · ` : ''}{chapter.title}
                  </div>
                )}
                <ul className="m-0 flex list-none flex-col gap-0.5 p-0">
                  {sections.map((s) => {
                    const active = s.id === activeId
                    const { label } = sectionRange(s)
                    return (
                      <li key={s.id}>
                        <button
                          onClick={() => onNavigate(s.id)}
                          className="flex w-full items-baseline justify-between gap-2 rounded-lg px-3 py-2 text-left text-sm transition-colors"
                          style={active ? { background: 'var(--accent-soft)', color: 'var(--accent)', fontWeight: 600 } : { color: 'var(--text-soft)' }}
                        >
                          <span className="min-w-0 truncate">{s.title}</span>
                          {label && <span className="shrink-0 font-mono text-xs opacity-70">{label}</span>}
                        </button>
                      </li>
                    )
                  })}
                </ul>
              </div>
            )
          })}
        </nav>
      </aside>
    </>
  )
}
