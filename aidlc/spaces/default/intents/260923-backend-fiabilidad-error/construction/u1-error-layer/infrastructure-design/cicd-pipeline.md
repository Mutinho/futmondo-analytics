# CI/CD Pipeline — U1 `u1-error-layer`

Sin infraestructura nueva. U1 es una biblioteca de tipos dentro de
`futmondo-api` (Fly.io, región `cdg`, ya definido). Este intent no cambia la
topología ni el orden de despliegue [memory:M1].

## Incidencia de U1 en el pipeline existente

- **Commit aislado `chore(ci)` (FR3.2.3)**: quitar `E722` del `ignore` de
  `backend/ruff.toml` para que `ruff check` reporte bare-except. `ruff check`
  sigue **advisory** (no bloqueante). Sin `--fix` ni `ruff format` (aísla el
  reflow, respeta la regla brownfield).
- **Gate CI existente**: la suite de U1 (`pytest` desde `backend/`) corre en el
  gate bloqueante `ci.yml` (PR→`main`) y en el job `verify` de `fly-deploy.yml`
  (push→`main`). No se cambia la cadena `needs:` ni el orden de despliegue.
- **Coste 0 €**: GitHub Actions free tier; sin recursos cloud nuevos.

## Recursos cloud

Ninguno nuevo. U1 no despliega nada por su cuenta.

## Assumptions & Open Questions

None.
