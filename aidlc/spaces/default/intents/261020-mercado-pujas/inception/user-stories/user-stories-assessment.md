# User Stories Assessment — F3 Mercado

## Sources

- `.../inception/user-stories/stories.md` (US1–US7).
- `.../inception/requirements-analysis/requirements.md` (FR1–FR8).

## Cobertura y calidad

| Historia | FR cubiertos | Independientemente testable | Notas |
|---|---|---|---|
| US1 | FR1, FR2 | Sí | Incluye estados error/vacío |
| US2 | FR3 | Sí | Banner de 5 campos |
| US3 | FR4 | Sí | Cards 1:1 + favorito |
| US4 | FR5 | Sí | Orden descendente, nulos al final |
| US5 | FR6 | Sí | Escritura con validación y 3 desenlaces |
| US6 | FR7 | Sí | Confirmación + recarga |
| US7 | FR8 | Sí | Should; fallo aislado del núcleo |

- **Cobertura de FR**: FR1–FR8 todos cubiertos por al menos una historia.
- **Priorización**: US1–US6 son Must (núcleo de lectura + escritura); US7 es
  Should (detalle Sofascore).
- **Independencia**: cada historia es verificable por sí misma; US5/US6 (escritura)
  dependen de que US1 haya cargado el mercado, pero su criterio de aceptación es
  autónomo.

## Riesgos de historia

- US5/US6 tienen **efecto real** en el campeonato: su verificación en dispositivo
  debe hacerse con cuidado (idealmente contra un jugador de prueba) para no
  comprometer pujas reales.

## Assumptions & Open Questions

None.
