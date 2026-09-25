# Reliability Requirements — u2-integrations (Integraciones)

Fiabilidad de la ruta de integración/sync: el corazón de este intent. La taxonomía
recuperable/fatal y la no-corrupción son los requisitos de fiabilidad centrales.
Objetivo expresado como SLI informal (Q3), coherente con el mandato coste 0 € y
la naturaleza batch del sync (crons Fly one-shot + bajo demanda).

Consume: `functional-spec.md`, `rules.md`, `requirements.md`, `contract-summary.md`.
Perspectiva inline: QA (fiabilidad).

## Requisitos de fiabilidad (derivados)

| ID | Requisito | Fuente | Verificación |
|----|-----------|--------|--------------|
| NFR2.1 | **No-corrupción**: ante fallo fatal en un punto de escritura (`team_prizes`), la tabla/caché queda todo-o-nada (reemplazo transaccional atómico), nunca a medias. | NFR2 (functional-design BR5.1) | Spec que fuerza el fallo y asvera el estado consistente (BR5.2) |
| NFR2.2 | **Degradación observable**: un fallo recuperable marca el paso `DEGRADED` (vía `sync_step_status.py`) y la operación de sync NO falla; continúa con los pasos restantes. | FR3.2.1, FR4.4 | Spec de efecto: paso DEGRADED + operación no falla |
| NFR2.3 | **Fallo fatal limpio**: un fallo fatal (baneo, o recuperable elevado en punto de escritura) propaga la excepción tipada y aborta sin dejar datos a medias. | FR3.2.1, NFR2 | Spec de efecto: excepción propagada + estado íntegro |
| NFR-rel.1 | **Timeout acotado**: ninguna llamada de integración espera de forma ilimitada; un timeout se clasifica recuperable (`IntegrationTimeoutError`) y degrada el paso. | Q2, FR4.4 | Spec: timeout → DEGRADED (recuperable) |
| NFR4.1 | **Sin regresión**: la suite `pytest` existente permanece en verde; el gate CI bloqueante (gitleaks + `pytest` + `ng test`) pasa antes de merge. | NFR4 | CI verde |

## Objetivo de fiabilidad (SLI informal — Q3)

- **SLI**: (1) ausencia de pasos `DEGRADED` **inesperados** en `fly logs`, y (2) no-corrupción de datos verificada por spec tras un fallo forzado.
- **SLA formal**: no aplica (proyecto personal, coste 0 €, sin compromiso externo).
- **SLO con burn-rate**: **NO-APLICA / diferido** — requiere métricas gestionadas de pago; se documenta la alternativa gratuita (`fly logs` + `grep`) en lugar de inventar infraestructura. (Corrección de proyecto ya afirmada para etapas de Operation, extendida aquí.)
- **Tolerancia a fallo puntual**: los crons (04:30 / 05:00 UTC) reintentan en la siguiente ejecución programada; un fallo aislado de un proveedor no exige disponibilidad porcentual formal.

## Recuperación

- **RTO/RPO formales**: no aplican como objetivos numéricos en U2. El sync es idempotente-por-reejecución (recomputa el estado); un fallo se recupera en la siguiente ventana de cron o disparo manual.
- **Rollback** de release: mecanismo Fly.io (redeploy de la release anterior), runbook `docs/ROLLBACK.md` — **sin cambio** en este intent.
- **Sin retry/backoff** dentro del sync (fuera de alcance, Q2 del intent): recuperable = detectar + degradar, no reintentar.

## Assumptions & Open Questions

None.
