import { useMemo } from 'react'
import { ArrowLeft, ArrowUpRight } from 'lucide-react'
import type { BookDoc, ConceptType } from '../types'
import { conceptParagraphIndex } from '../lib/model'
import { inlineFormat } from '../lib/markdown'

const GLOSS_PALETTE = ['var(--g1)', 'var(--g2)', 'var(--g3)', 'var(--accent)']

interface Props {
  doc: BookDoc
  conceptId: string
  conceptType: (id: string) => ConceptType | undefined
  onOpenParagraph: (id: string) => void
  onSelectConcept: (id: string) => void
  onBackToMap: () => void
}

export function ConceptDetail({ doc, conceptId, conceptType, onOpenParagraph, onSelectConcept, onBackToMap }: Props) {
  const concept = (doc.concepts ?? []).find((c) => c.id === conceptId)
  const index = useMemo(() => conceptParagraphIndex(doc), [doc])
  if (!concept) return null

  const t = conceptType(concept.id)
  const color = t?.color ?? 'var(--accent)'
  const appearances = index.get(concept.id) ?? []

  return (
    <div className="mx-auto max-w-[44rem] px-5 py-8 sm:px-8">
      <button onClick={onBackToMap} className="mb-6 flex items-center gap-1.5 text-sm text-soft hover:text-[var(--accent)]">
        <ArrowLeft size={15} /> Mapa conceptual
      </button>

      <header>
        <h1 className="text-4xl font-bold leading-tight sm:text-5xl">{concept.label}</h1>
        {concept.tagline && <p className="mt-3 text-lg italic text-soft">{concept.tagline}</p>}
        <div className="mt-5 h-0.5 w-full rounded" style={{ background: color }} />
      </header>

      {(concept.definition || concept.summary) && (
        <section className="mt-8">
          <div className="mb-3 text-xs font-bold uppercase tracking-[0.15em] text-soft">Definición</div>
          <p className="prose-reading m-0">{inlineFormat(concept.definition ?? concept.summary ?? '')}</p>
        </section>
      )}

      {concept.glosses && concept.glosses.length > 0 && (
        <div className="mt-8 flex flex-col gap-4">
          {concept.glosses.map((g, i) => {
            const gc = g.color ?? GLOSS_PALETTE[i % GLOSS_PALETTE.length]
            return (
              <section key={i} className="surface rounded-xl border border-l-[3px] p-5" style={{ borderLeftColor: gc }}>
                <div className="mb-2 text-xs font-bold uppercase tracking-wider" style={{ color: gc }}>{g.label}</div>
                <p className="m-0 leading-relaxed">{inlineFormat(g.text)}</p>
              </section>
            )
          })}
        </div>
      )}

      {appearances.length > 0 && (
        <section className="mt-10">
          <div className="mb-4 flex items-baseline gap-2 text-xs font-bold uppercase tracking-wider text-soft">
            Apariciones en el texto <span className="font-mono">{appearances.length}</span>
          </div>
          <div className="flex flex-col gap-2.5">
            {appearances.map((r) => (
              <button
                key={r.paragraph.id}
                onClick={() => onOpenParagraph(r.paragraph.id)}
                className="surface flex gap-3 rounded-xl border p-4 text-left transition-colors hover:border-[var(--accent)]"
              >
                {r.paragraph.number && <span className="shrink-0 pt-0.5 font-mono text-sm text-soft">{r.paragraph.number}</span>}
                <span className="prose-reading m-0 text-[0.98rem]">
                  {r.paragraph.citation ?? r.paragraph.text.slice(0, 160) + (r.paragraph.text.length > 160 ? '…' : '')}
                </span>
              </button>
            ))}
          </div>
        </section>
      )}

      {concept.related && concept.related.length > 0 && (
        <section className="mt-10">
          <div className="mb-3 text-xs font-bold uppercase tracking-wider text-soft">Conceptos relacionados</div>
          <div className="flex flex-wrap gap-2">
            {concept.related.map((rid) => {
              const rc = (doc.concepts ?? []).find((c) => c.id === rid)
              if (!rc) return null
              const rt = conceptType(rid)
              const rcColor = rt?.color ?? 'var(--accent)'
              return (
                <button
                  key={rid}
                  onClick={() => onSelectConcept(rid)}
                  className="surface flex items-center gap-1.5 rounded-lg border border-l-[3px] px-3 py-1.5 text-sm hover:opacity-80"
                  style={{ borderLeftColor: rcColor }}
                >
                  {rt?.glyph && <span aria-hidden style={{ color: rcColor }}>{rt.glyph}</span>}
                  {rc.label}
                </button>
              )
            })}
          </div>
        </section>
      )}

      {concept.references && concept.references.length > 0 && (
        <section className="mt-10 border-t pt-6" style={{ borderColor: 'var(--border)' }}>
          <div className="mb-4 text-xs font-bold uppercase tracking-wider text-soft">Referencias externas</div>
          <ul className="m-0 flex list-none flex-col gap-4 p-0">
            {concept.references.map((ref, i) => (
              <li key={i} className="flex gap-2">
                <ArrowUpRight size={16} className="mt-1 shrink-0 text-soft" />
                <div>
                  {ref.url ? (
                    <a href={ref.url} target="_blank" rel="noreferrer" className="font-semibold hover:opacity-80" style={{ color: 'var(--accent)' }}>{ref.label}</a>
                  ) : (
                    <span className="font-semibold">{ref.label}</span>
                  )}
                  {ref.detail && <p className="m-0 mt-0.5 text-sm italic text-soft">{ref.detail}</p>}
                </div>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
