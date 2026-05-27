# Libro de lectura asistida

App web estática que presenta un documento con apoyos de comprensión: índice
navegable, barra de progreso, glosario en contexto, resúmenes por capítulo,
notas al margen y preguntas de reflexión.

Todo el contenido vive en **`src/book.json`**. La interfaz es genérica y renderiza
ese archivo; para cambiar el libro, reemplaza el JSON.

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
  book.json          contenido del libro (el único archivo que sueles editar)
  types.ts           tipos del modelo de datos
  App.tsx            layout, temas, progreso, capítulo activo
  components/        Sidebar (índice), SettingsBar, Chapter, GlossaryDrawer, ...
  lib/glossary.ts    resaltado de términos del glosario en el texto
```

Generado por la skill `libro-lectura-asistida`.
