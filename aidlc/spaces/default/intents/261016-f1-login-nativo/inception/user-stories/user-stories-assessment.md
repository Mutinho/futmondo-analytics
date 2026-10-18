# User Stories Assessment — F1: Login nativo end-to-end

> Fase: inception (user-stories). Evaluación de cobertura y confirmación. Idioma: castellano;
> tokens técnicos verbatim en inglés.

## Cobertura de requisitos

8 historias (US-1…US-8) cubren los 9 FR y los 4 NFR (ver `traceability.json`):
- Cada FR traza al menos a una historia; cada historia traza al menos a un FR (sin orphans).
- Los NFR transversales se cubren así: NFR-1 (US-2), NFR-2 (US-6), NFR-3 (US-7 + validación manual
  documentada), NFR-4 (idioma, transversal a todas las historias; no es una historia propia).

## Independencia y testabilidad

- Cada historia es independientemente verificable con criterios Given/When/Then.
- US-7 (ajuste backend) es la base técnica de US-1…US-5/US-8; aun así es testable por sí misma
  (tests `pytest` de ambos canales), no "sólo en secuencia".

## Corners cubiertos

- Fallo de red / 5xx en refresh (US-3): preserva Keychain, no se cuelga.
- Logout con red caída (US-5): limpia estado local, revocación pendiente.
- Reduce Motion (US-6): animaciones degradadas.

## Confirmación

La confirmación y el checkpoint de resumen de esta etapa se registran en
`user-stories-questions.md` (fuente de verdad del `[Answer]`).

## Sources

- [consumes] requirements.md, business-overview.md, component-inventory.md, team-practices.md.
- `stories.md`, `personas.md`, `traceability.json` de esta etapa.

## Assumptions & Open Questions

None.
