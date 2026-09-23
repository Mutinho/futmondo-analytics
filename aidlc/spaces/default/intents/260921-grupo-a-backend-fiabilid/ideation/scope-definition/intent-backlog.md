# Backlog del intent — Fiabilidad de la sync de 11 pasos

> Conversation language: Spanish. Ítems de trabajo derivados del documento de
> alcance. Prioridad por valor/coste; todo backend, coste 0 €.

## Ítems

| ID | Ítem | Req | Prioridad | Esfuerzo | Notas |
|----|------|-----|-----------|----------|-------|
| B1 | Helper estrecho `record_degraded_step(task, step, reason)` (log estructurado + estado de paso "degradado" en la tarea) | FR3.1 | Alta | S | Vive fuera del god-file; contrato tipado del estado (R-02) |
| B2 | Cablear `prizes` y `phantoms` al helper B1 para que reporten "degradado" en vez de éxito | FR3.1 | Alta | S | Confirmar locus real del bucle (R-01) |
| B3 | Acotar `except Exception`/bare-except de arranque/migraciones (recuperable vs fatal) | FR3.2 | Media | M | `db_connection.py`, `token_store.py` y equivalentes |
| B4 | Acotar los `except` del camino de sync tocado por B1/B2 | FR3.2 | Media | S | Sin purga masiva |
| B5 | Techo de sanidad del `price` en `place_bid` + validación | FR6 | Media | S | Criterio de límite estable (R-03) |
| B6 | Specs `pytest` significativas para B1–B5 (estado de tarea, log, recuperable/fatal, rechazo por techo) | — | Alta | M | Aserciones reales; nunca `assert True` |

## Orden sugerido

1. B1 (helper + contrato tipado) — base de todo lo demás.
2. B2 (cablear prizes/phantoms) + sus specs.
3. B5 (techo de price) + su spec — independiente, cierra el remate de FR6.
4. B3 + B4 (acotar except) + specs.
5. B6 se desarrolla junto a cada ítem (test-after por capa), no al final en bloque.

## Sources

- Derivado de `scope-document.md` (esta etapa) y del `intent-statement.md`.

## Assumptions & Open Questions

- None.
