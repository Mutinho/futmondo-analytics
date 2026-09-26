# Validation Report — Intent 4 (gate CI/CD hardening)

> Fase Operation. Validación del entorno existente y de las expectativas del
> gate endurecido sobre el entorno. Adaptado al stack real (Fly.io + Neon, coste
> 0 €); NO-APLICA lo AWS-específico. Perspectivas: plataforma + DevSecOps +
> compliance (inline).

## Resultado de validación

| Validación | Criterio | Resultado | Notas |
|------------|----------|-----------|-------|
| Salud del backend | `futmondo-api` responde `/health` HTTP 200 | OK (verificación de release existente) | El smoke test post-deploy lo ejercita en cada release |
| Salud del frontend | `futmondo-app` responde `/` | OK (healthcheck existente) | nginx |
| Conexión a BD | Neon accesible vía `DATABASE_URL` (TLS) | OK (producción operativa) | Sin cambios |
| Secretos presentes | `JWT_SECRET`, `DATABASE_URL` (Fly); `FLY_API_TOKEN`, `GITHUB_TOKEN` (Actions) presentes por ubicación | OK | Referenciados por nombre; sin exponer valores |
| Sin secretos en claro | gitleaks bloqueante en ambos gates | OK | Unificado a `@v3` por este intent |
| Sin recursos de entorno nuevos | el gate endurecido no requiere infra nueva | OK | pip-audit/npm audit/ruff/piso/expiry no piden credenciales ni servicios |
| Paridad de secretos PR↔push | ambos gates usan `GITHUB_TOKEN` (gitleaks) y `JWT_SECRET` efímero (pytest) | OK | La paridad de contenido añade pasos, no secretos |

## Seguridad del entorno (DevSecOps)

- **Implicación de seguridad del cambio** (guardrail Operation): el intent
  **añade** controles de supply-chain al gate pre-deploy (pip-audit, npm audit,
  allowlist con caducidad); **no retira ni elude** ningún control existente. Es
  un endurecimiento neto de la postura de seguridad del pipeline.
- **Sin cambios de IAM/red/cifrado**: no aplica risk assessment de
  infraestructura; Fly.io gestiona red/TLS, Neon TLS.
- **`JWT_SECRET` productivo no-default** exigido en arranque (NFR1.1): sin
  cambios; el CI usa uno efímero no-productivo.

## Compliance / auditoría

- Sin marco regulatorio formal aplicable (fantasy football, datos no sensibles
  regulados). La higiene relevante es no filtrar credenciales (gitleaks
  bloqueante) y la **allowlist versionada con caducidad** como registro auditable
  de excepciones de seguridad (NFR-SEC.3). Auditable en git, coste 0 €.

## Métricas de salud / error (guardrail Operation, Q5=A)

| Componente | Métrica de salud | Métrica de error | Herramienta (gratuita) |
|------------|------------------|------------------|------------------------|
| `futmondo-api` | `/health` HTTP 200 | no-200 / fallo del smoke test | `fly status`, `fly logs`, smoke test |
| `futmondo-app` | `/` disponible | error de nginx en `fly logs` | `fly logs` |
| Gate de CI (componente lógico) | pass por paso con nombre | tasa de rojos del job | log de GitHub Actions |

Sin métricas de pago (CloudWatch, etc.) — NO-APLICA. El intent no añade
componentes que requieran instrumentación nueva.

## Drift detection (NO-APLICA AWS → equivalente)

- **AWS Config drift detection**: NO-APLICA. Equivalente gratuito: el diff de
  git sobre `fly.toml` y los workflows versionados es la fuente de verdad; un
  cambio no versionado es visible como drift en el propio repo.

## Veredicto

**PASS.** El entorno de producción existente está operativo y no cambia; los
secretos requeridos están presentes por ubicación sin exponerse; el gate
endurecido no introduce recursos de entorno ni secretos nuevos y refuerza la
postura de seguridad sin retirar controles. Lo AWS-específico se marca NO-APLICA
con su equivalente gratuito documentado.

## Sources

- `./environment-inventory.md`.
- `../../construction/infrastructure-design/infrastructure-specification.md`, `../../construction/nfr-design/security-design.md`.
- `.github/workflows/ci.yml`, `.github/workflows/fly-deploy.yml`.
- `aidlc/spaces/default/knowledge/aidlc-shared/operation-fly-stack.md`.

## Assumptions & Open Questions

- La validación se apoya en el estado de producción operativo y en la config versionada; no se ejecuta aprovisionamiento real en esta etapa de diseño/documentación.
