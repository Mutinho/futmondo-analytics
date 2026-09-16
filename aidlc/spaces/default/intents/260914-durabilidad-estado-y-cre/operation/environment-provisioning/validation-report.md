# Environment Validation Report — Durabilidad del estado

> Etapa Environment Provisioning (Operation). Validación del entorno de producción de
> futmondo-analytics respecto al delta que introduce la durabilidad. Perspectiva de plataforma
> (Fly.io/Neon), seguridad (DevSecOps) y cumplimiento (GRC), adaptada a coste 0 €.

## Veredicto: LISTO CON UNA ACCIÓN PREVIA AL DEPLOY

El entorno de producción es adecuado y no requiere aprovisionamiento nuevo, con **una acción
obligatoria antes del primer deploy que incluya la durabilidad de sesión**: fijar el secret
`FUTMONDO_CRED_KEY` en la app `futmondo-api` de Fly.io.

## Validaciones

### Plataforma (Fly.io / Neon)
| Ítem | Resultado | Detalle |
|------|-----------|---------|
| Apps Fly.io existentes | PASS | `futmondo-api` + `futmondo-app` ya en producción |
| Healthchecks | PASS | `/health` (backend) y `/` (frontend) configurados; smoke test del pipeline los verifica |
| Recursos / coste | PASS | `min=max=1`, `shared-cpu-1x`/256 MB; Neon free; coste 0 € — sin cambios |
| Esquema durable | PASS | `sync_session`/`sync_task` idempotentes en el arranque; no requiere provisión de BD manual |
| Compatibilidad de memoria | PASS (observación) | 256 MB por máquina; la durabilidad añade 1 lectura/escritura ligera por camino de sesión/tarea, sin estructuras en memoria significativas. Vigilar tras el deploy; `fly scale memory 512` disponible si hiciera falta (sigue en free allowance) |

### Seguridad (DevSecOps)
| Ítem | Resultado | Detalle |
|------|-----------|---------|
| Secret nuevo `FUTMONDO_CRED_KEY` | ACCIÓN REQUERIDA | Debe fijarse como secret de Fly.io antes del deploy. Generación: `Fernet.generate_key()`. Documentado en `docs/DEPLOY.md`. Si falta, el backend arranca pero la rehidratación de sesión degrada a **401 accionable** (no 403 opaco) — degradación segura, no caída |
| Gestión de secretos | PASS | Todos los secretos via `fly secrets` / GitHub Actions; ningún literal productivo en repo/workflow |
| Password en reposo | PASS | Cifrado Fernet en reposo (FR5.1/NFR1); nunca en claro. Rotar `FUTMONDO_CRED_KEY` invalida handles cifrados y fuerza re-login (documentado) |
| Guard de arranque JWT | PASS | `JWT_SECRET` no-default exigido en el arranque (NFR1.1), endurecido en `test_jwt_startup.py` |
| Escaneo de secretos | PASS | gitleaks BLOQUEANTE en el gate de MR y replicado en `verify` de push→main |

### Cumplimiento (GRC)
| Ítem | Resultado | Detalle |
|------|-----------|---------|
| PII / datos regulados nuevos | PASS | No se introduce PII regulada nueva. El dato sensible (credencial Futmondo) pasa de claro-en-memoria a cifrado-en-reposo: el cambio REDUCE la exposición |
| Residencia de datos | PASS | Neon (Frankfurt) + Fly.io (`cdg`), ambos UE; sin transferencia a regiones no aprobadas |
| Auditoría | PASS (sin cambio) | Sin requisito regulatorio formal aplicable a este proyecto personal; no se añaden ni retiran controles de auditoría |
| Coste recurrente | PASS | 0 € — sin servicios de pago nuevos (regla dura del proyecto) |

## Acción previa al deploy (obligatoria)

```bash
# En la app futmondo-api de Fly.io, antes del primer deploy con durabilidad de sesión:
fly secrets set \
  FUTMONDO_CRED_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')" \
  --app futmondo-api
```

- Guardar la clave SOLO como secret de Fly.io — nunca en el repositorio ni en el workflow.
- Rotarla invalida los handles cifrados existentes y obliga a un nuevo login por usuario.

## Riesgos y notas

- **Degradación segura si falta el secret**: sin `FUTMONDO_CRED_KEY`, el arranque no falla; solo se
  pierde la rehidratación transparente (401 accionable en el primer uso tras reinicio). Recomendado
  fijarlo antes del deploy para obtener el beneficio completo de FR1.2.
- **Memoria**: vigilar el uso tras el deploy (256 MB); margen para `fly scale memory 512` dentro del
  free allowance si fuese necesario. No esperado dado el diseño ligero.
- **Rollback**: sin cambios; runbook en `docs/ROLLBACK.md` (redeploy de release anterior). El esquema
  durable es aditivo e idempotente, no requiere rollback de BD.
