# Rollback Runbook — refactor `data_manager_v2`

Reusa el runbook de producción existente `docs/ROLLBACK.md` (fuente de verdad del
mecanismo Fly.io) y añade el matiz de **rollback quirúrgico por responsabilidad**
que este refactor habilita.

## Cuándo hacer rollback

- El smoke test post-deploy contra `/health` falla (workflow en rojo).
- Un error funcional o de disponibilidad en producción tras el merge, pese a la
  equivalencia esperada (p. ej. una ruta no cubierta por la caracterización).

## Mecanismo (igual que producción — `docs/ROLLBACK.md`)

1. Identificar la release estable previa:
   ```bash
   fly releases --app futmondo-api
   fly releases --app futmondo-app
   ```
2. Revertir a la imagen previa:
   ```bash
   fly releases rollback <vN> --app futmondo-api
   # (repetir para futmondo-app si procede)
   ```
   Alternativa: `fly deploy --app futmondo-api --image <imagen previa>`.
3. Verificar salud:
   ```bash
   curl -sS https://futmondo-api.fly.dev/health   # espera 200 + {"status":"healthy"}
   ```

## Rollback quirúrgico por responsabilidad (específico de este refactor)

Cada uno de los 14 módulos se extrajo en un **commit aislado** (squash por MR,
C3). Si una regresión se localiza en un módulo concreto (p. ej. `players` o
`transactions`), se puede **revertir sólo ese commit de extracción** y volver a
desplegar, en vez de revertir todo el refactor:

```bash
git revert <sha-del-commit-del-modulo>   # revierte sólo esa extracción
# abrir PR con el revert; el gate de CI debe pasar antes de fusionar
```

Como la fachada preserva la superficie byte a byte, revertir un módulo restaura
su cuerpo original en `data_manager_v2.py` sin afectar a los demás módulos ya
extraídos (los adapters se alcanzan vía `self.dm`, sin acoplamiento cruzado).

## Rollback de BD

**No aplica**: el refactor no cambia el esquema de Neon ni los datos
(equivalencia estricta). No hay migración que revertir.

## Limitaciones conocidas (heredadas)

- El estado en memoria (`TaskManager`, syncs en curso) se pierde en cada
  redeploy/rollback — limitación aceptada del modelo de entorno único. Relanzar
  los syncs tras el rollback.
- Sin staging: la verificación de release es el smoke test `/health`.

## Post-rollback

- Abrir PR con el fix real (nunca push directo a `main`); el gate de CI debe
  pasar antes de fusionar.
- Registrar el incidente y la causa raíz. Si la regresión fue de equivalencia,
  añadir el caso al characterization test del módulo afectado antes de reintentar
  la extracción.
