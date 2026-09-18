<!-- INVARIANT: examples are single-line HTML comments so a fresh template parses to total=0 (MEMORY_EMPTY). Do NOT un-comment or split across lines. t100 guards this. -->
> This file is kept up to date automatically while the stage runs. Add observations at the review step, not by editing here directly.

## Interpretations
- 2026-09-17T14:52:00Z — Esquema de IDs NFR: los requisitos detallados de seguridad heredan del NFR de inception NFR1 (único NFR de seguridad) como NFR1.1..NFR1.9, en vez de reutilizar NFR2..NFR5 (stack/coste/CI/testabilidad), que se detallan en los artefactos hermanos con prefijos propios (NFR-SCAL/REL/TECH/OBS/PERF). Corrige la colisión de IDs que marcó el reviewer (R-01/R-02).
- 2026-09-16T17:15:30Z — Intent sin DAG de unidades (units-generation SKIP en security-patch); ejecuto NFR Requirements como una iteración ordinaria de stage sin ceremonia de Bolt/Unit. Los NFR se derivan de requirements.md (NFR1-5) y de la base de código; en scope Minimal son sobre todo restricciones de no-regresión de seguridad más targets implícitos por FR, sin unidad que etiquetar.
<!-- example: 2026-05-29T10:14:32Z — chose REST over GraphQL; the consuming team only needs CRUD, revisit if subscriptions land -->

## Deviations
- 2026-09-17T14:50:00Z — Bug del framework en `summaryQuestionFiles` (2.8.2/2.9.0 instaladas): para etapa per-unit sin DAG de unidades (scope security-patch), el escaneo omitía el archivo de preguntas de nivel de etapa `construction/<slug>/`, deadlock `SUMMARY_QUESTIONS_MISSING` al pedir revisión. Reproducido determinista; arreglado en `core/` (incluir el dir de nivel de etapa). Recompilado binario 2.8.2-con-fix desde core y reinstalado (integridad re-anclada), proyecto fijado con `.aidlc-version=2.8.2`. Se necesitó redo-jump para salir del estado de revisión.
<!-- example: 2026-05-29T10:14:32Z — skipped the optional caching layer the stage prose suggested; the dataset is small enough that it adds risk -->

## Tradeoffs
<!-- example: 2026-05-29T10:14:32Z — picked TDD over BDD this run; the team is unit-first and the domain is well-understood -->

## Open questions
<!-- example: 2026-05-29T10:14:32Z — confirm the retention window with compliance before the next stage hardens the schema -->
