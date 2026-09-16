# External Dependency Map — Durabilidad del estado y credenciales

> Ítems fuera del equipo que podrían retrasar el build (APIs, datos, aprobaciones,
> hand-offs), mapeados a los Bolts que los consumen. Para este intent el mapa es
> esencialmente vacío: todo es código dentro de `futmondo-api` sobre infraestructura
> ya aprovisionada.

## Sources

- delivery-planning-questions.md (Q5-A: nada externo bloquea) [Q5]
- team.md (Neon PostgreSQL ya en producción; Fly.io free) [scope]

## Dependencias externas

| Dependencia | Dueño | Duración/ventana | Bolt que bloquea | Plan si se retrasa |
|-------------|-------|------------------|------------------|--------------------|
| _(ninguna bloqueante)_ | — | — | — | — |

## Notas

- **Neon PostgreSQL:** ya aprovisionado y en uso (no es una dependencia nueva ni un bloqueo);
  las tablas de estado durable se crean con las migraciones ad-hoc existentes (`CREATE TABLE
  IF NOT EXISTS`) dentro del propio Bolt.
- **API Futmondo:** ya integrada (cliente existente); se usa para la re-autenticación en la
  reconstrucción de sesión (Bolt 1), pero no bloquea el build ni requiere hand-off externo.
- **Aprobaciones/hand-offs externos:** ninguno — ejecución por AI en una sola sesión, con
  gates de aprobación humana internos al flujo.
- **Coste:** todo dentro de tiers gratuitos (Neon free, Fly.io free, GitHub Actions free) — 0 €.
