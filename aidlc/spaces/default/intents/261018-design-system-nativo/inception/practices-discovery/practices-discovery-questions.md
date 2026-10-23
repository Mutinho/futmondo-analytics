# Practices Discovery — Entrevista

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.
> Re-run de proyecto maduro: reafirmación del baseline afirmado. Única área con decisión nueva: alcance del testing de UI nativa.

## Q1. Alcance del testing de la UI nativa (SwiftUI) en este intent

El arnés de test del frontend Angular (Vitest/jsdom) no porta 1:1 a UI SwiftUI. ¿Cómo tratar el testing de la capa de diseño nativa en este intent?

- A. Sólo documentar como riesgo/deuda: este intent de capa de diseño no compromete un arnés de test de UI nativo nuevo; backend `pytest` y gates de CI del repo no cambian; el testing nativo (XCTest/snapshot) se decide cuando haya pantallas de datos (F2).
- B. Comprometer ya un arnés de test de UI nativo (XCTest / snapshot) con su umbral, como práctica afirmada desde este intent.
- X. Other (please specify)

[Answer]: A. Sólo documentar como riesgo/deuda; sin arnés de test de UI nativo nuevo en este intent.

## Q2. Resto de áreas (Way of Working, Walking Skeleton, Deployment, Code Style, constraints duros)

¿Confirmas que son reafirmación pura del baseline ya afirmado, sin cambios de práctica (salvo el matiz nativo: tema de Angular como fuente de verdad, Stitch descartado, Apple HIG de relleno, coste 0 €)?

- A. Sí, reafirmación pura + matiz nativo.
- B. Quiero cambiar alguna (indica cuál).
- X. Other (please specify)

[Answer]: A. Sí, reafirmación pura del baseline + matiz nativo (tema de Angular como fuente de verdad, Stitch descartado, Apple HIG de relleno, coste 0 €).

## Consolidated Summary Confirmation

Resumen de Practices Discovery (re-run):

- **Q1=A**: el testing de UI nativa (XCTest/snapshot) se documenta como riesgo/deuda; sin arnés nuevo en este intent; backend `pytest` y gates de CI del repo no cambian.
- **Q2=A**: reafirmación pura del baseline (trunk-based + squash, CI gate bloqueante, walking skeleton OFF, test-after, deploy Fly.io on-merge, coste 0 €, idioma código inglés / usuario y commits castellano) + matiz nativo (tema de Angular como fuente de verdad del diseño SwiftUI, Google Stitch descartado, Apple HIG de relleno).

Al aprobar se promueve a `memory/team.md` (5 secciones) y `memory/project.md` (Mandated/Forbidden) el contenido afirmado.

¿Está todo correcto?

[Answer]: Looks correct
