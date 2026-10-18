# Practices Discovery — Timestamp y alcance

> Etapa: inception (practices-discovery). Intent: `261016-f1-login-nativo`.
> Idioma: castellano; tokens técnicos verbatim en inglés.

## Timestamp

- **Fecha/hora de ejecución (UTC)**: `2026-10-17T10:07:40Z`
  (obtenido con `aidlc engine now`).
- **Zona local del proyecto**: 2026-10-17, ~12:07 (CEST, UTC+02:00).

## Alcance de la etapa

- **Intent**: `261016-f1-login-nativo` — F1: login nativo end-to-end en iOS
  (Swift/SwiftUI) contra el backend FastAPI existente.
- **Scope del workflow**: `feature`.
- **Fase**: inception.
- **Agente líder**: `aidlc-pipeline-deploy-agent` (release/CI engineer).
- **Modo de descubrimiento**: **brownfield con prácticas ya afirmadas**. El
  proyecto Futmondo Analytics ya tiene prácticas de equipo y proyecto durables en
  `aidlc/spaces/default/memory/{team,project}.md`. Esta etapa **reconoce** las
  vigentes aplicables a F1 (sin re-descubrirlas ni duplicarlas) y **propone sólo
  lo nuevo o específico de F1**.

## Entregables producidos (en este directorio)

1. `team-practices.md` — prácticas de equipo/proyecto YA AFIRMADAS y VIGENTES que
   aplican a F1, con su origen (`team.md`/`project.md`/`org.md`), sin
   re-proponerlas.
2. `discovered-rules.md` — prácticas NUEVAS/específicas de F1, cada una marcada
   como **PROPUESTA a afirmar** (P-1 testing posture del cliente nativo Swift;
   P-2 ajuste de backend D-01 aditivo + `pytest` + sin romper cookie PWA;
   P-3 dependencias nativas sólo SDK de Apple; P-4 scope de commit e idioma Swift).
3. `evidence.md` — evidencia (citas a codekb, `memory/` y artefactos de ideación)
   que respalda el reconocimiento y las propuestas.
4. `practices-discovery-timestamp.md` — este fichero.

## Nota de proceso

La **afirmación** de las propuestas de `discovered-rules.md` (y la decisión de en
qué layer de `memory/` aterrizan) es un paso **human-gated posterior**. Esta
etapa **no** edita los ficheros de `memory/`.

## Sources

- `aidlc engine now` (timestamp canónico).
- `aidlc/spaces/default/intents/261016-f1-login-nativo/aidlc-state.md` (scope
  `feature`, fase inception).
- Ficheros producidos en este directorio (listados arriba).

## Assumptions & Open Questions

None.
