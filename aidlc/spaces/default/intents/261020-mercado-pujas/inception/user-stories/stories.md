# User Stories — F3 Mercado (app nativa iOS)

> Historias en formato Given/When/Then (BDD). Actor: el mánager (P1). Cada
> historia traza a sus FR de origen.

## Sources

- `.../inception/requirements-analysis/requirements.md` (FR1–FR8, NFR1–NFR6).
- `.../inception/user-stories/personas.md` (P1).
- `aidlc/spaces/default/codekb/futmondo-analytics/component-inventory.md`.

## US1 — Abrir el Mercado (FR1, FR2)
**Como** mánager, **quiero** una pestaña "Mercado" en la app, **para** ver los
jugadores del computer sin salir del cliente nativo.
- **Given** estoy autenticado y con un campeonato activo,
  **when** selecciono la pestaña "Mercado",
  **then** la app carga `GET /market/today` del campeonato activo y muestra el
  mercado.
- **Given** la carga falla por red, **when** ocurre el error, **then** veo un
  estado de error con opción de reintento, no una lista vacía.
- **Given** no hay jugadores en el mercado, **when** termina la carga, **then**
  veo el estado vacío con su mensaje.

## US2 — Ver mi situación económica (FR3)
**Como** mánager, **quiero** un banner con mi dinero, **para** saber cuánto puedo
pujar.
- **Given** el mercado ha cargado, **when** miro el banner, **then** veo
  Presupuesto, En pujas, Balance, Puja máxima y Disponible, formateados como
  moneda; **Balance** se colorea en verde (money-positive) si `≥ 0` y en rojo
  (money-negative) si `< 0`, y **Disponible** en verde si `> 0` y en rojo si
  `≤ 0`.

## US3 — Explorar jugadores en cards (FR4)
**Como** mánager, **quiero** cards con los datos de cada jugador, **para**
comparar candidatos.
- **Given** el mercado ha cargado, **when** veo una card, **then** muestra avatar,
  nombre, equipo, badges de Sofascore y % titular, posición(es) y el grid de
  métricas (valor, tendencia con flecha+signo, precio de mercado, sugerida,
  puntos, media).
- **Given** un jugador es favorito, **when** veo su card, **then** se distingue
  visualmente.

## US4 — Ordenar la lista (FR5)
**Como** mánager, **quiero** ordenar los jugadores, **para** priorizar según el
criterio que me interese.
- **Given** el mercado ha cargado, **when** elijo un campo de orden, **then** la
  lista se reordena **descendente** por ese campo sin recargar, con los nulos al
  final.
- **Given** el mercado acaba de cargar sin que yo haya tocado el selector,
  **when** veo la lista, **then** está ordenada **descendente por `value`** (orden
  por defecto).

## US5 — Pujar por un jugador (FR6)
**Como** mánager, **quiero** pujar por un jugador con un importe validado,
**para** fichar sin pasarme de mi disponible.
- **Given** una card sin puja activa, **when** pulso "PUJAR", **then** se abre un
  sheet con el importe por defecto = puja sugerida.
- **Given** el sheet de puja, **when** introduzco un importe vacío o ≤ 0, o fuera
  de [precio de mercado, disponible], **then** veo el error inline y el botón
  "Pujar" queda deshabilitado.
- **Given** un importe válido, **when** confirmo, **then** la app llama a
  `POST /market/bid` y, si el backend acepta (2xx `success=true`), veo un aviso de
  éxito y el mercado se recarga.
- **Given** el backend **rechaza** la puja (2xx `success=false` o 4xx como 422/400),
  **when** confirmo, **then** veo un aviso de rechazo con el `message`/`detail` y
  el mercado **no** se recarga.
- **Given** hay un **error de red o 5xx**, **when** confirmo, **then** veo un aviso
  de error genérico y el mercado **no** se recarga ni queda en estado ambiguo.
- **Given** una escritura en curso, **when** está en progreso, **then** los
  botones de puja/cancelar quedan deshabilitados.

## US6 — Cancelar mi puja (FR7)
**Como** mánager, **quiero** cancelar una puja activa, **para** recuperar ese
disponible.
- **Given** una card con puja activa, **when** pulso cancelar, **then** se me pide
  confirmación.
- **Given** confirmo la cancelación, **when** la app llama a
  `POST /market/cancelbid` y el backend acepta (2xx `success=true`), **then** veo
  un aviso de éxito y el mercado se recarga.
- **Given** el backend **rechaza** la cancelación (2xx `success=false` o 4xx),
  **when** confirmo, **then** veo un aviso de rechazo con su `message`, sin
  recarga.
- **Given** hay **error de red o 5xx**, **when** confirmo, **then** veo un aviso
  de error genérico, sin recarga.

## US7 — Consultar el detalle Sofascore (FR8, Should)
**Como** mánager, **quiero** ver las estadísticas Sofascore de un jugador,
**para** decidir mejor mi puja.
- **Given** una card con rating Sofascore, **when** toco el badge, **then** se
  abre un sheet que llama a `GET /sofascore/player/{name}` y muestra rating y
  estadísticas.
- **Given** el detalle falla o tarda, **when** ocurre, **then** el sheet muestra
  su estado de carga/error y la lista y la capacidad de pujar no se ven afectadas.

## Assumptions & Open Questions

None.
