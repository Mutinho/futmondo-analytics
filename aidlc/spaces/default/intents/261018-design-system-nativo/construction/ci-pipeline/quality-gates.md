# Quality Gates — Sistema de diseño nativo iOS

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

## Gates aplicables

| Gate | Dónde | Estado en este intent |
|------|-------|-----------------------|
| CI bloqueante del repo (gitleaks + ruff + pytest + pip-audit + ng test + npm audit) | `ci.yml` / `fly-deploy.yml` | Heredado, no modificado; aplica igual si el PR toca el repo |
| Build nativo iOS (`swift build`) | local / checkpoint | Verde (debe compilar) |
| Tests nativos (`swift test`) | local / checkpoint | Verde (43/0, sin regresión); invariante: no bajar/omitir |
| Cobertura line iOS (llvm-cov) | — | NO medible de forma fiable en WSL (aprendizaje durable); no es un gate numérico en este entorno |
| Validación de UI en dispositivo | iPhone 13 Pro (manual) | Pendiente de validación en dispositivo (claro/oscuro, Dynamic Type, no-regresión login) |

## Invariantes (durables)

- Un rojo del gate de CI del repo nunca llega a `main`.
- No bajar/relajar umbrales para pasar (el trinquete sólo sube); el flapping se arregla en el test no-determinista.
- Sin dependencias de pago ni `ruff format`/Prettier masivo sobre brownfield.

## Assumptions & Open Questions

None.
