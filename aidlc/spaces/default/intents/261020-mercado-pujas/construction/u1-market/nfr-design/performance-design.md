# Performance Design — u1-market

> Diseño de patrones de rendimiento de UI para `u1-market` (kind `ui`). Mapea los
> `NFR6.x` de responsividad a soluciones concretas. No hay caching de servidor ni
> pooling de conexiones (es un cliente); el foco es responsividad y trabajo
> fuera del hilo principal.

## Sources

- `.../construction/u1-market/nfr-requirements/performance-requirements.md` (NFR6.1–NFR6.6).
- `.../construction/u1-market/functional-design/functional-spec.md` (W1–W7).
- `nfr-design-questions.md` (Q1).

## Patrones de diseño

| NFR | Patrón de diseño | Detalle |
|---|---|---|
| NFR6.1 | Estado explícito inmediato | `MarketViewModel` setea `loadState = loading` de forma síncrona antes del `await`, de modo que la vista nunca aparece en blanco. |
| NFR6.2 | Reemplazo atómico de datos | Al resolver `loadToday()`, se asigna la lista y el `userInfo` en una sola actualización de estado observable (`@MainActor`); una recarga reemplaza, no mergea. |
| NFR6.3 | Render perezoso | `LazyVStack` dentro del `ScrollView`; sólo se materializan las cards visibles. Imágenes con `AsyncImage` + placeholder (no bloquean el layout). |
| NFR6.4 | Ordenado en memoria | `MarketSorter` (puro, `FutmondoKit`) ordena la colección ya cargada; el cambio de criterio no dispara red ni recarga. |
| NFR6.5 | Trabajo off-main | La I/O de red y la decodificación corren en los actores `MarketService`/`SofascoreService`; sólo la publicación del estado toca `@MainActor`. `isWriting` deshabilita botones de escritura sin congelar scroll/navegación. |
| NFR6.6 | Carga aislada del detalle | El sheet de detalle carga en su propio estado local; no comparte el ciclo de carga de la lista, así que su latencia no afecta la responsividad de la pantalla. |

## Presupuesto de responsividad

- Formateo de moneda (es-ES) y cálculo de `balanceMinusBids`: en memoria, O(1)
  por fila; sin trabajo pesado en el render.
- Ordenado: O(n log n) sobre la lista en memoria; n = jugadores del mercado
  (decenas), coste despreciable.
- Sin temporizadores de auto-refresh (evita trabajo y repintados innecesarios).

## Fuera de alcance (justificado)

Caching de servidor, CDN, pooling de conexiones, paginación de API, async
batch processing: son patrones de `service`, no de un cliente `ui`; el backend es
inalterado.

## Assumptions & Open Questions

None.
