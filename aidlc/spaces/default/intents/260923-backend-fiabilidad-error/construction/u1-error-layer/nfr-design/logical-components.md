# Logical Components — U1 `u1-error-layer`

| Componente lógico | Límite | Failure domain | Blast radius |
|---|---|---|---|
| `integration_errors` (módulo de tipos) | Módulo estrecho bajo `backend/app/`; solo clases de excepción | Ninguno (sin estado, sin I/O, sin dependencias) | Nulo — importar el módulo no puede fallar en runtime salvo ImportError de arranque |

- **Aislamiento**: el módulo no depende de nada del proyecto (ni god-files, ni
  DB, ni red). Es una biblioteca de tipos hoja.
- **Recurso compartido**: lo importan los clientes (U2) y la ruta de sync; el
  acoplamiento es de compilación (importar tipos), no de runtime.
- **Patrón NFR aplicado**: la garantía de seguridad (no-filtración por
  construcción) vive en el constructor de cada tipo.

## Assumptions & Open Questions

None.
