# Security Test Instructions — cobertura mínima (perspectiva DevSecOps)

Intent `260929-assistant-god-file`, scope `refactor`, **Test Strategy: Minimal**.

## Aplicabilidad

**No se genera un árbol de tests de seguridad nuevo** (SAST/DAST dedicados) en este intent
Minimal. El refactor no cambia la superficie de autenticación/autorización ni introduce entradas
nuevas de usuario: preserva la superficie pública observable. Aun así, la perspectiva de
seguridad impone dos verificaciones que YA cubren la suite y el gate, y que se registran aquí.

## Verificaciones de seguridad que aplican (ya cubiertas)

- **Sin credenciales en excepciones (BR5.4)**: el adaptador LLM (`llm_adapter.py`) solo loguea
  `str(e)[:80]` en la degradación Groq→Gemini; nunca `api_key`/`token`/`password`/`secret` en el
  mensaje, `repr` ni `exc_info`. Congelado por `backend/tests/test_assistant_llm.py`, que asevera
  la ausencia de material de credencial en la respuesta degradada. **Verdict: cubierto, verde.**
- **Escaneo de secretos (gate)**: `gitleaks` es bloqueante en CI (PR) y en el job `verify`
  (push→`main`); escanea también los tests nuevos, que usan valores fake evidentes, sin
  credenciales/tokens reales (regla afirmada). No es ejecutable en local en este stage sin el
  action; lo ejerce el gate de CI antes de fusionar a `main`.
- **SQL parametrizado (OWASP A03 — Injection)**: todo el SQL crudo vive en los adaptadores de
  infraestructura con `db.adapt_params(...)` + `?` (sin concatenación), preservando el patrón del
  proyecto. Sin SQL nuevo en dominio/aplicación.

## Fuera de alcance / diferido

- SAST/DAST dedicados del backend y del frontend más allá del gate actual: **deuda diferida**
  (documentada en el conocimiento de equipo del stack Fly.io). El endurecimiento del gate
  (`pip-audit`/`ruff` bloqueantes) es objeto de otros intents de CI, no de este refactor.
