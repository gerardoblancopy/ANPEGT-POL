import { useMemo } from 'react'
import { ArrowLeft, ArrowRight, ExternalLink, Link2 } from 'lucide-react'
import type { BookDoc, ConceptType } from '../types'
import { flattenParagraphs } from '../lib/model'
import { availableLayers } from '../lib/layers'
import { inlineFormat } from '../lib/markdown'

interface Props {
  doc: BookDoc
  paragraphId: string
  conceptLabel: (id: string) => string | undefined
  conceptType: (id: string) => ConceptType | undefined
  onOpenParagraph: (id: string) => void
  onGoToConcept: (id: string) => void
  onBackToReading: () => void
  onGoToSection: (sectionId: string) => void
}

export function ParagraphDetail({
  doc, paragraphId, conceptLabel, conceptType, onOpenParagraph, onGoToConcept, onBackToReading, onGoToSection,
}: Props) {
  const refs = useMemo(() => flattenParagraphs(doc), [doc])
  const idx = refs.findIndex((r) => r.paragraph.id === paragraphId)
  if (idx === -1) return null
  const { paragraph: p, section, chapter } = refs[idx]
  const prev = refs[idx - 1]
  const next = refs[idx + 1]
  const layers = availableLayers(p)
  const hasConnections =
    (p.concepts && p.concepts.length) || (p.related && p.related.length) || (p.references && p.references.length)

  return (
    <div className="mx-auto max-w-[72rem] px-5 py-8 sm:px-8">
      {/* Breadcrumb + navegación */}
      <div className="mb-8 flex flex-wrap items-center justify-between gap-3 text-sm">
        <nav className="flex flex-wrap items-center gap-1.5 text-soft">
          <button onClick={onBackToReading} className="hover:text-[var(--accent)]">Inicio</button>
          {(chapter.title || chapter.number) && (
            <>
              <span className="opacity-50">›</span>
              <span>{chapter.number ?? chapter.title}</span>
            </>
          )}
          <span className="opacity-50">›</span>
          <button onClick={() => onGoToSection(section.id)} className="hover:text-[var(--accent)]">{section.title}</button>
          <span className="opacity-50">›</span>
          <span className="font-semibold" style={{ color: 'var(--text)' }}>{p.number ?? p.id}</span>
        </nav>
        <div className="flex items-center gap-3 font-mono text-soft">
          {prev && (
            <button onClick={() => onOpenParagraph(prev.paragraph.id)} className="flex items-center gap-1 hover:text-[var(--accent)]">
              <ArrowLeft size={14} /> {prev.paragraph.number ?? 'Anterior'}
            </button>
          )}
          {next && (
            <button onClick={() => onOpenParagraph(next.paragraph.id)} className="flex items-center gap-1 hover:text-[var(--accent)]">
              {next.paragraph.number ?? 'Siguiente'} <ArrowRight size={14} />
            </button>
          )}
        </div>
      </div>

      {/* Cita textual crítica */}
      {p.citation && (
        <blockquote className="prose-reading mx-auto mb-10 max-w-[40rem] text-center text-2xl italic leading-snug sm:text-3xl">
          <span className="text-soft">«&nbsp;</span>{p.citation}<span className="text-soft">&nbsp;»</span>
        </blockquote>
      )}

      {/* Dos columnas: texto original | lectura asistida */}
      <div className="grid gap-8 lg:grid-cols-2">
        <div>
          <ColumnHeader index="01" title="Texto original" aside={p.number} />
          <div className="prose-reading mt-4">{p.text}</div>
        </div>

        <div>
          <ColumnHeader index="02" title="Lectura asistida" aside={`${layers.length} ${layers.length === 1 ? 'bloque' : 'bloques'}`} />
          <div className="mt-4 flex flex-col gap-3">
            {layers.length === 0 && <p className="text-sm italic text-soft">Sin análisis editorial para este párrafo.</p>}
            {layers.map((l) => (
              <div key={l.key} className="surface rounded-xl border border-l-[3px] p-4" style={{ borderLeftColor: l.color }}>
                <div className="mb-2 flex items-center gap-2 text-xs font-bold uppercase tracking-wider" style={{ color: l.color }}>
                  <span aria-hidden>{l.glyph}</span> {l.label}
                </div>
                <p className="m-0 leading-relaxed">{inlineFormat(p[l.key] as string)}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Conexiones y referencias cruzadas */}
      {hasConnections && (
        <div className="mt-12 border-t pt-8" style={{ borderColor: 'var(--border)' }}>
          <div className="mb-5 flex items-center gap-2 text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--accent)' }}>
            <Link2 size={16} /> Conexiones y referencias cruzadas
          </div>
          <div className="grid gap-6 sm:grid-cols-3">
            {p.concepts && p.concepts.length > 0 && (
              <div>
                <div className="mb-2 text-xs font-bold uppercase tracking-wider text-soft">Conceptos</div>
                <div className="flex flex-wrap gap-1.5">
                  {p.concepts.map((cid) => {
                    const label = conceptLabel(cid)
                    if (!label) return null
                    const t = conceptType(cid)
                    return (
                      <button key={cid} onClick={() => onGoToConcept(cid)} className="rounded-full border px-2.5 py-0.5 text-sm hover:opacity-80" style={{ color: 'var(--text-soft)', borderColor: 'var(--border)' }}>
                        {t?.glyph && <span aria-hidden className="mr-1 opacity-70">{t.glyph}</span>}{label}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {p.related && p.related.length > 0 && (
              <div>
                <div className="mb-2 text-xs font-bold uppercase tracking-wider text-soft">Párrafos conectados</div>
                <div className="flex flex-wrap gap-1.5">
                  {p.related.map((rid) => {
                    const target = refs.find((r) => r.paragraph.id === rid)?.paragraph
                    return (
                      <button key={rid} onClick={() => onOpenParagraph(rid)} className="rounded-md px-2 py-1 font-mono text-xs hover:opacity-80" style={{ background: 'var(--surface-2)', color: 'var(--accent)' }}>
                        {target?.number ?? rid}
                      </button>
                    )
                  })}
                </div>
              </div>
            )}

            {p.references && p.references.length > 0 && (
              <div>
                <div className="mb-2 text-xs font-bold uppercase tracking-wider text-soft">Referencias</div>
                <ul className="m-0 flex list-none flex-col gap-2 p-0 text-sm">
                  {p.references.map((ref, i) => (
                    <li key={i}>
                      {ref.url ? (
                        <a href={ref.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 hover:opacity-80" style={{ color: 'var(--accent)' }}>
                          {ref.label} <ExternalLink size={12} />
                        </a>
                      ) : (
                        <span className="font-medium">{ref.label}</span>
                      )}
                      {ref.detail && <span className="text-soft"> — {ref.detail}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function ColumnHeader({ index, title, aside }: { index: string; title: string; aside?: string }) {
  return (
    <div className="flex items-baseline justify-between border-b pb-2" style={{ borderColor: 'var(--text)' }}>
      <div className="flex items-baseline gap-2">
        <span className="font-mono text-xs text-soft">{index}</span>
        <span className="text-sm font-bold uppercase tracking-wider">{title}</span>
      </div>
      {aside && <span className="font-mono text-xs text-soft">{aside}</span>}
    </div>
  )
}
