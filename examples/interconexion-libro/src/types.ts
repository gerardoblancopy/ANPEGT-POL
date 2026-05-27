export interface DocMeta {
  title: string
  subtitle?: string
  author?: string
  language: string
  description?: string
  source?: string
}

/** Familia de conceptos (p. ej. Bíblica, Técnico, Filosófico). */
export interface ConceptType {
  id: string
  label: string
  glyph?: string
  color?: string
}

/** Glosa tipada de un concepto (p. ej. teológica, técnica, jurídica) o el
 * tratamiento del concepto en el documento. */
export interface ConceptGloss {
  label: string
  text: string
  /** Color opcional; si se omite, se asigna uno de la paleta por su orden. */
  color?: string
}

/** Concepto transversal que atraviesa el documento. Se vincula con los párrafos
 * donde aparece (relación bidireccional). */
export interface Concept {
  id: string
  label: string
  type: string
  /** Caracterización breve en cursiva bajo el título. */
  tagline?: string
  /** Resumen corto para el listado del mapa conceptual. */
  summary?: string
  /** Definición extensa (admite **negritas**). */
  definition?: string
  /** Glosas tipadas y/o tratamiento en el documento. */
  glosses?: ConceptGloss[]
  /** Ids de conceptos relacionados. */
  related?: string[]
  /** Referencias externas (fuentes, magisterio, bibliografía…). */
  references?: CrossReference[]
}

/** Referencia cruzada externa (fuente citada, documento relacionado, etc.). */
export interface CrossReference {
  label: string
  detail?: string
  url?: string
}

/** Unidad mínima de lectura: el extracto literal más sus capas editoriales. */
export interface Paragraph {
  id: string
  number?: string
  /** Texto literal del documento (fiel, sin parafrasear). */
  text: string
  /** Cita textual crítica: la frase clave del párrafo, destacada. */
  citation?: string
  /** Síntesis fiel del párrafo. */
  synthesis?: string
  /** Lectura crítica: tensiones, supuestos, lo que está en juego. */
  criticalReading?: string
  /** Contraste técnico: matiz, precisión o discrepancia técnica. */
  technicalContrast?: string
  /** Nota técnica: aclaración o precisión técnica adicional. */
  technicalNote?: string
  /** Ids de los conceptos presentes en el párrafo. */
  concepts?: string[]
  /** Ids de párrafos conectados (conexiones internas). */
  related?: string[]
  /** Referencias cruzadas externas. */
  references?: CrossReference[]
}

export interface Section {
  id: string
  title: string
  /** Síntesis de la sección; admite **negritas** para destacar. */
  synthesis?: string
  paragraphs: Paragraph[]
}

export interface Chapter {
  id: string
  number?: string
  title?: string
  sections: Section[]
}

export interface BookDoc {
  meta: DocMeta
  conceptTypes?: ConceptType[]
  concepts?: Concept[]
  chapters: Chapter[]
}
