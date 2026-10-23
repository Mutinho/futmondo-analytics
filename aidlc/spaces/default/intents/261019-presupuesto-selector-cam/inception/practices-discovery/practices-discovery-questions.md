# Practices Discovery — Questions (F2)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Practices Discovery:

- F2 **hereda íntegramente** el conjunto de reglas afirmado por los intents previos, **sin contradicciones**: trunk-based + squash-merge; coste 0 € y cero dependencias externas iOS (`dependencies: []`); gate de CI bloqueante replicado (gitleaks + `ruff check` + `pytest` + `pip-audit` + `ng test` + `npm audit`, ratchet solo sube); idioma EN (código) / ES (UI, commits); tema Angular Material 3 como fuente de verdad; estructura/testing iOS (`FutmondoKit` testeable con `swift test` + vistas SwiftUI en `FutmondoApp` bajo `#if canImport(SwiftUI)` validadas en dispositivo; color sets en código; llvm-cov no fiable en WSL); seguridad de credenciales (refresh token en Keychain, access token en memoria); deploy on-merge; test-after; no ampliar god-files / SQL-en-router.
- **Ninguna práctica nueva a afirmar**: el único candidato (estructura/testing iOS) ya está capturado como Correction aprendida (2026-10-19) en `project.md`.
- La promoción reafirma lo vigente, sin cambios conflictivos en `team.md`/`project.md`.

¿Does this all look correct?

[Answer]: Looks correct
