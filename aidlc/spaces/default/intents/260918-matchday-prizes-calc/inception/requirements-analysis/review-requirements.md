# Review — Requisitos matchday-prizes-calc (advisory, product-lead)

## Review

**Verdict:** READY
**Reviewer:** aidlc-product-lead-agent
**Date:** 2026-09-18T10:17:35Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Major | inception/requirements-analysis/requirements.md > FR1.1 / FR1.2 | El criterio de empate es por `points` (FR1.1), pero el reparto suma "los premios de las N posiciones que ese grupo ocupa" (FR1.2). En `sync_prizes` la posición (`active_pos`) se asigna hoy por el ORDEN de índice que devuelve la API (`idx + 1`), no derivada de `points`. Para un grupo empatado, "las N posiciones que ocupa" depende de ese orden de índice, que es precisamente lo que el bug considera arbitrario. El requisito no fija de forma verificable qué N posiciones consecutivas se suman (¿las N posiciones de índice contiguas que hoy caen sobre los empatados?, ¿un rango 1..N recalculado por el bloque de empate?). Un desarrollador podría implementar dos algoritmos distintos y ambos "cumplirían" el texto. | Precisar en FR1.2 que las N posiciones a sumar son las N posiciones consecutivas (por `total_pct`/`ratio` vigente) que el grupo empatado ocupa una vez ordenado por `points`, y dar el criterio pass/fail exacto (p. ej. "suma de los `ranking_prize` de las posiciones contiguas p, p+1, …, p+N-1 asignadas al bloque"). El ejemplo de la jornada 5 (3ª+4ª) lo ilustra pero no lo formaliza. | New |
| R-02 | Minor | inception/requirements-analysis/requirements.md > FR1.4 / OQ1 | FR1.4 fija `round()` por parte y difiere el cuadre del resto a OQ1. Es una decisión consciente del usuario (Q2=A) y no bloquea, pero deja sin criterio pass/fail el importe TOTAL repartido al grupo: con `round()` por parte la suma de partes puede diferir en ±1 de la suma de posiciones. Es aceptable como riesgo asumido, pero conviene que un test lo afirme como comportamiento esperado y no como defecto. | Añadir en FR1.4 una nota verificable de que el descuadre ±1 por redondeo es comportamiento aceptado (no regresión), para que la caracterización/test del nuevo contrato lo fije explícitamente. | New |
| R-03 | Minor | inception/requirements-analysis/requirements.md > FR3.2 | La aplicación retroactiva (FR3.2) es correcta y trazable (Q6=A), pero carece de criterio pass/fail observable end-to-end: "la jornada 5 debe quedar corregida tras el siguiente sync". Dado que la caracterización usa fakes (NFR3), no queda claro si la verificación de la corrección de la J5 real es un test automatizado o una comprobación manual post-deploy. | Aclarar el medio de verificación de FR3.2 (test con fake que reproduzca el ranking de la J5 y compruebe 1.500.000/1.500.000, vs. verificación manual en prod), para que QA sepa qué prueba escribir. | New |

### Summary

El artefacto es sólido, está bien acotado y es trazable: cada FR/NFR referencia
su fuente (Q1–Q6, petición del usuario, RE, prácticas afirmadas), el alcance
coincide con el intent (solo `ranking_prize`, empate por `points`, retroactivo,
`round()`, con MVP/dream-team/puntos/identidad explícitamente fuera de alcance) y
no hay contradicciones internas. El único hallazgo Major (R-01) es una
ambigüedad de especificación real —qué N posiciones se suman— que conviene
cerrar antes o durante el diseño para que dos desarrolladores no diverjan; no es
un bloqueante de gate en un pase advisory de 1 iteración, y el ejemplo de la
jornada 5 acota suficientemente la intención. R-02 y R-03 son mejoras de
testabilidad. Recomiendo aprobar precisando R-01 al pasar a historias/diseño.
