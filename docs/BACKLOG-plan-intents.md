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
- **Prioridad**: Importante · **Esfuerzo**: L · **Scope**: `refactor` (multi-Bolt)
- **Alcance**: plan incremental por dominio de `data_manager_v2.py` (166 KB),
  `data_sync_service.py` (84 KB), `assistant_service.py` (51 KB),
  `analytics_service.py` (34 KB), preservando comportamiento (characterization-first).
- **Cohesión**: el más caro y arriesgado; el análisis ya lo marcó "planificar aparte".

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
