import type { Paragraph } from '../types'

export interface AnalysisLayer {
  key: 'synthesis' | 'criticalReading' | 'technicalContrast' | 'technicalNote'
  label: string
  glyph: string
  color: string
}

/** Capas editoriales de la "lectura asistida" de cada párrafo, en orden. */
export const LAYERS: AnalysisLayer[] = [
  { key: 'synthesis', label: 'Síntesis', glyph: '◆', color: 'var(--synth)' },
  { key: 'criticalReading', label: 'Lectura crítica', glyph: '▲', color: 'var(--crit)' },
  { key: 'technicalContrast', label: 'Contraste técnico', glyph: '◇', color: 'var(--contrast)' },
  { key: 'technicalNote', label: 'Nota técnica', glyph: '⬡', color: 'var(--tnote)' },
]

export function availableLayers(p: Paragraph): AnalysisLayer[] {
  return LAYERS.filter((l) => p[l.key])
}
