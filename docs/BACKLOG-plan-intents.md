# Plan de intents — mejoras pendientes del plan de análisis

> Redactado el 2026-09-23. Agrupa las mejoras que quedan pendientes del plan del
> intent de análisis `260911-analisis-mejoras`
> (`inception/requirements-analysis/requirements.md`) en intents cohesivos, tras
> verificar qué han cerrado los intents posteriores. No modifica artefactos de
> intents cerrados. Restricción transversal: coste 0 € (tiers gratuitos).

## Estado del plan de análisis (18 FR)

Ya cerrado por intents posteriores:

| FR | Mejora | Intent |
|----|--------|--------|
| FR2 | Reemplazo transaccional caché Sofascore | `260911-sofascore-cache-atomica` |
| FR1 | Durabilidad estado sync + sesiones | `260914-durabilidad-estado-y-cre` |
| FR5 | No credenciales Futmondo en claro | `260914-durabilidad-estado-y-cre` |
| FR7/FR8/FR9/FR18 | Verificaciones de seguridad backend | `260916-backend-security-hardeni` |
| FR6 | Validar `price` en backend de pujas | `260916-...`, `260921-grupo-a-backend-fiabilid` |
| FR3.1 | Pasos "non-critical" de sync visibles | `260921-grupo-a-backend-fiabilid` |
| FR10, FR17.1/17.2 | Cobertura frontend + gate | `260918-frontend-coverage-gate` |

Lo crítico del plan (FR1, FR2, FR5) está cerrado.

## Pendiente — agrupación en intents

### Intent 1 — Fiabilidad backend: manejo de errores + contratos de integración
- **Requisitos**: FR3.2 + FR4
- **Prioridad**: Importante · **Esfuerzo**: M · **Scope**: `feature`
- **Alcance**:
  - FR3.2: reducir `except Exception`/bare-except (159+6), empezando por los
    `except: pass` de arranque y migraciones; distinguir recuperable vs fatal.
  - FR4: documentar contratos y modos de fallo de Sofascore (baneo IP) y
    Futmondo (endpoints heterogéneos); detección de baneo reflejada en estado
    sin corromper datos.
- **Cohesión**: mismo eje AX3 (fiabilidad), mismas zonas de código
  (`data_sync_service.py`, clientes externos), continuación de FR3.1.

### Intent 2 — Limpieza de configuración y residuos
- **Requisitos**: FR14 + FR15
- **Prioridad**: Importante (FR14) / Opcional (FR15) · **Esfuerzo**: M+S · **Scope**: `refactor`
- **Alcance**:
  - FR14.1: config de BD solo Neon PostgreSQL; eliminar ramas muertas
    SQLite/Turso, `nixpacks.toml`, `migrate_to_turso.py`, `entrypoint.sh` tras
    confirmar que no se usan.
  - FR14.2: quitar `CHAMPIONSHIP_ID`/`LEAGUE_ID` hardcodeados de `constants.py`.
  - FR15: unificar el doble montaje de `matchdays`; sacar del control de
    versiones artefactos basura (`:Zone.Identifier`, `stitch_*`, imágenes sueltas).
- **Cohesión**: poda de bajo riesgo funcional (AX1/AX4), sin lógica nueva.

### Intent 3 — Descomposición de god files
- **Requisitos**: FR13
- **Prioridad**: Importante · **Esfuerzo**: L · **Scope**: `refactor` (multi-Bolt / multi-intent por oleada)
- **Alcance**: plan incremental por dominio de `data_manager_v2.py` (166 KB),
  `data_sync_service.py` (84 KB), `assistant_service.py` (51 KB),
  `analytics_service.py` (34 KB), preservando comportamiento (characterization-first).
- **Cohesión**: el más caro y arriesgado; el análisis ya lo marcó "planificar aparte".
- **Patrón objetivo por god file**: bounded context DDD bajo
  `backend/app/services/<contexto>/` (fachada delgada que preserva la superficie
  pública + `domain/` puerto + `application/` casos de uso + `infrastructure/`
  adaptador con el SQL crudo aislado). El fichero original queda como shim de
  re-export para no romper import paths. Puerto/adaptador propio del contexto
  (DIP) para no acoplar el orden de oleadas.

#### Oleadas (orden por riesgo creciente — BR4.1)

| Oleada | God file | Estado | Intent / rama |
|--------|----------|--------|---------------|
| 1 | `analytics_service.py` (34 KB) | Completada | `260927-god-files-refactor` (rama `refactor/god-files-analytics-wave1`) |
| 2 | `assistant_service.py` (51 KB) | Pendiente | intent nuevo (ver abajo) |
| 3 | `data_sync_service.py` (84 KB) | Pendiente | intent nuevo (ver abajo) |
| 4 | `data_manager_v2.py` (166 KB) | Pendiente | intent nuevo (posibles sub-Bolts por grupo de agregado) |

