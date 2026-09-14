# Flujo de Pull Request + Gate de CI

> FR8.1 / NFR4.1. Aun siendo un único desarrollador, los cambios entran a `main`
> a través de **ramas de feature + Pull Request** para **forzar el gate de CI**
> (lint + tests + escaneos) antes de fusionar. Nada aterriza en `main` sin que
> el gate pase.

## Flujo de trabajo

1. Crea una rama de feature de vida corta desde `main`:
   ```bash
   git switch -c feat/mi-cambio
   ```
2. Implementa el cambio. Los tests son un entregable de primera clase: añade o
   actualiza tests con el cambio.
3. Abre un Pull Request hacia `main`. Esto dispara `.github/workflows/ci.yml`.
4. El gate debe pasar (ver más abajo qué bloquea) antes de fusionar.
5. Fusiona con **squash-merge**: cada unidad de trabajo queda como un commit
   limpio en el trunk. Usa *conventional commits* (`feat`/`fix`/`chore`/`docs`).
6. El push a `main` dispara `.github/workflows/fly-deploy.yml`, que reejecuta
   lint+tests (`verify`) antes de desplegar y hace un smoke test `/health`.

## Qué comprueba el gate (`ci.yml`)

| Comprobación | Herramienta | Modo |
|---|---|---|
| Escaneo de secretos | gitleaks | **BLOQUEANTE** desde el inicio |
| Tests backend + cobertura | pytest / pytest-cov | **BLOQUEANTE** |
| Tests frontend headless | ng test (ChromeHeadlessNoSandbox) | **BLOQUEANTE** |
| Lint backend | ruff | Advisory (escalonado) |
| Lint frontend | ESLint (Angular) | Advisory (escalonado) |
| Auditoría de dependencias | pip-audit / npm audit | Advisory (escalonado) |

Escalonado (R-05): ruff/ESLint y las auditorías de dependencias arrancan como
**advisory** (no rompen el gate) para no fallar de golpe sobre la base heredada
sin formatear; pasarán a bloqueantes en un trabajo posterior, tras sanear la
deuda en un commit aislado. El escaneo de **secretos es bloqueante desde ya**.

## Branch protection (configuración en GitHub)

`needs:` no cruza workflows, así que el gate se apoya en **dos** mecanismos:

1. **Required status check** en `main`: en *Settings → Branches → Branch
   protection rules*, marca el job `quality` de `ci.yml` como *required*. Esto
   impide fusionar el PR mientras el gate esté en rojo.
2. **Job `verify` en `fly-deploy.yml`**: defensa en profundidad ante un push
   directo a `main`; el deploy depende de `verify` vía `needs:`.

Recomendado también: activar "Require a pull request before merging" y
"Do not allow bypassing the above settings".

## Comandos de test locales (unit-scoped)

- Backend: `cd backend && python -m pytest tests -q`
- Frontend: `cd angular-app && npx ng test --watch=false --browsers=ChromeHeadlessNoSandbox`

## Endurecimiento de seguridad relacionado

- **JWT** (`backend/app/core/config.py`): el servicio web falla al arrancar si
  `JWT_SECRET` falta o es el default inseguro (NFR1.1). Fija `JWT_SECRET` en los
  secrets de Fly.io.
- **Endpoints destructivos de BD** (`/api/v1/database/reset` y `/populate`):
  devuelven 404 salvo que `ENABLE_DB_ADMIN=1` (NFR1.2). No los habilites en
  producción salvo operación puntual y controlada.
