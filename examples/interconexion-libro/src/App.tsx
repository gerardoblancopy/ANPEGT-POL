import { useCallback, useEffect, useMemo, useState, type CSSProperties } from 'react'
import bookData from './book.json'
import type { BookDoc } from './types'
import { TopBar, type View } from './components/TopBar'
import { StructureIndex } from './components/StructureIndex'
import { ReadingView } from './components/ReadingView'
import { ParagraphDetail } from './components/ParagraphDetail'
import { ConceptMap } from './components/ConceptMap'
import { ConceptDetail } from './components/ConceptDetail'
import { SearchOverlay } from './components/SearchOverlay'
import { useLocalStorage } from './hooks/useLocalStorage'

export type Theme = 'light' | 'sepia' | 'dark'
type AppView = View | 'paragraph' | 'concept'

const doc = bookData as BookDoc

export default function App() {
  const [theme, setTheme] = useLocalStorage<Theme>('lla-theme', 'sepia')
  const [scale, setScale] = useLocalStorage<number>('lla-scale', 1)
  const [view, setView] = useState<AppView>('reading')
  const [detailId, setDetailId] = useState<string | null>(null)
  const [conceptId, setConceptId] = useState<string | null>(null)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [activeId, setActiveId] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)

  const concepts = useMemo(() => doc.concepts ?? [], [])
  const conceptTypes = useMemo(() => doc.conceptTypes ?? [], [])
  const hasConcepts = concepts.length > 0

  const conceptLabel = useCallback((id: string) => concepts.find((c) => c.id === id)?.label, [concepts])
  const conceptTypeOf = useCallback(
    (id: string) => {
      const c = concepts.find((x) => x.id === id)
      return c ? conceptTypes.find((t) => t.id === c.type) : undefined
    },
    [concepts, conceptTypes],
  )

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  useEffect(() => {
    document.title = doc.meta.title
    document.documentElement.lang = doc.meta.language || 'es'
  }, [])

  // Lleva el scroll arriba al cambiar de vista, párrafo o concepto.
  useEffect(() => {
    window.scrollTo({ top: 0 })
  }, [view, detailId, conceptId])

  // Sección activa en la vista de lectura.
  useEffect(() => {
    if (view !== 'reading') return
    const ids = doc.chapters.flatMap((c) => c.sections.map((s) => s.id))
    const els = ids.map((id) => document.getElementById(id)).filter((e): e is HTMLElement => e !== null)
    if (els.length === 0) return
    const observer = new IntersectionObserver(
      (entries) => {
        const vis = entries.filter((e) => e.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (vis[0]) setActiveId(vis[0].target.id)
      },
      { rootMargin: '-12% 0px -75% 0px', threshold: 0 },
    )
    els.forEach((e) => observer.observe(e))
    return () => observer.disconnect()
  }, [view])

  // Progreso de lectura.
  useEffect(() => {
    const onScroll = () => {
      const h = document.documentElement
      const max = h.scrollHeight - h.clientHeight
      setProgress(max > 0 ? Math.min(100, (h.scrollTop / max) * 100) : 0)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [view, detailId, conceptId])

  const openParagraph = useCallback((id: string) => {
    setSearchOpen(false)
    setDetailId(id)
    setView('paragraph')
  }, [])

  const goToConcept = useCallback((id: string) => {
    setSearchOpen(false)
    setConceptId(id)
    setView('concept')
  }, [])

  const switchView = useCallback((v: View) => {
    setView(v)
    setDetailId(null)
    setConceptId(null)
  }, [])

  const goToSection = useCallback((id: string) => {
    setView('reading')
    setDetailId(null)
    setConceptId(null)
    setSidebarOpen(false)
    requestAnimationFrame(() => document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }))
  }, [])

  const readingStyle = { '--reading-scale': scale } as CSSProperties
  const topView: View = view === 'concepts' || view === 'concept' ? 'concepts' : 'reading'

  return (
    <>
      <div className="fixed left-0 top-0 z-50 h-1 w-full">
        <div className="progress-fill h-full transition-[width] duration-150" style={{ width: `${view === 'reading' ? progress : 0}%` }} />
      </div>

      <TopBar
        meta={doc.meta}
        view={topView}
        setView={switchView}
        hasConcepts={hasConcepts}
        theme={theme}
        setTheme={setTheme}
        scale={scale}
        setScale={setScale}
        onToggleSidebar={() => setSidebarOpen((o) => !o)}
        onOpenSearch={() => setSearchOpen(true)}
      />

      {view === 'reading' && (
        <div className="mx-auto flex max-w-[88rem]">
          <StructureIndex
            doc={doc}
            activeId={activeId}
            open={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            onNavigate={goToSection}
          />
          <main className="min-w-0 flex-1 px-5 py-10 sm:px-8 lg:px-16" style={readingStyle}>
            <div className="mx-auto max-w-[46rem]">
              <Cover />
              <ReadingView
                doc={doc}
                conceptLabel={conceptLabel}
                conceptType={conceptTypeOf}
                onConceptClick={goToConcept}
                onOpenDetail={openParagraph}
              />
              <Footer />
            </div>
          </main>
        </div>
      )}

      {view === 'paragraph' && detailId && (
        <main style={readingStyle}>
          <ParagraphDetail
            doc={doc}
            paragraphId={detailId}
            conceptLabel={conceptLabel}
            conceptType={conceptTypeOf}
            onOpenParagraph={openParagraph}
            onGoToConcept={goToConcept}
            onBackToReading={() => switchView('reading')}
            onGoToSection={goToSection}
          />
        </main>
      )}

      {view === 'concepts' && (
        <main className="px-5 py-10 sm:px-8">
          <ConceptMap doc={doc} onSelectConcept={goToConcept} />
        </main>
      )}

      {view === 'concept' && conceptId && (
        <main style={readingStyle}>
          <ConceptDetail
            doc={doc}
            conceptId={conceptId}
            conceptType={conceptTypeOf}
            onOpenParagraph={openParagraph}
            onSelectConcept={goToConcept}
            onBackToMap={() => switchView('concepts')}
          />
        </main>
      )}

      <SearchOverlay
        doc={doc}
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
        onGoToParagraph={openParagraph}
        onGoToConcept={goToConcept}
      />
    </>
  )
}

function Cover() {
  const m = doc.meta
  return (
    <div className="mb-12 border-b pb-10 text-center" style={{ borderColor: 'var(--border)' }}>
      {m.author && <div className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-soft">{m.author}</div>}
      <h1 className="text-4xl font-bold leading-tight sm:text-5xl">{m.title}</h1>
      {m.subtitle && <p className="mt-4 text-lg text-soft sm:text-xl">{m.subtitle}</p>}
      {m.description && <p className="mx-auto mt-6 max-w-[34rem] leading-relaxed text-soft">{m.description}</p>}
    </div>
  )
}

function Footer() {
  return (
    <footer className="mt-12 border-t pt-6 text-center text-sm text-soft" style={{ borderColor: 'var(--border)' }}>
      {doc.meta.source && <p className="m-0">Fuente: {doc.meta.source}</p>}
      <p className="m-0 mt-1">Lectura asistida · el texto literal prevalece sobre el análisis</p>
    </footer>
  )
}
