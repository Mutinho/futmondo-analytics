# Mapa de Dependencias Externas — Frontend Coverage Gate

## Elementos externos que bloqueen

**Ninguno.** El intent está totalmente autocontenido: es una intervención sobre configuración de tests, tooling y workflows de CI/CD del propio repo. No depende de APIs externas nuevas, ventanas de disponibilidad de datos, tiempos de aprobación de otros equipos, ni hand-offs externos.

| Elemento | Tipo | Dueño | Lead time | Bolt que bloquea | Plan si se retrasa |
|----------|------|-------|-----------|-------------------|--------------------|
| (ninguno) | — | — | — | — | — |

## Notas

- **Proveedor de cobertura `@vitest/coverage-v8`**: es una devDependency OSS de npm (registro público), no un servicio externo con SLA ni coste. Se fija a versión exacta y se verifica con `npm ci` antes de pushear. No es un bloqueante externo.
- **Gate de CI (GitHub Actions) y despliegue (Fly.io)**: infraestructura existente del equipo, en tiers gratuitos; no introduce dependencia externa nueva.
- Todo el trabajo cabe en el free-tier (coste 0 €).

## Assumptions & Open Questions

- None.
