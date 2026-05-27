# Libro de lectura asistida

App web estática que presenta un documento con asistencia editorial **a nivel de
párrafo** y **dos formas de entrar**: por su estructura (capítulos y secciones) o
por sus conceptos (mapa conceptual).

- **Lectura**: secciones colapsables; cada párrafo muestra su extracto literal y
  bloques expandibles (síntesis, lectura crítica, contraste técnico, nota técnica)
  más chips de conceptos.
- **Detalle de párrafo**: cita textual crítica, texto original frente a lectura
  asistida, y conexiones/referencias cruzadas.
- **Mapa conceptual**: conceptos agrupados por tipo (con filtros y conteos). Cada
  concepto tiene su página (definición, glosas, tratamiento, apariciones en el
  texto, conceptos relacionados, referencias externas).
- Buscador, temas claro/sepia/oscuro y tamaño de letra ajustable.

Todo el contenido vive en **`src/book.json`**. La interfaz es genérica y renderiza
ese archivo; para cambiar el documento, reemplaza el JSON.

## Desarrollo

```bash
npm install
npm run dev      # servidor local (Vite)
npm run build    # genera dist/ (estático)
npm run preview  # previsualiza el build
```

## Despliegue en Vercel

El proyecto incluye `vercel.json`. Opciones:

- **CLI:** `vercel deploy` (o `vercel --prod`).
- **Git:** conecta el repo en vercel.com. Framework: *Vite*, build `npm run build`,
  directorio de salida `dist`.

## Estructura

```
src/
  book.json          contenido del documento (el único archivo que sueles editar)
  types.ts           tipos del modelo de datos
  App.tsx            vistas (lectura / detalle / mapa), temas, navegación
  components/        TopBar, StructureIndex, ReadingView, Section, Paragraph,
                     ParagraphDetail, ConceptMap, ConceptDetail, SearchOverlay
  lib/               model.ts (índices), layers.ts (capas), markdown.tsx (negritas)
```

Generado por la skill `libro-lectura-asistida`.
