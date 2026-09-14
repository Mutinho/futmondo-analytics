# Frontend Components — Mejoras de CI/Tooling

> Etapa Functional Design (Construction) · Intent `260914-ci-tooling-mejoras`.
> Artefacto opcional (aplica a unidades con UI). Se incluye para dejar constancia explícita del alcance de UI.

## Alcance de UI en este intent

Este intent **no modifica ningún componente de UI, jerarquía de componentes, props/estado, flujos de interacción ni validación de formularios**. Son mejoras de CI/tooling, dependencias y configuración de entorno.

La única mejora rozando el frontend visible es la **mejora 3 (animaciones)**, y su diseño (ver `functional-spec.md`, flujo 3) concluye que:

- No hay animaciones propias de la API antigua de `@angular/animations` que migrar (0 imports/triggers verificados).
- `provideAnimationsAsync()` y `@angular/animations` se **conservan** porque los requiere Angular Material.
- Por tanto **no hay cambios en componentes ni en su comportamiento visual**: las animaciones de Angular Material (ripples, menús, tooltips, overlays, expansion panels) siguen funcionando igual.

## Componentes afectados

Ninguno. No se crean, eliminan ni reestructuran componentes. Los ficheros modificados por el intent son de configuración/tooling (`ci.yml`, `fly-deploy.yml`, `package.json`, `angular.json`, `.nvmrc`), no componentes de UI.

## Verificación de no regresión visual

Cubierto por BR6.1 (`rules.md`): tras cada mejora la suite de tests del frontend permanece en verde. No se requiere verificación visual adicional porque ningún cambio altera plantillas, estilos ni lógica de componentes.
