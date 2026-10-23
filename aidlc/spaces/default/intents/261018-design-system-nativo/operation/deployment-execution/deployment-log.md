# Deployment Log — Sistema de diseño nativo iOS

> Fase: operación. Idioma: castellano; tokens técnicos verbatim en inglés. Adaptado al stack real.

## Qué se "despliega"

La capa de diseño (librería `DesignSystem` + login revestido) va **embebida en la app iOS**; no hay despliegue a servidor. El "deployment" de este intent es la build iOS verificada, lista para instalar en el iPhone 13 Pro con `xtool`.

## Registro

| Paso | Comando | Resultado |
|------|---------|-----------|
| Build | `cd ios && swift build` | Build complete! |
| Tests | `cd ios && swift test` | 43/0, sin regresión |
| Instalación en dispositivo | `cd ios && xtool dev build` | Manual, por el propietario (firma gratuita ~7 días) — paso no automatizado |

## Producción Fly.io/Neon

No se despliega nada: el backend/frontend producción no cambian por este intent (deployment-strategy §NO-APLICA). El pipeline `fly-deploy.yml` no se dispara por esta capa de diseño.

## Assumptions & Open Questions

- [assumption] La instalación en dispositivo con `xtool` la ejecuta el propietario cuando quiera validar visualmente; no es un paso automatizable en WSL sin el dispositivo conectado.
