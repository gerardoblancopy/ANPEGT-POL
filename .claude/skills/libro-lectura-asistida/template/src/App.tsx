import { useEffect, useMemo, useRef, useState, type CSSProperties } from 'react'
import bookData from './book.json'
import type { Book } from './types'
import { SettingsBar } from './components/SettingsBar'
import { Sidebar } from './components/Sidebar'
import { Chapter } from './components/Chapter'
import { GlossaryDrawer } from './components/GlossaryDrawer'
import { useLocalStorage } from './hooks/useLocalStorage'

export type Theme = 'light' | 'sepia' | 'dark'

const book = bookData as Book

export default function App() {
  const [theme, setTheme] = useLocalStorage<Theme>('lla-theme', 'sepia')
  const [scale, setScale] = useLocalStorage<number>('lla-scale', 1)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [glossaryOpen, setGlossaryOpen] = useState(false)
  const [activeId, setActiveId] = useState<string | null>(book.chapters[0]?.id ?? null)
  const [progress, setProgress] = useState(0)
  const mainRef = useRef<HTMLElement>(null)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  useEffect(() => {
    document.title = book.meta.title
    document.documentElement.lang = book.meta.language || 'es'
  }, [])

  // Capítulo activo según la posición de scroll.
  useEffect(() => {
    const sections = book.chapters
      .map((c) => document.getElementById(c.id))
      .filter((el): el is HTMLElement => el !== null)
    if (sections.length === 0) return
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)
        if (visible[0]) setActiveId(visible[0].target.id)
      },
      { rootMargin: '-15% 0px -70% 0px', threshold: 0 },
    )
    sections.forEach((s) => observer.observe(s))
    return () => observer.disconnect()
  }, [])

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
  }, [])

  const navigate = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    setSidebarOpen(false)
  }

  const hasGlossary = useMemo(() => (book.glossary?.length ?? 0) > 0, [])
  const readingStyle = { '--reading-scale': scale } as CSSProperties

  return (
    <>
      <div className="fixed left-0 top-0 z-50 h-1 w-full" style={{ background: 'transparent' }}>
        <div className="progress-fill h-full transition-[width] duration-150" style={{ width: `${progress}%` }} />
      </div>

      <SettingsBar
        title={book.meta.title}
        theme={theme}
        setTheme={setTheme}
        scale={scale}
        setScale={setScale}
        hasGlossary={hasGlossary}
        onToggleSidebar={() => setSidebarOpen((o) => !o)}
        onToggleGlossary={() => setGlossaryOpen(true)}
      />

      <div className="mx-auto flex max-w-[88rem]">
        <Sidebar
          chapters={book.chapters}
          activeId={activeId}
          open={sidebarOpen}
          onClose={() => setSidebarOpen(false)}
          onNavigate={navigate}
        />

        <main ref={mainRef} className="min-w-0 flex-1 px-5 py-10 sm:px-8 lg:px-16" style={readingStyle}>
          <div className="mx-auto max-w-[44rem]">
            <Cover />
            {book.chapters.map((c) => (
              <Chapter key={c.id} chapter={c} glossary={book.glossary} />
            ))}
            <footer className="mt-10 border-t pt-6 text-center text-sm text-soft" style={{ borderColor: 'var(--border)' }}>
              {book.meta.source && <p className="m-0">Fuente: {book.meta.source}</p>}
              <p className="m-0 mt-1">Libro de lectura asistida</p>
            </footer>
          </div>
        </main>
      </div>

      {hasGlossary && (
        <GlossaryDrawer entries={book.glossary!} open={glossaryOpen} onClose={() => setGlossaryOpen(false)} />
      )}
    </>
  )
}

function Cover() {
  const m = book.meta
  return (
    <div className="mb-16 border-b pb-12 text-center" style={{ borderColor: 'var(--border)' }}>
      {m.author && (
        <div className="mb-4 text-sm font-semibold uppercase tracking-[0.2em] text-soft">{m.author}</div>
      )}
      <h1 className="text-4xl font-bold leading-tight sm:text-5xl">{m.title}</h1>
      {m.subtitle && <p className="mt-4 text-lg text-soft sm:text-xl">{m.subtitle}</p>}
      {m.description && (
        <p className="mx-auto mt-6 max-w-[34rem] text-base leading-relaxed text-soft">{m.description}</p>
      )}
    </div>
  )
}
