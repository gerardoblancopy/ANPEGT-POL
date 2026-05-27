import { useEffect, useRef, useState, type ReactNode } from 'react'

interface PopoverProps {
  trigger: (open: boolean) => ReactNode
  children: ReactNode
  triggerClassName?: string
  ariaLabel?: string
}

/** Disparador en línea que abre una tarjeta flotante. Se cierra al hacer clic
 * fuera o pulsar Escape. */
export function Popover({ trigger, children, triggerClassName, ariaLabel }: PopoverProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    if (!open) return
    const onDown = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setOpen(false)
    document.addEventListener('mousedown', onDown)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onDown)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  return (
    <span ref={ref} className="relative inline">
      <button
        type="button"
        aria-label={ariaLabel}
        aria-expanded={open}
        className={triggerClassName}
        onClick={() => setOpen((o) => !o)}
      >
        {trigger(open)}
      </button>
      {open && (
        <span
          role="dialog"
          className="surface absolute left-0 top-[1.6em] z-30 block w-[min(20rem,78vw)] rounded-xl border p-3.5 text-left text-[0.92rem] leading-relaxed font-sans not-italic"
          style={{ boxShadow: 'var(--shadow)', color: 'var(--text)' }}
        >
          {children}
        </span>
      )}
    </span>
  )
}
