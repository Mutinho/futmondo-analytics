# Preguntas de captura de intención — Fiabilidad de la sync

> Conversation language: Spanish. Las tres preguntas de encuadre se resolvieron
> en conversación con el usuario (recomendaciones punto a punto + Opción C). Se
> registran aquí como fuente de verdad con su respuesta confirmada.

## Q1 — Alcance de FR3.1 (visibilizar pasos degradados)

¿Hasta dónde llega la visibilización de pasos "non-critical" degradados?

- A. Solo `prizes` y `phantoms`, mediante un helper estrecho reutilizable.
- B. Todos los pasos "non-critical" de la sync de 11 pasos.
- X. Other (please specify)

[Answer]: A

Razón: ceñirlo a los dos pasos que el plan señala mantiene el diff quirúrgico y
respeta la prohibición de ampliar el god-file; el helper deja la puerta abierta a
extenderlo después.

## Q2 — Alcance de FR3.2 (acotar `except` amplios)

¿Qué superficie de `except Exception`/bare-except se aborda?

- A. Solo arranque/migraciones + los `except` del camino de sync tocado por FR3.1.
- B. Purga completa de los ~159 `except` del backend.
- X. Other (please specify)

[Answer]: A

Razón: alcance conservador y de alto retorno; la purga masiva es un refactor
grande, riesgoso y fuera del apetito de este intent.

## Q3 — Alcance de FR6 y frontend

¿Cómo se trata FR6, sabiendo que la validación de positividad ya está en `main`?

- A. Añadir solo el techo de sanidad del `price` + su test; rango dinámico fuera; sin tocar frontend.
- B. Implementar también el rango dinámico min/max del mercado.
- C. Sacar FR6 por completo de este intent.
- X. Other (please specify)

[Answer]: A

Razón: la positividad ya está cerrada (hardening previo); el techo es un remate
trivial que no conviene perder. El rango dinámico acopla al estado del campeonato
(coste). El frontend queda fuera: el hueco es de backend.

## Assumption Confirmation

- A. Accept assumptions
- B. Convert to follow-up questions

[Answer]: A

## Consolidated Summary Confirmation

Resumen consolidado del reencuadre (Opción C), confirmado por el usuario:

- **FR3.1** — Visibilizar los pasos degradados `prizes` y `phantoms` (log estructurado + estado de paso "degradado" en la tarea) tras un helper estrecho reutilizable. No se amplía el god-file.
- **FR3.2** — Acotar los `except Exception`/bare-except silenciosos, empezando por arranque/migraciones y el camino de sync tocado por FR3.1; distinguir recuperable de fatal. Sin purga masiva.
- **FR6 (remate)** — Añadir solo el techo de sanidad del `price` de puja + su test; la positividad (rechazo `price <= 0` con 422) ya está en `main`. Rango dinámico y frontend fuera.

Restricciones: backend-only, coste 0 €, no ampliar god-files, specs `pytest` significativas, gate de CI verde antes de merge.

[Answer]: Looks correct
