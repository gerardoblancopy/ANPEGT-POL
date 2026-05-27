import { useState } from 'react'
import { ChevronDown, ChevronRight } from 'lucide-react'
import type { ConceptType, Section as SectionType } from '../types'
import { sectionRange } from '../lib/model'
import { inlineFormat } from '../lib/markdown'
import { Paragraph } from './Paragraph'

interface Props {
  section: SectionType
  conceptLabel: (id: string) => string | undefined
  conceptType: (id: string) => ConceptType | undefined
  onConceptClick: (id: string) => void
  onOpenDetail: (paragraphId: string) => void
}

export function Section({ section, conceptLabel, conceptType, onConceptClick, onOpenDetail }: Props) {
  const [open, setOpen] = useState(true)
  const { label, count } = sectionRange(section)

  return (
    <section id={section.id} className="scroll-mt-20 border-b py-7" style={{ borderColor: 'var(--border)' }}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-start gap-2 text-left"
        aria-expanded={open}
      >
        <span className="mt-1.5 text-soft">{open ? <ChevronDown size={18} /> : <ChevronRight size={18} />}</span>
        <span className="flex-1">
          <span className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
            <span className="text-2xl font-bold sm:text-3xl">{section.title}</span>
            {label && (
              <span className="font-mono text-sm text-soft">
                {label} · {count} {count === 1 ? 'párrafo' : 'párrafos'}
              </span>
            )}
          </span>
        </span>
      </button>

      {open && (
        <>
          {section.synthesis && (
            <p className="prose-reading mt-4 mb-2 pl-7 italic" style={{ color: 'var(--text-soft)' }}>
              {inlineFormat(section.synthesis)}
            </p>
          )}
          <div className="mt-4 flex flex-col gap-1 pl-0 sm:pl-4">
            {section.paragraphs.map((p) => (
              <Paragraph
                key={p.id}
                paragraph={p}
                conceptLabel={conceptLabel}
                conceptType={conceptType}
                onConceptClick={onConceptClick}
                onOpenDetail={onOpenDetail}
              />
            ))}
          </div>
        </>
      )}
    </section>
  )
}
