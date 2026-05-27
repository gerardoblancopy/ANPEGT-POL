import type { GlossaryEntry } from '../types'

export type Segment =
  | { kind: 'text'; value: string }
  | { kind: 'term'; value: string; term: string; definition: string }

export interface GlossaryMatcher {
  regex: RegExp | null
  lookup: Map<string, GlossaryEntry>
}

function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

export function buildMatcher(glossary?: GlossaryEntry[]): GlossaryMatcher {
  const lookup = new Map<string, GlossaryEntry>()
  if (!glossary || glossary.length === 0) return { regex: null, lookup }

  const forms: string[] = []
  for (const entry of glossary) {
    const surfaces = [entry.term, ...(entry.aliases ?? [])]
    for (const s of surfaces) {
      const key = s.trim().toLowerCase()
      if (!key || lookup.has(key)) continue
      lookup.set(key, entry)
      forms.push(s.trim())
    }
  }
  if (forms.length === 0) return { regex: null, lookup }

  // Coincidencias más largas primero para no romper términos compuestos.
  forms.sort((a, b) => b.length - a.length)
  const body = forms.map(escapeRegExp).join('|')
  // Límites de palabra compatibles con acentos (no usa \b).
  const regex = new RegExp(`(?<![\\p{L}\\p{N}])(${body})(?![\\p{L}\\p{N}])`, 'giu')
  return { regex, lookup }
}

/** Divide `text` en segmentos, marcando la primera aparición (según `seen`,
 * compartido a nivel de capítulo) de cada término del glosario. */
export function annotate(
  text: string,
  matcher: GlossaryMatcher,
  seen: Set<string>,
): Segment[] {
  if (!matcher.regex) return [{ kind: 'text', value: text }]

  const segments: Segment[] = []
  let last = 0
  matcher.regex.lastIndex = 0
  let m: RegExpExecArray | null
  while ((m = matcher.regex.exec(text)) !== null) {
    const matched = m[0]
    const entry = matcher.lookup.get(matched.toLowerCase())
    if (!entry || seen.has(entry.term)) continue
    seen.add(entry.term)
    if (m.index > last) segments.push({ kind: 'text', value: text.slice(last, m.index) })
    segments.push({
      kind: 'term',
      value: matched,
      term: entry.term,
      definition: entry.definition,
    })
    last = m.index + matched.length
  }
  if (last < text.length) segments.push({ kind: 'text', value: text.slice(last) })
  return segments.length ? segments : [{ kind: 'text', value: text }]
}
