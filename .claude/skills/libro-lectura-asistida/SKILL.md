---
name: libro-lectura-asistida
description: >-
  Convierte un documento PDF en un "libro de lectura asistida": una app web
  estática (React + Vite + Tailwind, lista para Vercel) que presenta el texto
  con apoyos de comprensión — índice navegable, barra de progreso, glosario con
  definiciones en contexto, resúmenes por capítulo, preguntas de comprensión y
  notas al margen. Úsala cuando el usuario pida transformar un PDF, encíclica,
  libro o documento largo en una experiencia de lectura asistida / interactiva
  (assisted reading book) o algo "como magnifica-humanitas.vercel.app".
---

# Libro de lectura asistida (PDF → web)

Esta skill toma un PDF y produce una aplicación web autónoma que muestra el
texto con apoyos de lectura. La parte determinista (extracción y plantilla web)
viene incluida; tu trabajo inteligente es **estructurar el contenido y redactar
los apoyos** (glosario, resúmenes, preguntas, notas) en un único archivo
`book.json` que la plantilla renderiza.

## Arquitectura

```
PDF  ──(scripts/extract_pdf.py)──►  texto plano por páginas
texto ──(tú, leyendo)───────────►  src/book.json   ← contrato de datos
template/ (React+Vite+Tailwind) ─►  renderiza book.json  ──►  build estático → Vercel
```

El **contrato de datos es `book.json`**. La plantilla es genérica: no la edites
salvo que el usuario pida cambios de diseño. Todo el contenido vive en
`book.json`, cuyo esquema está documentado en `reference/book-schema.md`.

## Procedimiento

Sigue estos pasos en orden. Trabaja desde la raíz de la skill
(`.claude/skills/libro-lectura-asistida/`); usa rutas absolutas para el PDF y el
directorio de salida.

### 1. Localiza el PDF y define la salida
- Pide al usuario la ruta del PDF si no la dio.
- Elige un directorio de salida con un *slug* del título, p. ej.
  `<cwd>/<slug>-libro/`. Confírmalo con el usuario si hay duda.

### 2. Extrae el texto
```bash
python3 .claude/skills/libro-lectura-asistida/scripts/extract_pdf.py \
  "<ruta-al-pdf>" --out /tmp/lectura/extracted.txt
```
El script intenta varios backends (PyMuPDF, pdfplumber, pypdf, `pdftotext`).
Si todos fallan, instala uno: `pip install pymupdf`. El resultado separa páginas
con `===== PAGE n =====` e imprime un resumen (nº de páginas, posibles títulos).

### 3. Lee y comprende el documento
Lee `extracted.txt`. Para documentos largos, léelo por tramos. Identifica:
- Metadatos: título, subtítulo, autor, idioma.
- La estructura natural en **capítulos/secciones** (usa los encabezados, la
  numeración de párrafos, los saltos temáticos).
- Términos difíciles o técnicos que merezcan **glosario**.
- Pasajes que se beneficien de una **nota al margen** (contexto histórico,
  referencia cruzada, aclaración).

### 4. Redacta `book.json`
Crea el archivo siguiendo **`reference/book-schema.md`** al pie de la letra.
Reglas de calidad:
- **Fidelidad**: copia el cuerpo del texto tal cual (no parafrasees el original).
  Limpia solo artefactos de extracción (guiones de corte de línea, números de
  página sueltos, encabezados/pies repetidos).
- **Glosario**: definiciones breves (1–2 frases), en el idioma del documento.
- **Resúmenes**: 2–4 frases por capítulo, con tus palabras.
- **Preguntas**: 2–4 por capítulo, abiertas, que inviten a reflexionar.
- **Notas al margen**: solo donde aporten; concisas. Se adjuntan a un bloque de
  párrafo mediante el campo `note`.
- No inventes contenido que no esté respaldado por el texto.

### 5. Genera la app
```bash
python3 .claude/skills/libro-lectura-asistida/scripts/scaffold.py \
  --out "<dir-de-salida>" --book /tmp/lectura/book.json
```
Esto copia `template/` al directorio de salida e inserta tu `book.json` en
`src/book.json`. (Alternativa manual: `cp -r template/. <salida>/` y copiar el
JSON.)

### 6. Verifica el build
```bash
cd "<dir-de-salida>" && npm install && npm run build
```
Si el build falla por el contenido (JSON inválido), corrige `src/book.json`. No
toques la plantilla por errores de contenido.

### 7. Entrega
Informa al usuario:
- Cómo previsualizar: `npm run dev` (abre el localhost que indique Vite).
- Cómo desplegar en Vercel: el directorio incluye `vercel.json`; basta
  `vercel deploy` o conectar el repo en vercel.com (framework: Vite, build
  `npm run build`, salida `dist`).
- Resumen de lo generado (nº de capítulos, términos del glosario, etc.).

## Notas
- La plantilla es estática y no necesita backend; el contenido se empaqueta en el
  bundle. Funciona offline tras el build.
- Si el PDF es escaneado (imágenes sin texto), la extracción saldrá vacía:
  avísalo al usuario y sugiere OCR (`ocrmypdf entrada.pdf salida.pdf`) antes de
  reintentar.
- Para verificar la UI en navegador puedes apoyarte en la skill `run`/`verify`.
