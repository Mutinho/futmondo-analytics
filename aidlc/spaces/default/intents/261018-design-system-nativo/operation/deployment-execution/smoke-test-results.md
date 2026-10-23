# Smoke Test Results — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés.

## Smoke del "release" (build iOS)

| Check | Resultado |
|-------|-----------|
| `swift build` compila | OK |
| `swift test` (suite completa) | 43/0, sin regresión |
| El login revestido compila y el catálogo está presente | OK (ficheros en `ios/Sources/FutmondoApp/DesignSystem/`) |

## Smoke en dispositivo (manual, pendiente del propietario)

Al instalar con `xtool` en el iPhone 13 Pro, el smoke manual es:
- Abrir el catálogo: tokens y componentes visibles; alternar claro/oscuro y tamaño de texto.
- Login revestido: login → (auto-login) → logout sin regresión; aspecto coherente con el sistema.

## Producción

El smoke de producción heredado (`/health`, 5 reintentos) pertenece a `fly-deploy.yml` y NO se ejecuta por este intent (no se despliega a Fly.io).

## Assumptions & Open Questions

None.
