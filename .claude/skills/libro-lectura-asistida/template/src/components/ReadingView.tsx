import type { BookDoc, ConceptType } from '../types'
import { Section } from './Section'

interface Props {
  doc: BookDoc
  conceptLabel: (id: string) => string | undefined
  conceptType: (id: string) => ConceptType | undefined
  onConceptClick: (id: string) => void
  onOpenDetail: (paragraphId: string) => void
}

export function ReadingView({ doc, conceptLabel, conceptType, onConceptClick, onOpenDetail }: Props) {
  return (
    <div>
      {doc.chapters.map((chapter) => (
        <div key={chapter.id} id={chapter.id} className="scroll-mt-20">
          {(chapter.title || chapter.number) && (
            <div className="mt-10 mb-2 first:mt-0">
              {chapter.number && (
                <div className="text-sm font-semibold uppercase tracking-[0.18em]" style={{ color: 'var(--accent)' }}>
                  {chapter.number}
                </div>
              )}
              {chapter.title && <h2 className="text-xl font-bold uppercase tracking-wide text-soft">{chapter.title}</h2>}
            </div>
          )}
          {chapter.sections.map((section) => (
            <Section
              key={section.id}
              section={section}
              conceptLabel={conceptLabel}
              conceptType={conceptType}
              onConceptClick={onConceptClick}
              onOpenDetail={onOpenDetail}
            />
          ))}
        </div>
      ))}
    </div>
  )
}
