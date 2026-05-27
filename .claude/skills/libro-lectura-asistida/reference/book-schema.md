# Esquema de `book.json`

Este archivo es el **contrato de datos** entre tu trabajo de estructuración y la
plantilla web. Escríbelo en UTF-8. La plantilla lo importa como
`src/book.json` y lo renderiza tal cual.

## Estructura general

```jsonc
{
  "meta": { ... },          // metadatos del libro (obligatorio)
  "glossary": [ ... ],      // términos definidos (opcional, recomendado)
  "chapters": [ ... ]       // capítulos/secciones en orden (obligatorio)
}
```

## `meta`

| Campo        | Tipo   | Obligatorio | Descripción                                   |
|--------------|--------|-------------|-----------------------------------------------|
| `title`      | string | sí          | Título del libro/documento.                   |
| `subtitle`   | string | no          | Subtítulo.                                     |
| `author`     | string | no          | Autor o emisor.                                |
| `language`   | string | sí          | Código BCP-47, p. ej. `"es"`, `"en"`, `"la"`. |
| `description`| string | no          | 1–2 frases para la portada.                    |
| `source`     | string | no          | Nombre del PDF de origen.                      |

## `glossary` (array de objetos)

Términos difíciles que la plantilla resalta **en el texto** y muestra en un
popover y en un panel. Define cada concepto una sola vez.

| Campo        | Tipo      | Obligatorio | Descripción                                            |
|--------------|-----------|-------------|--------------------------------------------------------|
| `term`       | string    | sí          | Forma canónica del término.                            |
| `definition` | string    | sí          | Definición breve (1–2 frases), en el idioma del texto. |
| `aliases`    | string[]  | no          | Otras formas a resaltar (plurales, sinónimos).         |

El resaltado en el texto es **insensible a mayúsculas** y marca la **primera
aparición por capítulo** de cada término o alias (para no saturar la lectura).

## `chapters` (array de objetos, en orden de lectura)

| Campo      | Tipo            | Obligatorio | Descripción                                          |
|------------|-----------------|-------------|------------------------------------------------------|
| `id`       | string          | sí          | Identificador único, slug. P. ej. `"cap-1"`.         |
| `number`   | string          | no          | Etiqueta visible: `"1"`, `"I"`, `"Introducción"`.    |
| `title`    | string          | sí          | Título del capítulo.                                 |
| `summary`  | string          | no          | Resumen de 2–4 frases (tus palabras).                |
| `blocks`   | Block[]         | sí          | Contenido en orden (ver abajo).                      |
| `questions`| Question[]      | no          | Preguntas de comprensión (2–4).                      |

### `Block` (unión discriminada por `type`)

```jsonc
// Párrafo (el caso más común)
{ "type": "paragraph", "text": "…", "number": 12, "note": "…" }
//   number: opcional, nº de párrafo/marginal del original.
//   note:   opcional, nota al margen anclada a este párrafo.

// Encabezado interno de sección
{ "type": "heading", "level": 2, "text": "…" }   // level 2 o 3

// Cita en bloque
{ "type": "quote", "text": "…", "cite": "…" }     // cite opcional

// Lista
{ "type": "list", "ordered": false, "items": ["…", "…"] }
```

- El **cuerpo (`text`) debe ser fiel al original**. No parafrasees; limpia solo
  artefactos de extracción (cortes de palabra con guion, números de página
  sueltos, encabezados/pies repetidos).
- `note` convierte el párrafo en un punto con **nota al margen** (marcador
  numerado en escritorio, popover en móvil). Úsalo para contexto histórico,
  referencias cruzadas o aclaraciones; sé breve.

### `Question`

```jsonc
{ "q": "¿Pregunta abierta?", "hint": "Pista opcional para guiar la reflexión." }
```

## Ejemplo mínimo válido

```json
{
  "meta": {
    "title": "Título de ejemplo",
    "subtitle": "Un subtítulo",
    "author": "Autor",
    "language": "es",
    "description": "Breve descripción para la portada.",
    "source": "documento.pdf"
  },
  "glossary": [
    { "term": "tecnocracia", "definition": "Gobierno o dominio ejercido por expertos técnicos.", "aliases": ["tecnocrático"] }
  ],
  "chapters": [
    {
      "id": "intro",
      "number": "Introducción",
      "title": "El umbral",
      "summary": "Plantea la pregunta central del documento y su contexto.",
      "blocks": [
        { "type": "heading", "level": 2, "text": "Un tiempo nuevo" },
        { "type": "paragraph", "number": 1, "text": "Texto fiel del primer párrafo…", "note": "Escrito en el 135.º aniversario de Rerum Novarum." },
        { "type": "paragraph", "number": 2, "text": "Segundo párrafo, donde aparece la tecnocracia como concepto clave…" },
        { "type": "quote", "text": "Una cita memorable del documento.", "cite": "§3" }
      ],
      "questions": [
        { "q": "¿Cuál es la tensión que el autor plantea desde el inicio?", "hint": "Fíjate en el primer y el último párrafo." }
      ]
    }
  ]
}
```

## Validación rápida
- JSON válido (UTF-8, sin comas finales).
- Cada `chapter.id` único.
- Todo `block` tiene un `type` reconocido.
- Si dudas, valida con: `python3 -c "import json,sys;json.load(open(sys.argv[1]))" book.json`
