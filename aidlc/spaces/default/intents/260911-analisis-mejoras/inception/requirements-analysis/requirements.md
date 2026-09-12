# Requisitos — Plan de Mejoras de futmondo-analytics

> Este documento traduce los hallazgos del análisis (codekb) en requisitos de
> mejora trazables. Cada requisito lleva prioridad (crítico/importante/opcional),
> esfuerzo estimado y criterios de aceptación. Nada se implementa en este trabajo:
> cada requisito es candidato a un intent futuro. Las prioridades siguen el marco
> del scope-document (severidad como eje principal, esfuerzo/retorno como
> desempate) y el apetito de riesgo conservador acordado. [scope-document] [Q1] [Q3]

## Análisis de intención

El objetivo es dejar futmondo-analytics listo para crecer con seguridad,
reduciendo deuda técnica, sin reescrituras grandes y a coste 0 €. El plan
prioriza arreglos de bajo riesgo y alto impacto (fiabilidad y seguridad) por
delante de refactors estructurales grandes, que quedan registrados como
importantes pero marcados para planificar aparte. [intent-statement] [Q3] [memory:M1]

Leyenda de prioridad: **Crítico** = riesgo real de rotura en producción,
seguridad o pérdida de datos; **Importante** = deuda que frena crecimiento o
mantenibilidad; **Opcional** = mejora deseable de bajo impacto. [scope-document]
Esfuerzo: S (pequeño), M (medio), L (grande). [Q1]

## Requisitos funcionales de mejora (por eje)

### Eje 1 — Fiabilidad y robustez (AX3)

**FR1 — Durabilidad del estado de sincronización.** [architecture] [code-quality-assessment]
El estado de las tareas de sync y las sesiones Futmondo vive solo en memoria
(`TaskManager`, `SessionStore`); un reinicio de la máquina Fly pierde tareas en
curso y sesiones, provocando 403 "sesión expirada" y tareas huérfanas.
- Prioridad: **Crítico** · Esfuerzo: M
- FR1.1: Persistir el estado de las tareas de sync (progreso, estado) fuera de la memoria del proceso.
- FR1.2: Persistir o poder reconstruir la sesión Futmondo del usuario tras un reinicio, o degradar con un mensaje claro de re-login en vez de un 403 opaco.
- Criterios de aceptación:
  - Dado un sync en curso, cuando la máquina Fly se reinicia, entonces la tarea puede consultarse y refleja su último estado conocido (no desaparece).
  - Dado un reinicio, cuando el usuario continúa, entonces recibe una acción clara (re-login/reintento) en lugar de un 403 sin contexto.

**FR2 — Reemplazo transaccional de la caché de Sofascore.** [api-documentation] [code-quality-assessment]
`sofascore_sync` hace `DELETE FROM sofascore_cache` antes de repoblar; si el
repoblado falla a mitad (baneo de IP, exit code 2), la caché queda vacía o
incompleta.
- Prioridad: **Crítico** · Esfuerzo: S
- Criterios de aceptación:
  - Dado un repoblado que falla a mitad, cuando termina el proceso, entonces la caché anterior permanece intacta (o se sustituye de forma atómica solo si el repoblado tuvo éxito).

**FR3 — Manejo de errores explícito en la sync de 11 pasos.** [architecture] [code-quality-assessment]
Los pasos `prizes` y `phantoms` degradan excepciones a "non-critical" y hay
`except Exception: pass` silenciosos que enmascaran fallos.
- Prioridad: **Importante** · Esfuerzo: M
- FR3.1: Los pasos degradados a "non-critical" registran el fallo de forma visible (log estructurado y estado en la tarea) en vez de ocultarlo.
- FR3.2: Reducir los `except Exception`/bare-except (159 + 6) empezando por los `except: pass` de arranque y migraciones, distinguiendo error recuperable de fatal.
- Criterios de aceptación:
  - Dado un fallo en un paso "non-critical", cuando el sync termina, entonces la tarea reporta ese paso como degradado con su motivo (no como éxito).

