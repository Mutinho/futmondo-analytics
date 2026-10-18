# Personas — F1: Login nativo end-to-end

> Fase: inception (user-stories). Idioma: castellano; tokens técnicos verbatim en inglés.

## P1 — Usuario de Futmondo en iPhone (persona principal)

- **Quién**: el propietario-ejecutor y, por extensión, cualquier usuario de Futmondo que use la
  app nativa en su iPhone 13 Pro.
- **Objetivo**: iniciar sesión con sus credenciales Futmondo y mantener la sesión sin fricción
  (que la app "recuerde" la sesión entre arranques).
- **Contexto**: uso personal, sin plazo; valora una experiencia nativa fluida.
- **Necesidades**: login rápido con autorrelleno; no tener que re-loguear cada vez; cierre de
  sesión fiable.
- **Frustraciones a evitar**: spinners colgados, re-login innecesario, mensajes de error poco
  claros.

## P2 — Mantenedor del backend / PWA (persona secundaria)

- **Quién**: el mismo propietario en su rol de mantenedor del backend FastAPI y la PWA Angular.
- **Objetivo**: que el cliente nativo reutilice el backend sin romper la PWA en producción.
- **Necesidades**: ajuste de backend aditivo, cubierto por `pytest`, que pase el gate de CI.
- **Frustraciones a evitar**: regresiones en el flujo de auth de la PWA; deuda de seguridad.

## Sources

- [consumes] requirements.md, business-overview.md, component-inventory.md, team-practices.md.
- stakeholder-map de F1 (ejecutor único).

## Assumptions & Open Questions

None.
