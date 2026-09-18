# Reverse Engineering — Decisión de escaneo del Code KB

**Repo:** `futmondo-analytics` (workspace root; el intent no registra `repos`)
**Store existente:** `aidlc/spaces/default/codekb/futmondo-analytics/`
**Veredicto del guard:** `STALE` — los paths analizados han cambiado desde que
se construyó el store (último intent que lo escribió: `260916-backend-security-hardeni`).

Como el store está desactualizado, no se ofrece reutilizarlo tal cual. Hay que
reescanear. El intent activo (`260918-matchday-prizes-calc`) trata sobre la
**mejora del cálculo de premios de las jornadas (matchday prizes)** — un área
acotada del backend de finanzas/analytics.

## Pregunta

Existe un Code KB para `futmondo-analytics` pero sus paths analizados han
cambiado desde que se construyó (veredicto `STALE`). Un **full rescan** lo
reemplaza por completo; un **focused scan** fusiona en él (preserva la prosa
previa fuera del área escaneada y degrada a superficial la cobertura profunda
que no se pueda re-verificar). ¿Cómo debe correr el escaneo?

- A. Full rescan — reconstruir el store cubriendo todo el repo (reemplaza los 9 artefactos)
- B. Focused scan — escanear el área de este intent (cálculo de premios de jornadas: módulos de finanzas/analytics del backend y su superficie relacionada) y extender el store; preservar la prosa previa fuera de esa área
- X. Other (please specify)

[Answer]: B