**FR4 — Robustez de las integraciones externas.** [api-documentation] [dependencies]
Sofascore (API no oficial vía `curl_cffi`) es frágil (baneo de IP); Futmondo
tiene endpoints heterogéneos.
- Prioridad: **Importante** · Esfuerzo: M
- Criterios de aceptación:
  - Dado un baneo/entrada fallida de Sofascore, cuando ocurre, entonces el sistema lo detecta, no corrompe datos (ver FR2) y lo refleja en el estado.
  - Documentar contratos y modos de fallo esperados de ambas integraciones.

### Eje 2 — Seguridad (AX2)

**FR5 — No almacenar credenciales Futmondo en claro.** [code-quality-assessment] [component-inventory]
`SessionStore` guarda email+password en claro en memoria.
- Prioridad: **Crítico** · Esfuerzo: M
- Criterios de aceptación:
  - Dado un usuario autenticado, cuando se inspecciona el estado del proceso, entonces la contraseña Futmondo no está almacenada en claro (se evita guardarla, se cifra, o se sustituye por un token/re-auth).

**FR6 — Validación de `price` en el backend de pujas.** [api-documentation] [architecture]
`market.py::place_bid` acepta `price` sin validar rango/positividad; solo el
frontend valida.
- Prioridad: **Importante** · Esfuerzo: S
- Criterios de aceptación:
  - Dado un `price` fuera de rango o no positivo enviado directamente a `POST /api/v1/market/bid`, cuando llega al backend, entonces se rechaza con un error de validación antes de proxyar a Futmondo.

**FR7 — Verificar exposición de `GET /api/v1/photos/{player_id}`.** [api-documentation]
Posible endpoint servido sin auth (no figura en `AUTH_EXCLUDED_PATHS`).
- Prioridad: **Importante (a verificar)** · Esfuerzo: S
- Criterios de aceptación:
  - Primer paso: confirmar si el endpoint es accesible sin token. Si lo es y no debería, entonces requerir auth; si es intencional, documentarlo como excepción explícita.

**FR8 — Confirmar que `SSL_VERIFY=0` no llega a producción.** [code-quality-assessment]
`docker-compose.yml` fija `SSL_VERIFY=0` (local).
- Prioridad: **Importante (a verificar)** · Esfuerzo: S
- Criterios de aceptación:
  - Confirmar que la verificación TLS está activa en producción; si hay riesgo de propagación, aislar el flag al entorno local de forma inequívoca.

**FR9 — Confirmar/corregir el bug de expiración de refresh token.** [code-quality-assessment] [component-inventory]
`token_store.is_refresh_token_valid` tiene un ternario ambiguo (naive/aware
datetimes).
- Prioridad: **Importante (a verificar)** · Esfuerzo: S
- Criterios de aceptación:
  - Primer paso: test dedicado que reproduzca la comparación de expiración. Si evalúa mal, entonces corregir y cubrir con test de regresión.

**FR18 — Confirmar que la guarda de los endpoints destructivos se mantiene en producción.** [api-documentation] [code-quality-assessment]
`POST /api/v1/database/reset` y `POST /api/v1/database/populate` deben quedar
inaccesibles (404) salvo con `ENABLE_DB_ADMIN` activado.
- Prioridad: **Importante (a verificar)** · Esfuerzo: S
- Criterios de aceptación:
  - Primer paso: confirmar que en producción `ENABLE_DB_ADMIN` está desactivado y ambos endpoints devuelven 404. Si no, entonces corregir la configuración; añadir un test que verifique la guarda.

### Eje 3 — Calidad y prácticas de ingeniería (AX5)

