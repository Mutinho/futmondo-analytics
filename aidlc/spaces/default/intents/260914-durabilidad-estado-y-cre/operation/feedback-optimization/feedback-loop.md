# Feedback Loop — Durabilidad del estado

> Etapa Feedback & Optimization (Operation), documento final. Consolida las mejoras de seguimiento
> reales identificadas durante todo el flujo del intent y las canaliza como entrada para un próximo
> ciclo de Ideation. Coste 0 € en todas las propuestas.

## Qué se entregó (resumen)

El intent `260914-durabilidad-estado-y-cre` hizo durable el estado de sesión (u1) y de tareas de sync
(u2) sobre `futmondo-api`: FR1.1–1.6 (durabilidad, 401 accionable, tareas consultables/marcadas/409)
y FR5 (credenciales cifradas en reposo, nunca en claro). 125 tests, 0 regresiones. Coste 0 €.

## Mejoras de seguimiento (entrada al próximo ciclo)

Priorizadas; todas a coste 0 €:

| # | Mejora | Origen | Prioridad | Nota |
|---|--------|--------|-----------|------|
| 1 | Cerrar la ventana no-atómica SELECT→INSERT en `/trigger` (u2) con índice único parcial sobre estado activo | Revisión de code-generation (R-01, Major) | Media | Estrecha con `min=max=1`; relevante si se escala (NFR5). Cambio pequeño. |
| 2 | Fijar umbral numérico NFR2 y ejecutar el load-test-plan | performance-validation (NFR2 Unverified) | Baja | Solo si el rendimiento pasa a ser preocupación observada. k6/locust + máquina Fly one-shot. |
| 3 | Replicar `--cov` en el job `verify` de `fly-deploy.yml` (paridad con gate de MR) | team.md / nota conocida | Baja | Referencia informativa; gitleaks ya se replicó. |
| 4 | Logging estructurado (`event=...`) para observabilidad por logs fiable | observability-setup | Baja | Hace `fly logs` + grep preciso; base para un `request_id` correlacionable. |
| 5 | Endurecer ruff/ESLint de advisory a bloqueante | team.md (modo escalonado) | Baja | Tras un formateo inicial en commit aislado; considerar familia `S` (bandit) de ruff. |
| 6 | Alinear la región en `docs/DEPLOY.md` (`cdg` vs `mad`) | drift-report | Muy baja | Corrección de documentación. |

## Acción operativa inmediata (recordatorio)

- **Antes de desplegar**: fijar `FUTMONDO_CRED_KEY` en Fly.io `futmondo-api` (validation-report de
  environment-provisioning). Sin él, la rehidratación de sesión degrada a 401 accionable.

## Insights para Ideation

- La deuda de "estado solo en memoria" queda saldada para sesión y tareas de sync. Si aparecen otras
  piezas de estado crítico en memoria (revisar `data_sync_service.py`, cachés en routers), aplicar el
  mismo patrón: capa `stores/` estrecha + BD autoridad + caché best-effort, caracterización primero.
- El patrón de credenciales cifradas en reposo (Fernet + secret de Fly.io) es reutilizable para
  cualquier otro secreto de terceros que hoy viva en claro.

## Estado del workflow

- Workflow del intent **completo**. El bucle de feedback está listo para alimentar un próximo intent
  cuando el equipo decida iterar.
