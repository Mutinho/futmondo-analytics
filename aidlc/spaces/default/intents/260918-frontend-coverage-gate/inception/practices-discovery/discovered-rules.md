# Reglas descubiertas — intent `260918-frontend-coverage-gate`

> Solo restricciones DURAS afirmadas por el humano (entrevista Q7=A,B,C,D,E) o ya
> vigentes en la línea base. No es lugar para preferencias blandas (esas van a
> `team-practices.md`). Formato de una línea: `ALWAYS ...` bajo `## Mandated`,
> `NEVER ...` bajo `## Forbidden`. El promote tool estampa estas líneas en
> `project.md` en el gate.

## Mandated

Afirmadas en la entrevista de ESTE intent (Q7):

- ALWAYS verificar `npm ci` + `ng test` en contenedor `node:22.22.3` antes de pushear cambios de devDependencies del frontend. (Q7-B)
- ALWAYS fijar versión exacta (pin) del proveedor de cobertura `@vitest/coverage-v8` (OSS, coste 0 €); nada de rangos abiertos en un gate bloqueante. (Q7-D)

Arrastradas (ya afirmadas, siguen vigentes):

- ALWAYS mantener el proyecto a coste 0 €: descartar toda mejora o dependencia con gasto recurrente; solo soluciones sostenibles en tiers gratuitos (Neon free, Fly.io free allowance, GitHub Actions free).
- ALWAYS pasar el gate de CI bloqueante (gitleaks + `pytest` + `ng test`) antes de fusionar a `main`; un rojo nunca llega a producción.
- ALWAYS exigir un `JWT_SECRET` no-default en el arranque del servicio web (NFR1.1; endurecido en `test_jwt_startup.py`).

## Forbidden

Afirmadas en la entrevista de ESTE intent (Q7):

- NEVER bajar/relajar un umbral de cobertura para pasar el gate; el ratcheting solo sube. (Q7-A)
- NEVER hardcodear secretos/tokens reales en specs; los tests de auth usan fakes/dobles (gitleaks escanea `*.spec.ts`). (Q7-C)
- NEVER reintroducir `skipTests: true` en los schematics donde se retire. (Q7-E)

Arrastradas (ya afirmadas, siguen vigentes):

- NEVER usar un `JWT_SECRET` por defecto en producción.
- NEVER almacenar la contraseña Futmondo en claro (ni en memoria ni en base de datos).
- NEVER ampliar los god-files existentes (`data_sync_service.py`, `data_manager_v2.py`) ni el patrón SQL-en-router.
- NEVER correr `ruff format` masivo sobre archivos brownfield ya modificados; formatear solo los archivos nuevos o de forma quirúrgica.
