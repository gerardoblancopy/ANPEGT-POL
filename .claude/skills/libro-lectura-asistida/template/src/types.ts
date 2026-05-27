export interface BookMeta {
  title: string
  subtitle?: string
  author?: string
  language: string
  description?: string
  source?: string
}

export interface GlossaryEntry {
  term: string
  definition: string
  aliases?: string[]
}

export interface ParagraphBlock {
  type: 'paragraph'
  text: string
  number?: number | string
  note?: string
}

export interface HeadingBlock {
  type: 'heading'
  level: 2 | 3
  text: string
}

export interface QuoteBlock {
  type: 'quote'
  text: string
  cite?: string
}

export interface ListBlock {
  type: 'list'
  ordered?: boolean
  items: string[]
}

export type Block = ParagraphBlock | HeadingBlock | QuoteBlock | ListBlock

export interface Question {
  q: string
  hint?: string
}

export interface Chapter {
  id: string
  number?: string
  title: string
  summary?: string
  blocks: Block[]
  questions?: Question[]
}

export interface Book {
  meta: BookMeta
  glossary?: GlossaryEntry[]
  chapters: Chapter[]
}
