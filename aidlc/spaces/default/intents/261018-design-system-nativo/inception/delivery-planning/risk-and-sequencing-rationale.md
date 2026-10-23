# Risk & Sequencing Rationale — Sistema de diseño / theming nativo iOS

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.

## Por qué este orden

La secuencia Bolt 1 (U1) → Bolt 2 (U2) viene impuesta por el DAG de Units (U2 depende de U1): no se puede revestir el login con una librería que aún no existe. No se aplica un modelo de puntuación (WSJF): con dependencia estricta y dos Units, el orden es forzado y un scoring no aporta.

## Argumento de riesgo (risk-first dentro del orden)

El riesgo dominante del intent es la **fidelidad de reproducir el tema de Angular en SwiftUI** (RAID R-01). Construir U1 primero, con su pantalla de catálogo, materializa y valida ese riesgo pronto: si la fidelidad o el soporte claro/oscuro + Dynamic Type fallan, se detecta en U1 antes de invertir en revestir el login (U2). Así el orden por dependencias coincide con el risk-first.

## Heurística de referencia

Orden topológico del DAG (dependency-first) + validación temprana del riesgo dominante (risk-first), sin WSJF por innecesario a esta escala.

## Assumptions & Open Questions

None.
