---
name: libro-lectura-asistida
description: >-
  Convierte un documento (PDF o .docx) en un "libro de lectura asistida": una app
  web estática (React + Vite + Tailwind, lista para Vercel) que presenta el texto
  con asistencia editorial a nivel de párrafo. Cada párrafo ofrece extracto
  literal, síntesis fiel y —donde aporta— cita textual crítica, lectura crítica,
  contraste técnico y nota técnica, además de conexiones y referencias cruzadas.
  El documento se navega de dos formas: por su estructura (capítulos y secciones)
  o por sus conceptos (mapa conceptual agrupado por tipo, con enlaces
  bidireccionales párrafo↔concepto). Úsala cuando el usuario pida transformar un
  PDF/encíclica/ley/libro/documento largo en una experiencia de lectura asistida
  o algo "como magnifica-humanitas.vercel.app".
---

# Libro de lectura asistida (PDF/DOCX → web)

Toma un documento y produce una app web autónoma que lo presenta con apoyos de
lectura **a nivel de párrafo** y **dos formas de entrar**: por estructura y por
conceptos. La parte determinista (extracción + plantilla) viene incluida; tu
trabajo inteligente es **estructurar el contenido y redactar la asistencia
editorial** en un único `book.json`.

## Arquitectura

```
documento ──(scripts/extract.py)──►  texto plano (PDF por páginas; DOCX por párrafos)
texto ──(tú, leyendo)─────────────►  src/book.json   ← contrato de datos
template/ (React+Vite+Tailwind) ──►  renderiza book.json  ──►  build estático → Vercel
```

El **contrato de datos es `book.json`**. La plantilla es genérica: no la edites
salvo que el usuario pida cambios de diseño. El esquema completo está en
**`reference/book-schema.md`**.

### Qué renderiza la plantilla
- **Vista de lectura** (por estructura): capítulos → secciones colapsables (con
  rango § y nº de párrafos) → párrafos. Cada párrafo muestra su extracto literal
  y badges expandibles (Síntesis, Lectura crítica, Contraste técnico, Nota
  técnica) y chips de conceptos.
- **Detalle de párrafo**: cita textual crítica + dos columnas (Texto original |
  Lectura asistida con todos los bloques) + Conexiones y referencias cruzadas
  (conceptos, párrafos conectados y referencias externas) + navegación
  § anterior/siguiente.
- **Mapa conceptual** (por conceptos): conceptos agrupados por tipo, con filtros
  y conteos; cada concepto enlaza a todos los párrafos donde aparece, y desde
  cada párrafo se vuelve a sus conceptos (bidireccional).
- Buscador, temas claro/sepia/oscuro y tamaño de letra ajustable.

## Procedimiento

Usa rutas absolutas para el documento y el directorio de salida.

### 1. Localiza el documento y define la salida
- Pide la ruta del PDF/.docx si no se dio.
- Elige un directorio de salida con un *slug* del título, p. ej.
  `<cwd>/<slug>-libro/`.

### 2. Extrae el texto
```bash
python3 .claude/skills/libro-lectura-asistida/scripts/extract.py \
  "<ruta-al-documento>" --out /tmp/lectura/extracted.txt
```
Soporta PDF (PyMuPDF/pdfplumber/pypdf/`pdftotext`) y .docx (python-docx/docx2txt/
pandoc). Si falla, instala un backend (`pip install pymupdf python-docx`). Para
PDF escaneado, aplica OCR antes (`ocrmypdf in.pdf out.pdf`). El script imprime un
resumen con posibles títulos/secciones/artículos.

### 3. Lee y comprende el documento
Lee `extracted.txt` (por tramos si es largo). Identifica metadatos, la estructura
en **capítulos → secciones**, la **numeración de párrafos** (§1, §2…; o artículos)
y los **conceptos transversales** y su tipo.

### 4. Redacta `book.json`
Sigue **`reference/book-schema.md`**. Reglas de calidad:
- **Fidelidad**: el `text` de cada párrafo (extracto literal) se copia tal cual;
  no parafrasees. Limpia solo artefactos de extracción (cortes con guion, números
  de página, encabezados/pies repetidos).
- **Síntesis fiel** (`synthesis`): 1–3 frases, idealmente en todos los párrafos.
- **Cita textual crítica** (`citation`): la frase clave del párrafo, literal.
- **Lectura crítica / contraste técnico / nota técnica**: solo donde aporten.
  Etiqueta siempre como análisis; nunca sustituyas el texto literal.
- **Síntesis de sección** (`synthesis` de la sección): admite `**negritas**`.
- **Conceptos**: define `conceptTypes` (familias) y `concepts` (con `summary`).
  En cada párrafo, lista en `concepts` los ids presentes. Añade `related`
  (párrafos conectados) y `references` (fuentes citadas) cuando existan.
- No inventes contenido que el texto no respalde.

### 5. Genera la app
```bash
python3 .claude/skills/libro-lectura-asistida/scripts/scaffold.py \
  --out "<dir-de-salida>" --book /tmp/lectura/book.json
```
Copia `template/` al destino e inserta tu `book.json` en `src/book.json`.

### 6. Verifica el build
```bash
cd "<dir-de-salida>" && npm install && npm run build
```
Si falla por contenido (JSON inválido), corrige `src/book.json`; no toques la
plantilla.

### 7. Entrega
- Previsualizar: `npm run dev`.
- Desplegar en Vercel: incluye `vercel.json` (framework Vite, build `npm run
  build`, salida `dist`). Basta `vercel deploy` o conectar el repo en vercel.com.
- Resumen de lo generado (capítulos, secciones, párrafos, conceptos).

## Notas
- App estática, sin backend; funciona offline tras el build.
- Para validar la UI en navegador, usa las skills `run`/`verify`.
