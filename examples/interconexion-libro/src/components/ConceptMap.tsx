import { useMemo, useState } from 'react'
import { ChevronRight } from 'lucide-react'
import type { BookDoc } from '../types'
import { conceptParagraphIndex } from '../lib/model'

interface Props {
  doc: BookDoc
  onSelectConcept: (id: string) => void
}

export function ConceptMap({ doc, onSelectConcept }: Props) {
  const concepts = doc.concepts ?? []
  const types = doc.conceptTypes ?? []
  const index = useMemo(() => conceptParagraphIndex(doc), [doc])
  const [typeFilter, setTypeFilter] = useState<string | null>(null)

  const countByType = useMemo(() => {
    const m = new Map<string, number>()
    for (const c of concepts) m.set(c.type, (m.get(c.type) ?? 0) + 1)
    return m
  }, [concepts])

  const visible = typeFilter ? concepts.filter((c) => c.type === typeFilter) : concepts
  const typeLabel = (id: string) => types.find((t) => t.id === id)?.label ?? id
  const typeGlyph = (id: string) => types.find((t) => t.id === id)?.glyph
  const typeColor = (id: string) => types.find((t) => t.id === id)?.color ?? 'var(--accent)'

  return (
    <div className="mx-auto max-w-[46rem] py-4">
      <div className="mb-10 text-center">
        <div className="mb-2 text-xs font-semibold uppercase tracking-[0.22em] text-soft">Segundo índice del sitio</div>
        <h1 className="text-4xl font-bold sm:text-5xl">Mapa conceptual</h1>
        <p className="mx-auto mt-5 max-w-[34rem] leading-relaxed text-soft">
          Conceptos transversales que atraviesan el documento, agrupados por tipo. Cada concepto
          enlaza a los párrafos donde aparece, y desde cualquier párrafo se vuelve a sus conceptos.
        </p>
        <p className="mt-4 font-mono text-sm text-soft">
          {concepts.length} conceptos · {types.length} tipos · extraídos del corpus completo
        </p>
      </div>

      <div className="mb-9 flex flex-wrap justify-center gap-2">
        <Chip active={typeFilter === null} onClick={() => setTypeFilter(null)} label="Todos" count={concepts.length} />
        {types.map((t) => (
          <Chip
            key={t.id}
            active={typeFilter === t.id}
            color={t.color}
            glyph={t.glyph}
            onClick={() => setTypeFilter(typeFilter === t.id ? null : t.id)}
            label={t.label}
            count={countByType.get(t.id) ?? 0}
          />
        ))}
      </div>

      <div className="flex flex-col gap-3">
        {visible.map((c) => {
          const refs = index.get(c.id) ?? []
          return (
            <button
              key={c.id}
              onClick={() => onSelectConcept(c.id)}
              className="surface flex items-center gap-3 rounded-xl border p-4 text-left transition-colors hover:border-[var(--accent)]"
            >
              <span className="min-w-0 flex-1">
                <span className="flex items-center gap-2">
                  {typeGlyph(c.type) && <span aria-hidden style={{ color: typeColor(c.type) }}>{typeGlyph(c.type)}</span>}
                  <span className="text-lg font-semibold">{c.label}</span>
                  <span className="rounded-full px-2 py-0.5 text-xs" style={{ background: 'var(--surface-2)', color: 'var(--text-soft)' }}>
                    {typeLabel(c.type)}
                  </span>
                </span>
                {(c.summary || c.tagline) && (
                  <span className="mt-1 block text-[0.95rem] leading-relaxed text-soft">{c.summary ?? c.tagline}</span>
                )}
              </span>
              <span className="flex shrink-0 items-center gap-2 font-mono text-sm text-soft">
                {refs.length}
                <ChevronRight size={16} />
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

function Chip({
  active, label, count, color, glyph, onClick,
}: {
  active: boolean
  label: string
  count: number
  color?: string
  glyph?: string
  onClick: () => void
}) {
  const c = color || 'var(--accent)'
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1.5 rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors"
      style={active ? { background: c, color: '#fff', borderColor: c } : { color: 'var(--text)', borderColor: 'var(--border)' }}
    >
      {glyph && <span aria-hidden style={active ? undefined : { color: c }}>{glyph}</span>}
      {label}
      <span className="rounded-full px-1.5 text-xs" style={{ background: active ? 'rgba(255,255,255,.25)' : 'var(--surface-2)' }}>
        {count}
      </span>
    </button>
  )
}
