# Build Instructions — Optimización del bundle inicial

> Stage 3.6 Build and Test · Intent `260914-bundle-optimization` · scope `refactor` · Minimal · brownfield.
> Rol: quality engineer (con devsecops de apoyo). Sin cambio funcional, coste 0 €.

## Prerrequisitos

- Node 22.22.3 (fijado en `.nvmrc`; el Angular CLI 22 exige ≥22.22.3). Si el Node local no llega, usar el contenedor documentado abajo (regla de proyecto, coste 0 €).
- `angular-app/` con dependencias instaladas vía `npm ci`.

## Comando de build de producción

```bash
cd angular-app && npx ng build --configuration production
```

Contenedor (Node local < mínimo del CLI), volumen anónimo para `node_modules`:

```bash
docker run --rm -v "$PWD/angular-app":/app -v /app/node_modules -w /app node:22.22.3 \
  sh -c "npm ci && npx ng build --configuration production"
```

## Criterio de aceptación (NFR1 / FR4.3 / BR4.2)

- El build de producción debe completar **sin error** con el budget `type: initial` `maximumError: 1MB`, `maximumWarning: 900kB`.
- El chunk `initial` total debe quedar **por debajo de 1 MB** (1 048 576 bytes).

## Resultado verificado

- Build **completa sin error** con `maximumError: 1MB`.
- **Initial total: 819.05 kB** (raw) / 181.09 kB (transfer estimado) — por debajo de 1 MB. ✓
- Sin warnings de budget.
