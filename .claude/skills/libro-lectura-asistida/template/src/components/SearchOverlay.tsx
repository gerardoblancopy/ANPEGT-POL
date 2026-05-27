import { useEffect, useMemo, useRef, useState } from 'react'
import { Search, X } from 'lucide-react'
import type { BookDoc } from '../types'
import { flattenParagraphs } from '../lib/model'

interface Props {
  doc: BookDoc
  open: boolean
  onClose: () => void
  onGoToParagraph: (id: string) => void
  onGoToConcept: (id: string) => void
}

export function SearchOverlay({ doc, open, onClose, onGoToParagraph, onGoToConcept }: Props) {
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const paras = useMemo(() => flattenParagraphs(doc), [doc])
  const concepts = doc.concepts ?? []

  useEffect(() => {
    if (open) {
      setQuery('')
      setTimeout(() => inputRef.current?.focus(), 40)
    }
  }, [open])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    if (open) document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [open, onClose])

  if (!open) return null
  const q = query.trim().toLowerCase()

  const conceptHits = q ? concepts.filter((c) => c.label.toLowerCase().includes(q)).slice(0, 8) : []
  const paraHits = q
    ? paras
        .filter((r) => {
          const p = r.paragraph
          return [p.text, p.synthesis, p.criticalReading, p.technicalContrast]
            .filter(Boolean)
            .some((t) => t!.toLowerCase().includes(q))
        })
        .slice(0, 30)
    : []

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 p-4 pt-[10vh]" onClick={onClose}>
      <div
        className="surface thin-scroll max-h-[78vh] w-full max-w-[40rem] overflow-y-auto rounded-2xl border"
        style={{ boxShadow: 'var(--shadow)' }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="surface sticky top-0 flex items-center gap-2 border-b px-4 py-3">
          <Search size={18} className="opacity-50" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar en el texto y los conceptos…"
            className="w-full bg-transparent text-base outline-none placeholder:text-soft"
            style={{ color: 'var(--text)' }}
          />
          <button onClick={onClose} aria-label="Cerrar" className="opacity-60 hover:opacity-100"><X size={18} /></button>
        </div>

        <div className="p-2">
          {q && conceptHits.length === 0 && paraHits.length === 0 && (
            <p className="px-3 py-6 text-center text-sm text-soft">Sin resultados.</p>
          )}

          {conceptHits.length > 0 && (
            <div className="mb-2">
              <div className="px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-soft">Conceptos</div>
              {conceptHits.map((c) => (
                <button
                  key={c.id}
                  onClick={() => onGoToConcept(c.id)}
                  className="block w-full rounded-lg px-3 py-2 text-left text-sm hover:opacity-80"
                  style={{ color: 'var(--accent)' }}
                >
                  {c.label}
                </button>
              ))}
            </div>
          )}

          {paraHits.length > 0 && (
            <div>
              <div className="px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-soft">Párrafos</div>
              {paraHits.map((r) => (
                <button
                  key={r.paragraph.id}
                  onClick={() => onGoToParagraph(r.paragraph.id)}
                  className="block w-full rounded-lg px-3 py-2 text-left hover:bg-[var(--surface-2)]"
                >
                  <span className="mr-2 font-mono text-xs text-soft">{r.paragraph.number ?? ''}</span>
                  <span className="text-sm">{r.paragraph.text.slice(0, 110)}{r.paragraph.text.length > 110 ? '…' : ''}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
