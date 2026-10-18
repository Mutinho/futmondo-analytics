# Environment Inventory — F1: Login nativo end-to-end

> Fase: operación (environment-provisioning). Perspectiva de platform engineer. Idioma: castellano;
> identificadores, rutas y claves verbatim en inglés. F1 **no provisiona entornos nuevos**: el
> stack de producción (Fly.io + Neon) ya existe y está operativo. Este inventario documenta el
> entorno real y qué cambia (y qué no) con F1. Adaptación AWS → equivalente gratuito según
> `aidlc-shared/operation-fly-stack.md`; coste 0 € salvo la excepción acotada (publicación nativa,
> diferida).

## Entorno único de producción (ya existente, sin staging)

| Recurso | Plataforma | Config | Check | Cambio en F1 |
|---------|-----------|--------|-------|--------------|
| Backend `futmondo-api` | Fly.io (región `cdg`) | puerto 8000, FastAPI/Python 3.12 | `/health` → 200 `{"status":"healthy"}` | Redesplegado con D-01 (aditivo); **sin cambio de topología** |
| Frontend `futmondo-app` | Fly.io (región `cdg`) | nginx, puerto 80 | `/` | Sin cambios funcionales en F1 |
| Base de datos | Neon PostgreSQL (Frankfurt, tier free) | serverless | conexión TLS desde backend | **Sin cambios de esquema** (D-01 no migra) |
| App nativa iOS | iPhone 13 Pro (dispositivo del propietario) | `FutmondoApp`, bundleID `com.futmondo.app` | validación manual en dispositivo | **Nueva** — instalada por firma gratuita con `xtool`, no es un entorno gestionado |

## Secretos y parámetros (auditoría)

| Secreto | Dónde | Estado en F1 |
|---------|-------|--------------|
| `FLY_API_TOKEN` | GitHub Actions secrets | Sin cambios (despliegue backend) |
| `JWT_SECRET` | Fly.io secrets (prod) / efímero en CI | Sin cambios; no-default en prod (NFR1.1); D-01 **no añade secretos** |
| `DATABASE_URL` (Neon) | Fly.io secrets | Sin cambios |
| Credenciales de firma iOS | Local en WSL (Apple ID free-signing) | **No es un secreto del repo**; la firma gratuita no almacena credencial (el script falla ruidoso y no persiste nada) |

Ningún secreto en claro en el repo; `gitleaks` es bloqueante en ambos gates y escanea también
`ios/` (sin secretos). D-01 es aditivo: no introduce ni rota secretos.

## Conectividad

- La app iOS apunta al backend prod `https://futmondo-api.fly.dev` (hardcoded en `FutmondoApp.swift`),
  HTTPS/TLS. No hay VPC peering ni cross-account: Fly.io gestiona red/routing y el TLS a Neon.
- El refresh token del cliente nativo viaja por body (login) / header `X-Refresh-Token` sobre TLS;
  se guarda en el **iOS Keychain** (nunca en claro) — garantía de seguridad durable preservada.

## Mapeo de adaptación (términos AWS del stage → este stack)

| Término AWS del stage | En este stack | Estado |
|---|---|---|
| Provisión de entornos con IaC | Entorno Fly.io + Neon **ya provisionado**; F1 no crea infra | Sustituido |
| VPC / subnets / security groups / NACL | Fly.io gestiona red/routing | NO-APLICA |
| Secrets Manager / Parameter Store | Fly.io secrets + GitHub Actions secrets | Sustituido |
| Cross-account / cross-VPC connectivity | Única app pública + TLS a Neon; sin peering | NO-APLICA |
| Stack deployment logs | `fly logs` / `fly status` (observación pull) | Aplica |

## Artefactos consumidos no disponibles

`infrastructure-specification.md` (por unidad de construcción) **no existe**: infrastructure-design
se reportó `skipped` en los 3 bolts (sin infra nueva). No se inventa; el inventario se toma del
entorno real (`fly.toml`, `fly-deploy.yml`, `team.md` → `## Deployment`).

## Sources

- [consumes] cd-config.md (operation/deployment-pipeline).
- [consumes] infrastructure-specification.md — NO existe (infrastructure-design `skipped`).
- [code] `.github/workflows/fly-deploy.yml`, `ios/scripts/install-app.sh`, `ios/Sources/FutmondoApp/FutmondoApp.swift`.
- [memory] team.md `## Deployment` (topología Fly.io + Neon); project.md (coste 0 €, Keychain,
  JWT no-default); aidlc-shared/operation-fly-stack.md.

## Assumptions & Open Questions

None.
