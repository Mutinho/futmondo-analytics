# Security Requirements — Intent 4 (gate CI/CD hardening)

Este es el eje central del intent desde la perspectiva de seguridad: el
endurecimiento del gate es, en esencia, **seguridad de supply-chain y de la
cadena de release** a coste 0 €. Perspectivas superpuestas: DevSecOps
(supply-chain, escaneo), Compliance (trazabilidad/auditoría del gate), Quality
(que la señal de seguridad sea real y no cosmética).

## Modelo de amenaza (acotado al gate)

El activo protegido es `main` y, por extensión, el release a producción. Los
vectores que este intent cierra o endurece:

1. **Dependencia vulnerable con fix disponible que llega a producción** — hoy
   `pip-audit`/`npm audit` son advisory (`continue-on-error`), así que un CVE
   explotable con parche disponible no bloquea.
2. **Gate no reproducible / evadible** — `pip-audit -r` audita rangos (findings
   intermitentes); tooling flotante (`pip install ruff` sin pin, `vitest`
   `^4.0.8`) puede cambiar el veredicto entre ejecuciones; gitleaks corre en dos
   versiones distintas (`@v3` vs `@v2`) hacia `main`.
3. **Secreto filtrado en el repo o en los tests** — cubierto por gitleaks
   bloqueante (ya operativo), que este intent unifica y fija.
4. **Push directo a `main` que elude el gate** — el job `verify` hoy no corre
   audits ni lint; un push directo se los salta (FR14).

## Requisitos

Esquema de IDs: cada requisito detallado hereda del NFR de inception del que
deriva y añade un sub-número. La seguridad de secretos deriva de **NFR4**
(secretos vía `secrets`/JWT efímero); la seguridad de supply-chain (audits,
pins, escáneres) no tiene un NFR de inception propio de seguridad, así que se
ancla en el requisito funcional que la origina (FR12/FR13/FR14) y se numera bajo
un slot de seguridad dedicado **NFR-SEC** para evitar colisión con los slots
NFR1–NFR6 de inception.

| ID | Requisito | Criterio pass-fail | Origen (inception) |
|----|-----------|--------------------|--------------------|
| NFR-SEC.1 | `pip-audit` bloqueante sobre el entorno instalado | El gate falla ante todo finding CON fix disponible; se ejecuta sobre el venv resuelto tras `pip install` (sin `-r`), no sobre los rangos de `requirements.txt`. | FR12.3, FR12.4 |
| NFR-SEC.2 | `npm audit` bloqueante en severidad `high` | El gate falla ante findings de severidad `high` o superior (no critical-only). Trinquete de severidad solo endurece (critical→high). | FR12.2 |
| NFR-SEC.3 | Allowlist versionada y auditada para findings sin fix | Todo finding sin fix upstream se registra en fichero versionado y commiteado (ID CVE/advisory, dependencia+versión, motivo, fecha, fecha de caducidad), vía `pip-audit --ignore-vuln <ID>` y equivalente npm. Una entrada caducada vuelve a bloquear. Nunca `continue-on-error` permanente ni borrar el audit. | FR12.5 |
| NFR-SEC.4 | gitleaks unificado y fijado en ambos gates | `ci.yml` y el job `verify` corren la misma versión de gitleaks, fijada; secretos escaneados también en los tests. | FR13.1 |
| NFR-SEC.5 | Tooling del gate a versión exacta | `ruff`, `pip-audit` (fijados en el paso que los instala) y `vitest` (emparejado con `@vitest/coverage-v8==4.1.11`) a versión exacta; sin rangos abiertos en un check bloqueante. | FR13.2, FR13.3 |
| NFR4.1 | Secretos nunca en claro en workflows ni specs | Secretos vía `secrets` de GitHub Actions / Fly.io; en CI el `JWT_SECRET` es efímero y no productivo; los tests usan fakes/dobles, nunca credenciales reales. | NFR4 |
| NFR-SEC.6 | Paridad de defensa en profundidad PR ↔ push | Los audits y el lint que se vuelvan bloqueantes se añaden también al job `verify`, de modo que un push directo a `main` no eluda el gate de seguridad. | FR14.2 |

## Fuera de alcance (deuda de seguridad documentada)

- **SAST/DAST dedicado** (CodeQL/Semgrep/ZAP): fuera de alcance. CodeQL añadiría
  minutos de Actions y ruido de findings sobre los god-files heredados; DAST
  exige un entorno corriendo. `ruff`/`pip-audit`/`npm audit`/gitleaks cubren el
  mínimo viable de seguridad de pipeline a coste 0 €. Deuda documentada.
- **Pin de acciones de terceros por SHA** (`setup-flyctl@master`, etc.): se
  decide en ci-pipeline (FR13.4).

## Compliance / auditoría (perspectiva compliance)

- El proyecto no está bajo un marco regulatorio formal (fantasy football, datos
  no sensibles regulados); no aplican GDPR-artículo-específico, HIPAA, PCI, etc.
  más allá de la higiene de no filtrar credenciales.
- El requisito de auditoría relevante es interno: la **allowlist versionada con
  caducidad** (NFR2.3) da trazabilidad auditable de qué vulnerabilidad se aceptó,
  por qué y hasta cuándo — auditable en git sin coste.

## Sources

- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/requirements-analysis/requirements.md` (FR12, FR13, FR14, NFR4).
- `aidlc/spaces/default/intents/260925-ci-gate-hardening/inception/practices-discovery/team-practices.md` (decisiones Q2/Q3/Q5, evidencia del repo).
- `aidlc/spaces/default/codekb/futmondo-analytics/technology-stack.md` (rangos abiertos en requirements.txt, pins existentes).

## Assumptions & Open Questions

- None.
