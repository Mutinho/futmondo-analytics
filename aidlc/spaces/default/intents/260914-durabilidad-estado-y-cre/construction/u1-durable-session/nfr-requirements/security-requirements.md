# Security Requirements — u1-durable-session

> NFR Requirements (Construction), perspectiva devsecops. Derivados de NFR1 y la regla dura de
> `project.md`. Cada requisito es verificable.

## Sources

- requirements.md (NFR1; FR5.1/FR5.2) [scope]
- project.md (NEVER contraseña en claro ni en memoria ni en BD; NEVER JWT_SECRET default) [scope]
- contract-summary.md (C1: nunca plaintext, resolve→None→401) [scope]
- functional-design/rules.md (BR1.4) [scope]
- nfr-requirements-questions.md (Q2-A) [Q2]

## Modelo de amenaza (STRIDE, superficies del intent)

- **Information Disclosure**: exposición de la contraseña Futmondo (en BD, logs o valores de
  retorno) — superficie principal; mitigada por NFR1.1/NFR1.2.
- **Spoofing/Elevation**: arranque con `JWT_SECRET` por defecto permitiría forjar tokens —
  mitigado por NFR1.3 (guard existente).
- **Tampering/Repudiation**: fuera del alcance nuevo (la firma JWT y el hashing de refresh
  tokens ya existen y no cambian).

## Requisitos de seguridad

| ID | Requisito | Verificación | Fuente |
|----|-----------|--------------|--------|
| NFR1.1 | La contraseña Futmondo NUNCA se almacena ni registra en claro (BD, logs, retornos). | Test (no aparece en filas/logs) + gitleaks; revisión de `CredentialProtection` | FR5.1, project.md, BR1.4 |
| NFR1.2 | El material de credencial solo es accesible tras `CredentialProtection`. Si el diseño cifra en reposo, la clave se gestiona como **secret de Fly.io**, nunca literal en el repo. | Revisión de frontera + escaneo de secretos; ausencia de literales | FR5.2, C1 |
| NFR1.3 | El arranque del servicio exige un `JWT_SECRET` no-default. | Test existente `test_jwt_startup.py` (ya endurecido) | NFR1, project.md |
| NFR1.4 | Ningún secreto nuevo se introduce en el repo; gitleaks es **bloqueante** en CI. | Job gitleaks del gate de MR (bloqueante) | project.md, team.md |

## Notas de cumplimiento (perspectiva compliance)

- No se introduce un framework regulatorio nuevo ni PII nueva más allá de la credencial ya
  existente; la clasificación de la credencial es **restricted** y su tratamiento queda acotado
  a `CredentialProtection`. No hay obligaciones GDPR/PCI nuevas derivadas de este intent.
- El único dato sensible es el medio de re-autenticación; su retención sigue el TTL de sesión
  (12h) o el modelo de re-auth elegido en FR5.2.
