# Inventario de Componentes — Futmondo Analytics

> Nombres de componente usados verbatim en el bloque `Scope of Analysis` de
> `reverse-engineering-timestamp.md`. Responsabilidad registrada una vez aquí;
> el resto de artefactos cross-referencia.

## core

Configuración y constantes del backend. `config.py` resuelve el tipo de BD en
cascada (`DATABASE_URL` → `TURSO_DATABASE_URL` → fallback `sqlite`) y expone
secretos; **contiene los defaults hardcodeados `CHAMPIONSHIP_ID`/`LEAGUE_ID`**
(residuo mono-usuario, FR14). `constants.py` mantiene el catálogo estático
`LALIGA_TEAMS` (fallback legítimo).
Depende de: variables de entorno.

## services

Lógica de negocio e integraciones. Incluye `db_connection.py` (manager
multi-backend), los god-files `data_manager_v2.py`/`data_sync_service.py`,
`analytics_service.py`, `assistant_service.py`, los clientes
`futmondo_client.py`/`sofascore_client.py`, `integration_errors.py` y
`sync_step_status.py`.
Depende de: `core`, `stores`, BD (Neon), APIs externas.

## api/v1/endpoints

24 routers HTTP montados bajo `/api/v1/*`. Traducen peticiones a llamadas de
servicio. Contiene el doble montaje de `matchdays` (FR15).
Depende de: `services`, `auth`.

## auth

Autenticación JWT (access en memoria + refresh en cookie HttpOnly) y
token/session store; `AuthMiddleware` protege las rutas no públicas.
Depende de: `stores`, `security`, PyJWT.

## stores

Repositorios durables de estado de tareas y sesiones (soporte del sync async y
la sesión Futmondo por usuario).
Depende de: `db_connection` (`services`).

## security

Protección de credenciales (nunca password/token en claro en memoria, BD,
logs ni excepciones).
Depende de: —.

## models

Modelos de datos compartidos.
Depende de: —.

## scripts

Utilidades one-shot: sync, export, `init_db`, y las migraciones a Turso
(`migrate_to_turso.py`, `migrate_data_to_turso.py`) — estas últimas sin uso en
el flujo Neon actual (deuda FR14).
Depende de: `services`, `core`.

## angular-app

SPA Angular 22 (PWA), servida por nginx en producción. Consume la API interna.
No relevante al alcance FR14/FR15 salvo por el consumo del doble prefijo de
`matchdays`.
Depende de: API interna del backend.

## proxy / cron

`proxy` = nginx reverse proxy local; `cron` = app Fly.io de crons
(`daily-sync`, `sofascore-sync`, máquinas one-shot). Ejercitan rutas de sync
pero no cambian la topología de despliegue.
Depende de: backend.

> Dependencias externas (librerías) y cross-paquete internas en
> `dependencies.md`.
