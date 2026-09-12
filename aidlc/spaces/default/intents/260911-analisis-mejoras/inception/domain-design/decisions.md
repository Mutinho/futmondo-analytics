# Decisiones de Arquitectura (ADRs) — Plan de Mejoras de futmondo-analytics

> Estas ADRs documentan las decisiones de arquitectura del PLAN de mejoras
> (no implementaciones). Cada una guía el intent futuro que la aborde y respeta
> la restricción dura de coste 0 € y "mantener el stack sin reescrituras grandes".
> [requirements] [memory:M1]

## ADR-001: Persistir el estado de la sincronización y de la sesión (FR1)

### Status
Proposed

### Context
`TaskManager` y `SessionStore` mantienen el estado solo en memoria del proceso.
Un reinicio de la máquina Fly (política de restart/auto-stop) durante un sync
pierde la tarea y la sesión Futmondo, provocando 403 "sesión expirada" y tareas
huérfanas. [architecture] [component-inventory]

### Decision
Persistir el estado de las tareas de sync (y poder reconstruir/degradar la
sesión) fuera de la memoria del proceso, usando la base de datos ya existente
(Neon PostgreSQL) como store — sin introducir infraestructura nueva.

### Consequences
- Positivas: las tareas sobreviven a reinicios; el usuario recibe una acción
  clara en lugar de un 403 opaco; coste 0 € (reutiliza Neon).
- Negativas: añade escrituras a BD por cada actualización de progreso (mitigable
  con throttling); requiere migración de esquema.

### Alternatives Rejected
- Redis/valkey gestionado para el estado: descartado por coste recurrente (viola coste 0 €).
- Dejar el estado en memoria y solo mejorar el mensaje de error: no resuelve la pérdida de tareas.

## ADR-002: Reemplazo transaccional de la caché de Sofascore (FR2)

### Status
Proposed

### Context
`sofascore_sync` hace `DELETE FROM sofascore_cache` antes de repoblar; un fallo a
mitad (baneo de IP, exit code 2) deja la caché vacía o incompleta. [api-documentation]

### Decision
Repoblar en una tabla/lote temporal y sustituir de forma atómica solo si el
repoblado tuvo éxito (swap transaccional), preservando la caché anterior ante fallo.

### Consequences
- Positivas: la caché nunca queda vacía por un fallo parcial; comportamiento predecible.
- Negativas: uso transitorio de más espacio durante el swap (despreciable en Neon free).

### Alternatives Rejected
- Upsert incremental sin borrado: válido pero no limpia entradas obsoletas; se puede combinar más adelante.
- Reintentos sin transaccionalidad: no evita el estado incompleto si se agotan los reintentos.

## ADR-003: No almacenar credenciales Futmondo en claro (FR5)

### Status
Proposed

### Context
`SessionStore` guarda email+password en claro en memoria para re-autenticar
contra Futmondo. [component-inventory] [code-quality-assessment]

### Decision
Evitar almacenar la contraseña: preferir mantener/renovar el token de sesión
Futmondo; si es imprescindible conservar credenciales para re-auth, cifrarlas en
reposo con una clave de entorno. Enlaza con ADR-001 (durabilidad de sesión).

### Consequences
- Positivas: reduce el impacto de un volcado de memoria/estado; mejora la postura de seguridad.
- Negativas: puede requerir manejar expiraciones de sesión Futmondo con re-login explícito.

### Alternatives Rejected
- Seguir guardando en claro: riesgo de exposición inaceptable.
- Vault/servicio de secretos gestionado: descartado por coste recurrente (coste 0 €).

## ADR-004: Consolidar la capa de BD en Neon único y podar residuos (FR14)

### Status
Proposed

### Context
`config.py` soporta SQLite/Turso/PostgreSQL con ramas muertas; `nixpacks.toml`
(Railway) y `migrate_to_turso.py` son residuo; `entrypoint.sh` está muerto;
`constants.py` fija `CHAMPIONSHIP_ID`/`LEAGUE_ID`. [architecture] [code-structure]

### Decision
Consolidar la configuración de BD en Neon PostgreSQL como único backend
productivo, eliminar ramas muertas y residuos tras confirmar que no se usan, y
externalizar los identificadores fijos a configuración/entorno.

### Consequences
- Positivas: menos superficie de error y confusión; código más simple y mantenible.
- Negativas: perder la portabilidad multi-backend (aceptable: no se usa hoy).

### Alternatives Rejected
- Mantener el multi-backend "por si acaso": conserva complejidad y ramas sin probar.
- Migrar a Turso/libSQL: descartado; Neon free cubre la necesidad a coste 0 €.

## ADR-005: Descomponer los god files de forma incremental (FR13)

### Status
Proposed

### Context
`data_manager_v2.py` (166 KB) y `data_sync_service.py` (84 KB) concentran el
riesgo de cambio y son intestables sin fakes. [code-quality-assessment]

### Decision
Abordar la descomposición de forma incremental y guiada por dominio/responsabilidad,
apoyándose en los tests de caracterización existentes para preservar comportamiento,
y NO como una reescritura de golpe. Marcado como "importante, planificar aparte".

### Consequences
- Positivas: reduce el riesgo de introducir regresiones; progreso medible por módulo.
- Negativas: la mejora se extiende en el tiempo (no hay un "big bang" que lo cierre).

### Alternatives Rejected
- Reescritura completa de una vez: alto riesgo de regresiones para un mantenedor único.
- No tocarlos: la deuda sigue frenando el crecimiento y la testabilidad.

## ADR-006: Enfoque global conservador e incremental del plan

### Status
Accepted

### Context
El proyecto lo mantiene una sola persona, con el objetivo de "crecer con
seguridad", manteniendo el stack sin reescrituras grandes y a coste 0 €.
[intent-statement] [memory:M1]

### Decision
El plan prioriza arreglos de bajo riesgo y alto impacto (fiabilidad y seguridad:
FR1, FR2, FR5) por delante de los refactors estructurales grandes (FR13), que
quedan registrados como importantes pero "planificar aparte". Toda propuesta se
limita a soluciones sostenibles en tiers gratuitos.

### Consequences
- Positivas: el plan es realista para un mantenedor único; minimiza el riesgo de romper producción; respeta coste 0 €.
- Negativas: la deuda estructural profunda tarda más en resolverse.

### Alternatives Rejected
- Enfoque agresivo (atacar la deuda estructural cuanto antes): mayor riesgo de regresiones y de salir del tier gratuito.
- Enfoque puramente reactivo (solo arreglar cuando algo se rompe): no cumple el objetivo de "crecer con seguridad".

## Índice de ADRs

| ADR | Título | Estado | FR |
|-----|--------|--------|-----|
| 001 | Persistir estado de sync y sesión | Proposed | FR1 |
| 002 | Caché Sofascore transaccional | Proposed | FR2 |
| 003 | No credenciales en claro | Proposed | FR5 |
| 004 | Consolidar BD en Neon único | Proposed | FR14 |
| 005 | Descomponer god files incremental | Proposed | FR13 |
| 006 | Enfoque global conservador | Accepted | — |
