# Security Test Instructions — Construction (FR3.2 + FR4)

## Aplicabilidad

Estrategia **Standard**. El alcance de seguridad de este intent es acotado (ver
`nfr-design/security-design.md`): **Information Disclosure** (NFR3: sin
credenciales en excepciones/logs) + integridad de datos (NFR2) + gestión de
secretos. No se introduce auth/authz nueva ni superficie HTTP nueva.

## Controles de seguridad verificados

| Control | Verificación | Estado |
|---|---|---|
| NFR3 — sin credenciales en excepción/`repr`/`exc_info` | `tests/test_futmondo_client_typed_failures.py` asvera ausencia de password/token en `str`/`repr`/`args` de las excepciones tipadas | Cubierto |
| NFR3 — sin credenciales en log estructurado | el helper de log recibe sólo campos permitidos (`sync_step`, `failure_mode`, `status`, `endpoint`, `task_id`, `reason`) | Cubierto (diseño + test de tipo) |
| Secretos fuera del código/tests | `gitleaks` bloqueante en `ci.yml` (PR) y job `verify` (push); los tests usan fakes | Cubierto (pipeline existente) |
| NFR2 — no-corrupción (Tampering) | `tests/test_team_prizes_atomic_replacement.py` (reemplazo atómico) | Cubierto |

## Cómo ejecutar

```bash
cd backend && JWT_SECRET="<efímero>" python -m pytest tests/test_futmondo_client_typed_failures.py tests/test_team_prizes_atomic_replacement.py -q
```

`gitleaks` corre en el pipeline (CI), no localmente en este stage.

## NO-APLICA (coste 0 €)

- SAST/DAST gestionados de pago → **NO-APLICA**; el gate CI existente (gitleaks +
  pytest) es la garantía. Los `I` de `ruff check` en brownfield son advisory.
