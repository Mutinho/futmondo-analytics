# Units Generation — Mapa de requisitos por unidad

## Sources

- `unit-of-work.md` (U1) y `requirements.md` (FR3.1, FR3.2, FR6).

## Mapa U1 — sync-reliability

| Requisito | Cubierto en U1 |
|---|---|
| FR3.1 — estado `degraded` observable (prizes/phantoms) | Sí (helper + valor + cableado) |
| FR3.2 — `except` acotados recuperable/fatal | Sí (arranque/migraciones + camino de sync) |
| FR6 — techo de sanidad del `price` | Sí (`PRICE_SANITY_CAP` en place_bid) |
| NFR1 fiabilidad observable, NFR2 mantenibilidad, NFR3 testabilidad, NFR4 coste 0 €, NFR5 seguridad | Sí (transversales a U1) |

Toda la funcionalidad del intent recae en la única unidad U1.

## Assumptions & Open Questions

None.
