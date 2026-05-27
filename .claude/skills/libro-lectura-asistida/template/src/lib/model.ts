import type { BookDoc, Chapter, Concept, Paragraph, Section } from '../types'

export interface ParaRef {
  paragraph: Paragraph
  section: Section
  chapter: Chapter
}

/** Aplana todos los párrafos del documento conservando su sección y capítulo. */
export function flattenParagraphs(doc: BookDoc): ParaRef[] {
  const out: ParaRef[] = []
  for (const chapter of doc.chapters) {
    for (const section of chapter.sections) {
      for (const paragraph of section.paragraphs) {
        out.push({ paragraph, section, chapter })
      }
    }
  }
  return out
}

/** Índice concepto -> párrafos donde aparece (relación bidireccional). */
export function conceptParagraphIndex(doc: BookDoc): Map<string, ParaRef[]> {
  const index = new Map<string, ParaRef[]>()
  for (const ref of flattenParagraphs(doc)) {
    for (const cid of ref.paragraph.concepts ?? []) {
      const list = index.get(cid) ?? []
      list.push(ref)
      index.set(cid, list)
    }
  }
  return index
}

export function conceptsByType(doc: BookDoc): Map<string, Concept[]> {
  const map = new Map<string, Concept[]>()
  for (const c of doc.concepts ?? []) {
    const list = map.get(c.type) ?? []
    list.push(c)
    map.set(c.type, list)
  }
  return map
}

/** Rango y conteo de párrafos de una sección (usa los `number` si existen). */
export function sectionRange(section: Section): { label: string; count: number } {
  const count = section.paragraphs.length
  const first = section.paragraphs[0]?.number
  const last = section.paragraphs[count - 1]?.number
  if (!first) return { label: '', count }
  const label = count > 1 && last && last !== first ? `${first}–${last}` : first
  return { label, count }
}

export function totalParagraphs(doc: BookDoc): number {
  return flattenParagraphs(doc).length
}
