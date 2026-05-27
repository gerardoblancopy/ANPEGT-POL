import { Fragment } from 'react'
import type { Segment } from '../lib/glossary'
import { Popover } from './Popover'

export function GlossaryText({ segments }: { segments: Segment[] }) {
  return (
    <>
      {segments.map((seg, i) => {
        if (seg.kind === 'text') return <Fragment key={i}>{seg.value}</Fragment>
        return (
          <Popover
            key={i}
            ariaLabel={`Definición de ${seg.term}`}
            triggerClassName="glossary-term"
            trigger={() => seg.value}
          >
            <span className="mb-1 block text-[0.7rem] font-semibold uppercase tracking-wide" style={{ color: 'var(--accent)' }}>
              {seg.term}
            </span>
            {seg.definition}
          </Popover>
        )
      })}
    </>
  )
}