**FR10 — Cobertura de tests en el frontend.** [code-quality-assessment]
`angular.json` fija `skipTests: true` global y solo existe 1 spec, pese a que
`ci.yml` marca `ng test` como bloqueante (gate pasa con cobertura ~0).
- Prioridad: **Importante** · Esfuerzo: M
- FR10.1: Quitar `skipTests: true` (o justificarlo) para que los componentes/servicios nuevos nazcan con test.
- FR10.2: Establecer un piso mínimo de cobertura razonable y creciente (sin coste; Karma ya está configurado).
- Criterios de aceptación:
  - Dado un componente/servicio nuevo, cuando se genera, entonces se crea su archivo de test.
  - `ng test` deja de pasar trivialmente con cobertura ~0 (existe un umbral efectivo).

**FR11 — Piso de cobertura en el backend.** [code-quality-assessment]
`--cov=app` disponible pero sin piso bloqueante.
- Prioridad: **Opcional** · Esfuerzo: S
- Criterios de aceptación:
  - Se define un umbral de cobertura de partida (no regresivo) que el CI comprueba.

**FR12 — Elevar linters/audits de advisory a bloqueante de forma escalonada.** [code-quality-assessment]
ruff/ESLint/pip-audit/npm audit son advisory (decisión escalonada R-05).
- Prioridad: **Opcional** · Esfuerzo: S
- Criterios de aceptación:
  - Existe un plan escalonado para volver bloqueantes primero seguridad (pip-audit/npm audit) y luego lint, sin romper el flujo actual.

**FR17 — Endurecer el pipeline de despliegue con verificación efectiva.** [code-quality-assessment]
`fly-deploy.yml` tiene un job `verify` (pytest + `ng test`) antes de desplegar,
pero hereda la debilidad de FR10 (el gate de tests pasa con cobertura ~0), dando
falsa sensación de seguridad; el smoke test `/health` post-deploy no tiene una
acción de fallo/rollback claramente definida; el despliegue es deploy-on-push a
`main` sin gate intermedio.
- Prioridad: **Importante** · Esfuerzo: M
- FR17.1: El job `verify` de despliegue ejecuta una suite de tests con cobertura efectiva (depende de FR10/FR11), de modo que un despliegue no procede si los tests no son significativos.
- FR17.2: Definir el comportamiento ante fallo del smoke test `/health` post-deploy (abortar / rollback documentado, enlazando con `docs/ROLLBACK.md`).
- FR17.3 (opcional): Evaluar un gate de verificación más completo antes del deploy a producción, respetando coste 0 € (GitHub Actions free).
- Criterios de aceptación:
  - Dado un cambio que rompe tests significativos, cuando se hace push a `main`, entonces el despliegue no llega a producción.
  - Dado un fallo del smoke test `/health` post-deploy, entonces hay una acción de rollback/aborto definida y documentada.

### Eje 4 — Arquitectura y estructura de código (AX1)

**FR13 — Descomponer los "god files".** [code-quality-assessment] [component-inventory]
`data_manager_v2.py` (166 KB), `data_sync_service.py` (84 KB),
`assistant_service.py` (51 KB), `analytics_service.py` (34 KB) concentran
riesgo y son intestables sin fakes.
- Prioridad: **Importante — alto esfuerzo/riesgo, planificar aparte** · Esfuerzo: L
- Criterios de aceptación:
  - Existe un plan de descomposición incremental (por dominio/responsabilidad) que preserva comportamiento (apoyado en los tests de caracterización existentes) y no se aborda de golpe.

**FR14 — Podar la configuración multi-backend de BD y el residuo de plataformas.** [architecture] [code-structure]
`config.py` soporta SQLite/Turso/PostgreSQL con ramas muertas; `nixpacks.toml`
(Railway) y `migrate_to_turso.py` son residuales; `entrypoint.sh` está muerto;
`constants.py` fija `CHAMPIONSHIP_ID`/`LEAGUE_ID` hardcodeados.
- Prioridad: **Importante** · Esfuerzo: M
- FR14.1: La configuración de BD refleja solo Neon PostgreSQL; se eliminan ramas muertas y residuos (`nixpacks.toml`, scripts Turso, `entrypoint.sh`) tras confirmar que no se usan.
- FR14.2: Los identificadores fijos (`CHAMPIONSHIP_ID`, `LEAGUE_ID`) dejan de estar hardcodeados en `constants.py` y pasan a configuración/entorno o se derivan por usuario.
- Criterios de aceptación:
  - La configuración de BD refleja solo Neon PostgreSQL; se eliminan ramas muertas y residuos tras confirmar que no se usan.
  - No quedan identificadores de campeonato/liga hardcodeados en el código.

