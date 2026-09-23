# Feedback loop — Fiabilidad de la sync

> Conversation language: Spanish. Última etapa del ciclo AI-DLC. Este documento
> recoge los insumos para un futuro ciclo de Ideation. Coste 0 €.

## Qué entregó este intent

- Fiabilidad **observable** de la sync: los pasos non-critical (`prizes`,
  `phantoms`) que fallan quedan `degraded` (no `done`) con `reason` + log
  estructurado (FR3.1/NFR1).
- Manejo de errores acotado en arranque/migraciones + camino de sync: los
  fallos fatales se propagan con contexto; los recuperables se registran (FR3.2).
- Techo de sanidad del `price` de puja (422 antes de proxyar) como defensa en
  profundidad (FR6/NFR5).
- 16 tests `pytest` significativos nuevos; suite 166 en verde.

## Nuevos datos disponibles (antes inexistentes)

- El log estructurado `sync step degraded` (`sync_step`, `reason`) permite, por
  primera vez, saber **qué paso** de la sync falla y **con qué frecuencia**. Es
  materia prima para decisiones de robustez futuras.

## Insumos para el próximo ciclo de Ideation (backlog)

1. **Robustez de pasos concretos**: si un paso aparece `degraded` de forma
   recurrente en `fly logs`, abrir un intent para hacerlo resiliente (retry,
   fallback) en lugar de solo degradar.
2. **Durabilidad del estado en memoria**: `TaskManager`/syncs en curso se pierden
   en cada redeploy (limitación aceptada). Candidato a un intent de durabilidad.
3. **Deuda de pipeline diferida** (registrada, fuera de alcance de este intent):
   - Paridad de la señal de cobertura `--cov` de backend en el job `verify`.
   - SAST/DAST del frontend más allá de ESLint advisory.
4. **Observabilidad de pago (opcional, rompería coste 0 €)**: SLOs formales con
   burn-rate, dashboards y tracing distribuido — solo si el proyecto decide
   asumir coste; hoy diferidos por mandato.

## Toil operativo

- Rollback e inspección de logs siguen siendo manuales por diseño (coste 0 €).
  Automatizarlos requeriría servicios de pago; diferido.

## Cierre del ciclo

- El intent se despliega on-merge a `main` (gate `verify` bloqueante + smoke
  test `/health`). Rollback documentado, sin reversión de datos (sin migración).
- Este documento alimenta el siguiente ciclo de Ideation si se decide iterar.

## Sources

- Todos los artefactos de Operation de este intent,
  `construction/build-and-test/test-results.md`, `team.md`/`project.md` (deuda
  diferida y mandato coste 0 €).

## Assumptions & Open Questions

None.
