# Requisitos de Observabilidad — Backend Security Hardening

> Scope `security-patch`, depth Minimal. Adaptado al stack real (Fly.io + Neon, coste 0 €).

## Logging (con herramientas gratuitas)

- **NFR-OBS.1** (FR6): El rechazo por validación de `price` produce una respuesta 422 estándar de FastAPI, visible en los logs de acceso (`fly logs`). No se requiere logging adicional; no registrar el `price` completo si pudiera ser ruido, pero sí es aceptable el log estándar de 422. Traza: FR6.
- **NFR-OBS.2** (FR18): Los intentos contra los endpoints de administración cerrados devuelven 404, observables en `fly logs`. Sin dashboard ni alerta nueva (coste 0 €).

## SLI/SLO

- **NFR-OBS.3**: Sin SLO formales nuevos (burn-rate, tracing distribuido y anomaly detection ML exigen servicios de pago → NO-APLICA para este intent). El healthcheck `/health` y el smoke test de release siguen siendo la verificación de disponibilidad. Traza: regla aprendida de Operation (adaptar a Fly.io/Neon, coste 0 €). `[memory:project.md]`

## Alertas

- **NFR-OBS.4**: Sin umbrales de alerta nuevos. Las correcciones no introducen componentes que requieran métricas de error dedicadas más allá de los logs existentes de Fly.io.

## Assumptions & Open Questions

None.

<!-- Re-anclado 2026-09-17 (redo-jump; contenido sin cambios). -->

<!-- Re-guardado 2026-09-17 tras confirmación vigente (contenido sin cambios). -->
