# Requisitos de Escalabilidad — Backend Security Hardening

> Scope `security-patch`, depth Minimal.

## Alcance

- **NFR-SCAL.1**: Las cinco correcciones no cambian el modelo de despliegue ni la capacidad. La topología se mantiene: dos apps Fly.io `min=max=1` (`shared-cpu-1x`/256 MB) y Neon PostgreSQL tier free. Traza: NFR2 (compatibilidad de stack), restricción de coste 0 €. `[memory:technology-stack.md]`
- **NFR-SCAL.2**: Ninguna corrección introduce estado nuevo, colas, ni recursos que escalen con la carga. La validación de `price` (FR6) y la corrección de refresh (FR9) son operaciones sin estado por petición.

## Proyecciones

- Sin proyecciones de crecimiento nuevas: el intent no altera el perfil de carga. Cualquier propuesta que exigiera escalar más allá de los tiers gratuitos queda fuera de alcance (regla `## Mandated`: coste 0 €). `[memory:project.md]`

## Assumptions & Open Questions

None.

<!-- Re-anclado 2026-09-17 (redo-jump; contenido sin cambios). -->

<!-- Re-guardado 2026-09-17 tras confirmación vigente (contenido sin cambios). -->
