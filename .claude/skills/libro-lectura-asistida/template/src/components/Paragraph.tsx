import { useState } from 'react'
import { Maximize2 } from 'lucide-react'
import type { ConceptType, Paragraph as ParagraphType } from '../types'
import { availableLayers } from '../lib/layers'
import { inlineFormat } from '../lib/markdown'

interface Props {
  paragraph: ParagraphType
  conceptLabel: (id: string) => string | undefined
  conceptType: (id: string) => ConceptType | undefined
  onConceptClick: (id: string) => void
  onOpenDetail: (paragraphId: string) => void
}

export function Paragraph({ paragraph, conceptLabel, conceptType, onConceptClick, onOpenDetail }: Props) {
  const [open, setOpen] = useState<Set<string>>(new Set())
  const layers = availableLayers(paragraph)

  const toggle = (key: string) =>
    setOpen((prev) => {
      const next = new Set(prev)
      next.has(key) ? next.delete(key) : next.add(key)
      return next
    })

  return (
    <div id={paragraph.id} className="scroll-mt-20 rounded-xl px-2 py-3">
      <div className="flex gap-3 sm:gap-5">
        {paragraph.number && (
          <button
            onClick={() => onOpenDetail(paragraph.id)}
            className="w-9 shrink-0 pt-1 text-left text-sm font-semibold text-soft transition-colors hover:text-[var(--accent)] sm:w-12"
            title="Analizar a fondo"
          >
            {paragraph.number}
          </button>
        )}
        <div className="min-w-0 flex-1">
          <p className="prose-reading group m-0">
            {paragraph.text}
            <button
              onClick={() => onOpenDetail(paragraph.id)}
              className="ml-1.5 inline-flex translate-y-0.5 opacity-0 transition-opacity hover:opacity-100 group-hover:opacity-60 sm:opacity-0"
              aria-label="Analizar a fondo"
              title="Analizar a fondo"
            >
              <Maximize2 size={14} />
            </button>
          </p>

          {layers.length > 0 && (
            <div className="mt-2.5 flex flex-wrap gap-2">
              {layers.map((l) => {
                const isOpen = open.has(l.key)
                return (
                  <button
                    key={l.key}
                    onClick={() => toggle(l.key)}
                    aria-expanded={isOpen}
                    className="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-bold uppercase tracking-wider transition-opacity"
                    style={{ color: l.color, background: isOpen ? `color-mix(in srgb, ${l.color} 14%, transparent)` : 'transparent', opacity: isOpen ? 1 : 0.85 }}
                  >
                    <span aria-hidden style={{ fontSize: '0.85em' }}>{l.glyph}</span> {l.label}
                  </button>
                )
              })}
            </div>
          )}

          {layers.map((l) =>
            open.has(l.key) ? (
              <div
                key={l.key}
                className="mt-2 rounded-lg border-l-2 py-1.5 pl-3 text-[0.95rem] leading-relaxed"
                style={{ borderColor: l.color, color: 'var(--text)' }}
              >
                {inlineFormat(paragraph[l.key] as string)}
              </div>
            ) : null,
          )}

          {paragraph.concepts && paragraph.concepts.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {paragraph.concepts.map((cid) => {
                const label = conceptLabel(cid)
                if (!label) return null
                const t = conceptType(cid)
                return (
                  <button
                    key={cid}
                    onClick={() => onConceptClick(cid)}
                    className="rounded-full border px-2 py-0.5 text-xs transition-colors hover:opacity-80"
                    style={{ color: 'var(--text-soft)', borderColor: 'var(--border)' }}
                  >
                    {t?.glyph && <span aria-hidden className="mr-1 opacity-70">{t.glyph}</span>}
                    {label}
                  </button>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
