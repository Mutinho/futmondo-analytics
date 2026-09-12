# Requisitos de Observabilidad — Plan de Mejoras de futmondo-analytics


> Nivel de observabilidad sostenible a coste 0 €: logs estructurados + healthcheck
> existente + alertas básicas gratuitas. Derivado de NFR1/NFR3 de `requirements.md`.
> [requirements] [technology-stack] [memory:M1]

## Logging

- **NFR3.1** — La aplicación emite logs estructurados de eventos significativos
  (login, arranque/fin de sync, fallo de paso de sync, errores de integración),
  sin registrar datos sensibles (contraseñas, tokens). Verificación: revisión de
  que los logs no contienen secretos. Origen: FR3. [requirements]
- **NFR3.2** — Los pasos "non-critical" de la sync que fallan quedan registrados de
  forma visible (nivel WARN/ERROR con contexto), no silenciados. Origen: FR3. [requirements]

## Health y métricas

- **NFR1.7** — Se mantiene el healthcheck `/health` existente, usado por el smoke
  test post-deploy (enlaza con FR17). [requirements]
- **NFR3.3** — Métricas básicas observables desde los logs de Fly (arranques,
  reinicios, errores); sin plataforma de observabilidad de pago. [memory:M1]

## Alertas (opciones gratuitas)

- **NFR3.4** — Alerta básica ante fallo de un workflow de sync programada
  (`daily-sync.yml`, `sofascore-sync.yml`) usando notificaciones gratuitas de
  GitHub Actions (fallo de workflow). Origen: FR3, FR17. [requirements]
- **NFR3.5** — Alerta/registro ante fallo del smoke test `/health` post-deploy,
  ligado a la acción de rollback de FR17. [requirements]

## Anti-patrones a evitar

- No registrar PII/credenciales/tokens en logs (NFR3.1).
- No introducir dependencias de observabilidad con coste recurrente (coste 0 €). [memory:M1]

## Assumptions & Open Questions

- Se asume que las notificaciones gratuitas de GitHub Actions y los logs de Fly
  cubren la necesidad de alertas de un mantenedor único; si no bastara, se
  buscaría otra opción gratuita antes que una de pago. [assumption]
