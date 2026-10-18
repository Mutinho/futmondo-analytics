# Quality Gates — F1: Login nativo end-to-end

> Fase: construcción (ci-pipeline). Idioma: castellano; tokens técnicos verbatim en inglés.

## Gates bloqueantes a `main` (CI del repo, ya operativo)

| Gate | Herramienta | Alcance en F1 |
|------|-------------|----------------|
| Secretos | `gitleaks` | Todo el árbol, incl. `ios/` y tests (sin secretos reales). |
| Lint backend | `ruff check` | Ficheros de `backend/` tocados por D-01 (limpio). |
| Tests backend | `pytest` | Suite backend incl. los 8 tests nuevos de transporte (422 passed). |
| Deps backend | `pip-audit` | Entorno resuelto; sin findings con fix. |
| Tests frontend | `ng test` | PWA Angular (sin cambios en F1; sigue verde). |
| Deps frontend | `npm audit` | Sin regresión. |

Un rojo en cualquiera **bloquea** el merge/despliegue (regla durable). El ajuste de backend de F1
pasa todos.

## Verificación fuera del CI del repo (F1)

| Verificación | Dónde | Estado |
|--------------|-------|--------|
| `swift test` (lógica iOS) | WSL (Swift 6.4), ejecutado por el propietario | 29 passed — verde |
| Validación de dispositivo (`xtool`) | iPhone 13 Pro | login → auto-login → logout, completada |

El trinquete de cobertura backend heredado (`--cov-fail-under`) no se baja (regla durable); F1 no
lo modifica. El piso de cobertura iOS no existe aún (deuda P-1 del arnés de dispositivo).

## Sources

- [consumes] ci-config.md, build-and-test-summary.md, test-results.md.

## Assumptions & Open Questions

None.
