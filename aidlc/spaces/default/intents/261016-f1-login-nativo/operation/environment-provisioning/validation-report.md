# Validation Report — F1: Login nativo end-to-end

> Fase: operación (environment-provisioning). Idioma: castellano; tokens técnicos verbatim en
> inglés. Valida que el entorno (ya existente) soporta F1 sin cambios de topología. Herramientas de
> validación gratuitas (curl `/health`, `fly status`/`fly logs`, validación manual en dispositivo);
> coste 0 €.

## Resultado de validación

| Comprobación | Método | Resultado |
|--------------|--------|-----------|
| Backend `futmondo-api` sano tras D-01 | `curl https://futmondo-api.fly.dev/health` | ✅ HTTP 200 `{"status":"healthy"}` (verificado en vivo 2026-10-18) |
| D-01 desplegado en prod | PR backend mergeado + `fly-deploy.yml` verde | ✅ Desplegado (gate `verify` pasó, smoke `/health` OK) |
| Esquema de Neon sin cambios | D-01 no incluye migraciones | ✅ Sin acción requerida |
| Secretos sin regresión | `gitleaks` bloqueante en ambos gates | ✅ Sin secretos en el árbol (incl. `ios/`) |
| `JWT_SECRET` no-default en prod | NFR1.1 (arranque del servicio) | ✅ Invariante preservada; D-01 no lo toca |
| App iOS instalable y funcional | `install-app.sh` + validación manual en iPhone 13 Pro | ✅ login → auto-login (Keychain) → logout (completada por el propietario) |
| Refresh token en almacenamiento seguro | revisión de código `KeychainTokenStore` + flujo en dispositivo | ✅ iOS Keychain, nunca en claro (regla durable) |

## Posture de seguridad (validación delegada: NO-APLICA formal)

El stage prevé invocar a `aidlc-devsecops-agent`/`aidlc-compliance-agent` para validar posture de
seguridad de infra provisionada. En F1 **no se provisiona infra nueva** y `collaborators: off`, así
que no hay provisión AWS que auditar. Los controles de seguridad relevantes a F1 ya están cubiertos
y verificados:

- Transporte del refresh token sobre TLS; no se registra el body del token (guardarraíl de
  seguridad de D-01, documentado en security-requirements del bolt backend).
- Refresh token nativo en iOS Keychain (nunca `ApplicationSettings`/`localStorage` en claro).
- `gitleaks` + `pip-audit` + `npm audit` bloqueantes en ambos gates (control de cadena de
  suministro durable).

## Validación de conectividad

- App iOS → `https://futmondo-api.fly.dev` (TLS): verificada por el flujo de login real en el
  dispositivo (el login contra prod devolvió sesión; el auto-login refrescó vía Keychain).
- Backend → Neon (TLS): sin cambios; el `/health` 200 confirma la conexión de arranque.

## Términos AWS del stage marcados NO-APLICA

- VPC/subnets/security groups/NACL, cross-account/cross-VPC: Fly.io gestiona red/routing;
  NO-APLICA.
- Secrets Manager/Parameter Store audit formal: sustituido por auditoría de Fly.io/GitHub Actions
  secrets (ver environment-inventory.md).
- Stack deployment logs de IaC: sustituido por `fly logs`/`fly status` (observación pull).

## Sources

- [consumes] cd-config.md; environment-inventory.md.
- [consumes] infrastructure-specification.md — NO existe (infrastructure-design `skipped`).
- [code] validación en vivo `curl /health`; `.github/workflows/fly-deploy.yml`; test-results.md
  (construction/build-and-test: 29 swift test + 422 pytest).
- [memory] phases/operation.md (health check de verificación); project.md (coste 0 €, Keychain,
  JWT no-default); aidlc-shared/operation-fly-stack.md.

## Assumptions & Open Questions

None.
