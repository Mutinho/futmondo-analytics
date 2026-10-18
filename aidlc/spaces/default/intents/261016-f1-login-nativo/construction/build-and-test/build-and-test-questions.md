# Build and Test — Preguntas (F1: Login nativo end-to-end)

> Idioma: castellano; identificadores/código en inglés.

## Consolidated Summary Confirmation

Antes de cerrar build-and-test (y la fase de construcción de F1), confirma:

- **F1 construido y verificado**: backend (`pytest` **422 passed / 3 xfailed**, cobertura 58,3%),
  iOS lógica (`swift test` **29 passed**); total **451 tests verdes**. `ruff` limpio; el gate de CI
  del repo sigue aplicando.
- **Los 3 bolts** completos, verificados por el engine y aprobados: backend (transporte aditivo
  D-01), cliente de red Swift, auth nativa (Keychain + AuthService actor + vistas).
- **Validación manual en el iPhone 13 Pro — COMPLETADA**: login → "Sesión iniciada" → cerrar y
  reabrir = auto-login directo (refresh token del Keychain) → logout. NFR-3 cubierto end-to-end.
  (Se corrigieron 4 fixes que solo afloran con el SDK de Apple: producto xtool, Sendable iOS, URL,
  navegación del splash; backend desplegado a Fly.io con D-01.)
- **Sin regresión** de la PWA; coste 0 €; higiene de `.gitignore` (venv efímeros, `ios/.build`).

¿Está todo correcto?

[Answer]: Looks correct