**FR15 — Eliminar el doble montaje de rutas y limpiar artefactos versionados.** [api-documentation] [code-quality-assessment]
`matchdays` bajo `/api/v1/matchdays` y `/v1/matchdays`; imágenes sueltas y
ficheros `:Zone.Identifier`/`stitch_*` en la raíz.
- Prioridad: **Opcional** · Esfuerzo: S
- Criterios de aceptación:
  - Existe un único montaje de `matchdays` (o se documenta por qué son dos); los artefactos innecesarios salen del control de versiones.

### Eje 5 — Rendimiento y coste (AX4)

**FR16 — Revisar el patrón de llamadas y recursos dentro de tiers gratuitos.** [architecture] [dependencies] [memory:M1]
El coste 0 € es una restricción dura; conviene verificar que el patrón de sync
y las llamadas externas no fuercen a salir de los tiers gratuitos al crecer.
- Prioridad: **Opcional** · Esfuerzo: M
- Criterios de aceptación:
  - Se documenta el consumo actual (Fly `min_machines_running=1` 256 MB, crons one-shot, pool 5-20) y se identifican los umbrales que obligarían a salir del tier gratuito, con mitigaciones a coste 0 €.

## Requisitos no funcionales

Estos NFR se detallarán con objetivos medibles en la etapa NFR Requirements.

- **NFR1 — Fiabilidad**: las operaciones de larga duración (sync) deben sobrevivir a reinicios de la infraestructura sin pérdida de estado observable. [architecture]
- **NFR2 — Seguridad**: no se almacenan secretos ni credenciales en claro; toda entrada de usuario se valida en el backend. [code-quality-assessment]
- **NFR3 — Mantenibilidad**: reducir el tamaño de los módulos y el manejo de errores demasiado amplio para bajar el riesgo de cambio. [code-quality-assessment]
- **NFR4 — Rendimiento/coste**: el sistema opera dentro de tiers gratuitos; se define el umbral de crecimiento que lo pondría en riesgo. [memory:M1]
- **NFR5 — Testabilidad**: componentes nuevos nacen con test; existe un umbral de cobertura efectivo, del que depende la fiabilidad del gate de despliegue (FR17). [code-quality-assessment]
- **NFR6 — Fiabilidad del despliegue**: el pipeline no promueve a producción cambios cuyos tests no sean significativos, y define una acción de rollback ante fallo del smoke test post-deploy (FR17). [code-quality-assessment]

## Constraints

- Mantener el stack actual (Angular + FastAPI + Neon + Fly.io); sin reescrituras grandes. [intent-statement]
- Coste 0 €: solo soluciones sostenibles en tiers gratuitos. [intent-statement] [memory:M1]
- Este trabajo produce solo el plan; la implementación va a intents futuros. [scope-document]

## Assumptions

- El endurecimiento de seguridad ya presente (JWT fail-fast, `ENABLE_DB_ADMIN` 404, refresh HttpOnly, CORS whitelist, gitleaks bloqueante) se mantiene y no se revierte. [code-quality-assessment] [assumption]

## Out of scope

- Implementar, diseñar en detalle o desplegar cualquiera de estas mejoras. [scope-document]
- Rediseño de UI/UX y dictámenes legales/regulatorios (pueden señalarse como hallazgos, no se ejecutan). [scope-document]

## Open questions

- ¿Cuál es el volumen real de uso (número de usuarios/campeonatos) que ayudaría a fijar los umbrales de NFR4? — se resolverá o se asumirá conservador en NFR Requirements.
