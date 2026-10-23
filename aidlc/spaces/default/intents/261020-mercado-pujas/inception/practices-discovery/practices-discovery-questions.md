# Practices Discovery — Resumen (F3 Mercado)

> Etapa en modo subagent (pipeline-deploy-agent). Descubrimiento de confirmación.

## Consolidated Summary Confirmation

Resumen de Practices Discovery para F3 = Mercado:

- **Descubrimiento de confirmación**: las prácticas vigentes en
  `org.md`/`team.md`/`project.md` aplican íntegramente a F3. **Ninguna regla
  nueva** a proponer a memoria.
- **Confirmadas** (ya afirmadas): trunk-based + squash-merge + Conventional
  Commits; walking skeleton OFF; testing posture test-after con matiz nativo iOS
  (lógica pura en `FutmondoKit` con XCTest; vistas SwiftUI validadas en
  dispositivo; cobertura llvm-cov no fiable en WSL); deployment Fly.io on-merge
  (F3 no despliega); coste 0 € (sólo SDK de Apple); idioma (inglés código /
  castellano usuario); tema Angular como fuente de verdad.
- **Seguridad reforzada (no cambiada)** por la novedad de F3 (escritura
  pujar/cancelar + endpoint Sofascore): Bearer, refresh token sólo en Keychain,
  errores de integración tipados sin material de credencial, JWT_SECRET
  no-default.
- **Artefactos**: team-practices.md, discovered-rules.md (todo [YA-AFIRMADA]),
  evidence.md, practices-discovery-timestamp.md.
- **Siguiente etapa**: Requirements Analysis.

¿Todo correcto?

- **Looks correct** — confirmo y avanzamos.
- **Request changes** — quiero ajustar algo.

[Answer]: Looks correct