**Oleada 1 — analytics (HECHA).** Extraído a `backend/app/services/analytics/`
(fachada `AnalyticsService` con 11 `get_*` preservados, `AnalyticsDataPort`,
`DataManagerAnalyticsAdapter` con los 2 SELECT crudos aislados). Consumidores
intactos. Suite verde (218 passed), cobertura 29.75% >= piso 27. Reviewer READY.

**Oleada 2 — assistant (PENDIENTE).** Seams claros ya identificados en
`functional-spec.md`: `AssistantUsageTracker` (agregado propio con tabla), capa
factual (`_try_factual_answer`/`_factual_*`), `ContextBuilder`
(`_build_context`/`_ctx_*` con ~42 `cursor.execute` -> repositorios), guardrails
(`_check_guardrails`, modulo puro); `ask()` queda como orquestador. Superficie a
preservar: `get_assistant_service()` + `async ask(...)`. Cobertura directa hoy
CERO -> caracterizacion just-enough por seam antes de mover. Scope `refactor`.

**Oleada 3 — sync (PENDIENTE).** Un modulo/servicio de aplicacion por dominio de
sync (transactions, clauses, punishments, dream_teams, performance, rosters,
rankings, players, odds, prizes) coordinados por un `sync_all` delgado;
`sync_prizes` ya delega en `prizes/` (patron a replicar). Reemplazos de conjunto
-> repositorios con escritura atomica (BR3.2, patron `team_prizes_writer`).
Superficie a preservar: `sync_*` (10) + `sync_all()`. La caracterizacion de
efecto (DEGRADED/fatal, prizes atomico) ya existe; anadir por dominio antes de
trocear. Scope `refactor`.

**Oleada 4 — data_manager (PENDIENTE, nucleo).** Hub de 8 routers + sync +
analytics; ~94 `cursor.execute`; cobertura directa ~cero. Los 8 agregados de
`entities.md` -> un repositorio por agregado (SRP, BR2.4); `_init_database`/DDL
-> `SchemaInitializer` aislado (no cuenta como agregado). Superficie a preservar:
los 51 metodos publicos de `DataManagerV2`. Requiere **caracterizacion AMPLIA**
de la superficie publica (FR3.1) antes del primer movimiento, con el
`_FakeInMemoryDB` de `conftest.py`. Por tamano puede requerir **sub-Bolts por
grupo de agregado** (schema/DDL, jugadores, transacciones, standings, ...). En
esta oleada, los adaptadores de las oleadas 1-3 se reapuntan de la fachada
`DataManagerV2` a los repositorios reales, sin tocar la logica de los contextos
consumidores. Scope `refactor`.

**Como arrancar cada oleada pendiente**: nuevo intent AI-DLC con
`/aidlc --new-intent --scope refactor "<descripcion de la oleada>"`, reutilizando
este patron y las reglas afirmadas (characterization-first, no ampliar god-files,
no reformatear brownfield, no relajar cobertura, coste 0 EUR).

### Intent 4 — Endurecimiento del gate CI/CD (opcionales)
- **Requisitos**: FR11 + FR12 + FR17.3 + deuda diferida
- **Prioridad**: Opcional · **Esfuerzo**: S/M · **Scope**: `feature`/`infra`
- **Alcance**:
  - FR11: piso de cobertura bloqueante en backend (`fail_under`, ratcheting).
  - FR12: elevar linters/audits de advisory a bloqueante escalonado
    (pip-audit/npm audit primero, luego lint).
  - FR17.3: gate de verificación más completo pre-deploy a coste 0 €.
  - Deuda diferida: paridad de `--cov` backend en el job `verify` de
    `fly-deploy.yml`; SAST/DAST frontend; subir el ratchet de cobertura frontend.
- **Cohesión**: todo tooling de pipeline/CI, mismo tipo de cambio.

### FR16 — suelto o anexo
- Documentar consumo actual dentro de tiers gratuitos e identificar umbrales que
  forzarían salir del free tier. Opcional, esfuerzo M, mayormente documentación.
  Puede ir como anexo al Intent 4 o como tarea de doc independiente.

## Orden recomendado

1. **Intent 1** (FR3.2+FR4) — cierra AX3, baja riesgo de producción.
2. **Intent 2** (FR14+FR15) — bajo riesgo, reduce ruido antes de tocar estructura.
3. **Intent 4** (gate CI opcional) — endurece la red de seguridad antes del refactor grande.
4. **Intent 3** (FR13) — el más caro; entra cuando la red de tests y la limpieza ya lo respaldan.

## Notas transversales (todos los intents)

- Coste 0 € (solo tiers gratuitos).
- Gate bloqueante (gitleaks + pytest + ng test) antes de merge a `main`.
- NO ampliar god-files fuera del Intent 3; código nuevo tras capa/función estrecha testeable.
- Characterization-first en cualquier refactor.
- NUNCA reformatear en masa (Prettier/ruff format); solo quirúrgico.
