import { useMemo } from 'react'
import { BookOpen, HelpCircle, Lightbulb } from 'lucide-react'
import type { Block, Chapter as ChapterType, GlossaryEntry } from '../types'
import { annotate, buildMatcher, type Segment } from '../lib/glossary'
import { GlossaryText } from './GlossaryText'
import { Popover } from './Popover'

interface Props {
  chapter: ChapterType
  glossary?: GlossaryEntry[]
}

export function Chapter({ chapter, glossary }: Props) {
  // Anota los términos del glosario una sola vez por capítulo.
  const annotated = useMemo(() => {
    const matcher = buildMatcher(glossary)
    const seen = new Set<string>()
    const map = new Map<number, Segment[]>()
    chapter.blocks.forEach((b, i) => {
      if (b.type === 'paragraph' || b.type === 'quote') {
        map.set(i, annotate(b.text, matcher, seen))
      }
    })
    return map
  }, [chapter, glossary])

  return (
    <section id={chapter.id} className="scroll-mt-20 pb-16">
      <header className="mb-7">
        {chapter.number && (
          <div className="mb-1 text-sm font-semibold uppercase tracking-[0.18em]" style={{ color: 'var(--accent)' }}>
            {chapter.number}
          </div>
        )}
        <h2 className="text-3xl font-bold leading-tight sm:text-4xl">{chapter.title}</h2>
      </header>

      {chapter.summary && (
        <div className="surface mb-9 rounded-2xl border p-5" style={{ background: 'var(--surface-2)' }}>
          <div className="mb-1.5 flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-soft">
            <BookOpen size={14} /> Resumen
          </div>
          <p className="m-0 text-[0.98rem] leading-relaxed">{chapter.summary}</p>
        </div>
      )}

      <div className="prose-reading">
        {chapter.blocks.map((block, i) => (
          <BlockView key={i} block={block} segments={annotated.get(i)} />
        ))}
      </div>

      {chapter.questions && chapter.questions.length > 0 && (
        <div className="surface mt-12 rounded-2xl border p-6">
          <div className="mb-4 flex items-center gap-2 text-sm font-bold uppercase tracking-wider" style={{ color: 'var(--accent)' }}>
            <HelpCircle size={16} /> Para reflexionar
          </div>
          <ol className="m-0 flex list-none flex-col gap-4 p-0">
            {chapter.questions.map((question, qi) => (
              <li key={qi} className="flex gap-3">
                <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold" style={{ background: 'var(--accent-soft)', color: 'var(--accent)' }}>
                  {qi + 1}
                </span>
                <div>
                  <p className="m-0 font-medium">{question.q}</p>
                  {question.hint && (
                    <p className="mt-1 mb-0 flex items-start gap-1.5 text-sm text-soft">
                      <Lightbulb size={14} className="mt-0.5 shrink-0" /> {question.hint}
                    </p>
                  )}
                </div>
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  )
}

function BlockView({ block, segments }: { block: Block; segments?: Segment[] }) {
  switch (block.type) {
    case 'heading': {
      const Tag = block.level === 3 ? 'h4' : 'h3'
      return (
        <Tag className={block.level === 3 ? 'mt-8 mb-3 text-xl font-semibold' : 'mt-10 mb-4 text-2xl font-bold'}>
          {block.text}
        </Tag>
      )
    }
    case 'quote':
      return (
        <blockquote className="my-6 border-l-4 pl-5 italic" style={{ borderColor: 'var(--quote)', color: 'var(--text-soft)' }}>
          {segments ? <GlossaryText segments={segments} /> : block.text}
          {block.cite && <cite className="mt-2 block text-sm not-italic text-soft">— {block.cite}</cite>}
        </blockquote>
      )
    case 'list':
      return block.ordered ? (
        <ol className="my-4 ml-6 list-decimal space-y-1.5">
          {block.items.map((it, i) => <li key={i}>{it}</li>)}
        </ol>
      ) : (
        <ul className="my-4 ml-6 list-disc space-y-1.5">
          {block.items.map((it, i) => <li key={i}>{it}</li>)}
        </ul>
      )
    case 'paragraph':
      return (
        <p data-pnum={block.number}>
          {block.number != null && (
            <span className="mr-2 select-none align-super text-[0.62em] font-sans font-semibold text-soft">
              {block.number}
            </span>
          )}
          {segments ? <GlossaryText segments={segments} /> : block.text}
          {block.note && (
            <Popover
              ariaLabel="Nota"
              triggerClassName="note-marker"
              trigger={() => 'i'}
            >
              <span className="mb-1 block text-[0.7rem] font-semibold uppercase tracking-wide" style={{ color: 'var(--note)' }}>
                Nota
              </span>
              {block.note}
            </Popover>
          )}
        </p>
      )
  }
}
