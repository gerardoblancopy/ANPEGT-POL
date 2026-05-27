import { Fragment, type ReactNode } from 'react'

/** Formato mínimo en línea: convierte **negrita** en <strong>. El resto del
 * texto se deja tal cual. */
export function inlineFormat(text: string): ReactNode {
  const parts = text.split(/\*\*(.+?)\*\*/g)
  return parts.map((part, i) =>
    i % 2 === 1 ? <strong key={i}>{part}</strong> : <Fragment key={i}>{part}</Fragment>,
  )
}
