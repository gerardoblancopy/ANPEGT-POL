# Esquema de `book.json`

Contrato de datos entre tu estructuración y la plantilla web. UTF-8. La plantilla
lo importa como `src/book.json` y lo renderiza.

## Estructura general

```jsonc
{
  "meta": { ... },          // metadatos (obligatorio)
  "conceptTypes": [ ... ],  // familias de conceptos (recomendado)
  "concepts": [ ... ],      // conceptos transversales (recomendado)
  "chapters": [ ... ]       // capítulos → secciones → párrafos (obligatorio)
}
```

## `meta`

| Campo        | Tipo   | Obl. | Descripción                          |
|--------------|--------|------|--------------------------------------|
| `title`      | string | sí   | Título del documento.                |
| `subtitle`   | string | no   | Subtítulo (se muestra en la portada y la barra). |
| `author`     | string | no   | Autor o emisor.                      |
| `language`   | string | sí   | Código BCP-47: `"es"`, `"en"`, `"la"`. |
| `description`| string | no   | 1–2 frases para la portada.          |
| `source`     | string | no   | Nombre del archivo de origen.        |

## `conceptTypes` (familias de conceptos)

Definen los grupos del mapa conceptual (chips con conteo).

| Campo   | Tipo   | Obl. | Descripción                                   |
|---------|--------|------|-----------------------------------------------|
| `id`    | string | sí   | Identificador, referenciado por `concept.type`. |
| `label` | string | sí   | Nombre visible (p. ej. "Bíblica", "Técnico"). |
| `glyph` | string | no   | Símbolo corto (p. ej. `"✦"`, `"◆"`, `"⬡"`).    |
| `color` | string | no   | Color hex para chips y acentos del tipo.       |

## `concepts` (conceptos transversales)

Cada concepto tiene su **página de detalle** y se enlaza bidireccionalmente con
los párrafos que lo declaran en `paragraph.concepts`.

| Campo        | Tipo            | Obl. | Descripción                                              |
|--------------|-----------------|------|----------------------------------------------------------|
| `id`         | string          | sí   | Identificador único (slug).                              |
| `label`      | string          | sí   | Nombre del concepto.                                     |
| `type`       | string          | sí   | Id de un `conceptType`.                                  |
| `tagline`    | string          | no   | Caracterización breve (cursiva, bajo el título).         |
| `summary`    | string          | no   | Resumen corto para el listado del mapa.                  |
| `definition` | string          | no   | Definición extensa; admite `**negritas**`.               |
| `glosses`    | Gloss[]         | no   | Glosas tipadas y/o "Tratamiento en el documento".        |
| `related`    | string[]        | no   | Ids de conceptos relacionados.                           |
| `references` | CrossReference[]| no   | Referencias externas.                                    |

### `Gloss`
```jsonc
{ "label": "Glosa teológica", "text": "…", "color": "#9f1239" }
```
`color` es opcional; si se omite, se asigna por orden (granate, ámbar, azul, …).
Usa una glosa con `label` "Tratamiento en el documento" para explicar cómo se
trata el concepto a lo largo del texto.

## `chapters` → `sections` → `paragraphs`

### `Chapter`
| Campo      | Tipo      | Obl. | Descripción                              |
|------------|-----------|------|------------------------------------------|
| `id`       | string    | sí   | Único (slug).                            |
| `number`   | string    | no   | Etiqueta: `"Capítulo 3"`, `"I"`, etc.    |
| `title`    | string    | no   | Título del capítulo.                     |
| `sections` | Section[] | sí   | Secciones en orden.                      |

### `Section`
| Campo        | Tipo        | Obl. | Descripción                                            |
|--------------|-------------|------|--------------------------------------------------------|
| `id`         | string      | sí   | Único (slug); ancla de navegación.                     |
| `title`      | string      | sí   | Título de la sección.                                  |
| `synthesis`  | string      | no   | Síntesis de la sección; admite `**negritas**`.         |
| `paragraphs` | Paragraph[] | sí   | Párrafos en orden.                                     |

### `Paragraph`
La unidad de lectura. El **`text` es literal** (no parafrasear). El resto es
asistencia editorial; se muestra como bloques expandibles y en la página de
detalle del párrafo.

| Campo               | Tipo            | Obl. | Descripción                                              |
|---------------------|-----------------|------|----------------------------------------------------------|
| `id`                | string          | sí   | Único (slug); ancla y destino de enlaces.                |
| `number`            | string          | no   | Etiqueta visible: `"§1"`, `"§107"`, `"Art. 4"`.          |
| `text`              | string          | sí   | **Extracto literal**, fiel al original.                  |
| `citation`          | string          | no   | Cita textual crítica (frase clave, literal).             |
| `synthesis`         | string          | no   | Síntesis fiel (idealmente en todos los párrafos).        |
| `criticalReading`   | string          | no   | Lectura crítica: tensiones, supuestos, lo que está en juego. |
| `technicalContrast` | string          | no   | Contraste técnico: matiz o discrepancia técnica.         |
| `technicalNote`     | string          | no   | Nota técnica: precisión o aclaración.                    |
| `concepts`          | string[]        | no   | Ids de conceptos presentes (genera enlaces bidireccionales). |
| `related`           | string[]        | no   | Ids de párrafos conectados.                              |
| `references`        | CrossReference[]| no   | Referencias externas del párrafo.                        |

Los campos de análisis (`synthesis`, `criticalReading`, `technicalContrast`,
`technicalNote`) admiten `**negritas**`.

### `CrossReference`
```jsonc
{ "label": "Rerum Novarum (1891)", "detail": "León XIII, sobre la cuestión social", "url": "https://…" }
```

## Ejemplo mínimo válido

```json
{
  "meta": { "title": "Documento", "language": "es" },
  "conceptTypes": [{ "id": "dsi", "label": "DSI", "glyph": "◆", "color": "#7c3aed" }],
  "concepts": [
    { "id": "justicia-social", "label": "Justicia social", "type": "dsi",
      "tagline": "Criterio que ordena instituciones y tecnologías.",
      "definition": "Categoría central del Magisterio social; **criterio estructural**, no caridad privada.",
      "glosses": [{ "label": "Glosa técnica", "text": "Invierte el criterio: mide el impacto sobre los más vulnerables." }],
      "related": [], "references": [{ "label": "Sollicitudo Rei Socialis (1987)" }] }
  ],
  "chapters": [
    { "id": "cap-1", "number": "Capítulo 1", "title": "Gobernanza",
      "sections": [
        { "id": "s1", "title": "Alineación y deliberación",
          "synthesis": "No solo **cómo** alinear, sino **quién** decide los valores.",
          "paragraphs": [
            { "id": "p107", "number": "§107",
              "text": "No serviría de nada una IA más moral, si esta moral es decidida por unos pocos…",
              "citation": "No serviría de nada una IA más moral, si esta moral es decidida por unos pocos.",
              "synthesis": "Cuestiona la 'alineación' sin deliberar **quién** fija los valores.",
              "criticalReading": "Pasaje de gobernanza: alineación sin deliberación concentra poder.",
              "concepts": ["justicia-social"],
              "related": [],
              "references": [{ "label": "Gaudium et Spes, 36" }] }
          ] }
      ] }
  ]
}
```

## Validación rápida
- JSON válido (UTF-8, sin comas finales).
- `chapter.id`, `section.id`, `paragraph.id`, `concept.id` únicos.
- Todo `concept.type` apunta a un `conceptType.id`; todo id en `concepts`/`related`
  existe.
- Valida con: `python3 -c "import json,sys;json.load(open(sys.argv[1]))" book.json`
