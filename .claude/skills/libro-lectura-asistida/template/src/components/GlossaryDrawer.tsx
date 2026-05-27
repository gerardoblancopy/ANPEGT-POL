import { X } from 'lucide-react'
import type { GlossaryEntry } from '../types'

interface Props {
  entries: GlossaryEntry[]
  open: boolean
  onClose: () => void
}

export function GlossaryDrawer({ entries, open, onClose }: Props) {
  const sorted = [...entries].sort((a, b) => a.term.localeCompare(b.term))
  return (
    <>
      {open && <div className="fixed inset-0 z-40 bg-black/40" onClick={onClose} />}
      <aside
        className={`surface thin-scroll fixed right-0 top-0 z-50 h-dvh w-[22rem] max-w-[88vw] overflow-y-auto border-l p-5 transition-transform ${open ? 'translate-x-0' : 'translate-x-full'}`}
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="m-0 text-lg font-bold">Glosario</h2>
          <button onClick={onClose} aria-label="Cerrar"><X size={20} /></button>
        </div>
        <dl className="m-0">
          {sorted.map((e) => (
            <div key={e.term} className="border-b py-3" style={{ borderColor: 'var(--border)' }}>
              <dt className="font-semibold" style={{ color: 'var(--accent)' }}>{e.term}</dt>
              <dd className="m-0 mt-1 text-[0.92rem] leading-relaxed text-soft">{e.definition}</dd>
            </div>
          ))}
        </dl>
      </aside>
    </>
  )
}
