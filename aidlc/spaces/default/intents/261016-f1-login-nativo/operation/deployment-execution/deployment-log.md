# Deployment Log — F1: Login nativo end-to-end

> Fase: operación (deployment-execution). Perspectiva de release engineer. Idioma: castellano;
> identificadores, rutas y comandos verbatim en inglés. F1 ya está **desplegado y validado**: el
> backend D-01 por el CD on-merge a Fly.io, y la app iOS por firma gratuita con `xtool` en el
> iPhone 13 Pro. Este log registra la ejecución real. Coste 0 € salvo la excepción acotada
> (publicación nativa, diferida).

## Canal 1 — Backend D-01 (Fly.io, CD on-merge)

| Paso | Acción | Resultado |
|------|--------|-----------|
| Merge a `main` | PR del backend (`feat/f1-backend-refresh-transport`, commit `f5a51f44`) fusionado | ✅ |
| `verify` | Gate bloqueante: gitleaks + pip-audit + `ruff check` + `pytest` (incl. 8 tests `test_auth_refresh_transport.py`, 422 passed) + `npm audit` + `ng test` | ✅ verde |
| `deploy-backend` | `flyctl deploy` en `./backend` → `futmondo-api` (región `cdg`) | ✅ release publicada |
| `deploy-frontend` | `flyctl deploy` en `./angular-app` → `futmondo-app` (encadenado por `needs:`; sin cambios funcionales) | ✅ |
| `smoke-test` | `curl` a `/health` (5 reintentos, HTTP 200) | ✅ (ver smoke-test-results.md) |
| Migraciones de BD | D-01 no incluye migraciones | N/A — no aplica |

Estrategia: recreate on-merge (sin blue/green ni canary; entorno único). Retrocompatibilidad
garantizada por precedencia cookie → header `X-Refresh-Token` → body: sin feature flag ni ventana
de migración.

## Canal 2 — App iOS (`xtool`, firma gratuita, manual)

| Paso | Acción | Resultado |
|------|--------|-----------|
| Pre-deploy (lógica) | `swift test` en WSL (Swift 6.4) | ✅ 29 passed |
| Build + sign + install | `ios/scripts/install-app.sh` → `xtool dev run` (product `FutmondoApp`, bundleID `com.futmondo.app`) | ✅ instalada en iPhone 13 Pro |
| Trust del perfil | Ajustes del iPhone → Device Management → Trust | ✅ (paso manual de primera instalación) |
| Validación funcional | login contra prod → cerrar/reabrir (auto-login vía Keychain) → logout | ✅ completada por el propietario |

Validez de la firma gratuita: ~7 días. Redespliegue = re-ejecutar el script. Publicación en App
Store **diferida (B-09)** (Apple Developer Program de pago; excepción acotada de coste).

## Pre-deployment checks (resumen)

- Gate de CI bloqueante verde antes del merge: ✅ (un rojo nunca llega a producción).
- Servicios dependientes sanos: Neon PostgreSQL alcanzable (confirmado por `/health` 200).
- Ventana de despliegue: sin ventana formal (single-maintainer, entorno único, on-merge).

## Sources

- [consumes] cd-config.md, deployment-strategy.md (operation/deployment-pipeline);
  environment-inventory.md (operation/environment-provisioning); test-results.md
  (construction/build-and-test: 29 swift test + 422 pytest).
- [code] `.github/workflows/fly-deploy.yml`, `ios/scripts/install-app.sh`; commit `f5a51f44`.
- [memory] team.md `## Deployment`; project.md (coste 0 € + excepción acotada);
  aidlc-shared/operation-fly-stack.md.

## Assumptions & Open Questions

None.
