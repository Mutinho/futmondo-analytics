# Refined Mockups — F3 Mercado (app nativa iOS)

> Mockups refinados sobre los wireframes de Ideación, concretando el mapeo al
> `DesignSystem` oscuro/neón de F1/F2 y el comportamiento de cada estado. Fuente
> de verdad del contenido: la vista Angular de Mercado.

## Sources

- `.../ideation/rough-mockups/wireframes.md` y `user-flow.md`.
- `.../inception/user-stories/stories.md` (US1–US7) y
  `.../requirements-analysis/requirements.md` (FR1–FR8).
- `.../inception/practices-discovery/team-practices.md` (tema Angular / HIG).

## M1 — Pantalla de Mercado (pestaña 2)

- **Contenedor**: `AuthenticatedBackground` (imagen `background.jpg` vía
  `Bundle.module`) como en F2, con `ScrollView` vertical.
- **Page header**: título "Mercado" + subtítulo, estilo `DSFont` del header de F2.
- **Banner** (`NeonGlassCard` horizontal o fila de tiles): 5 métricas (Presupuesto,
  En pujas, Balance, Puja máxima, Disponible) con `DSFont` de etiqueta + valor;
  Balance y Disponible usan `DSColor.moneyPositive` / `moneyNegative` según umbral
  (FR3 / US2).
- **Barra de control**: contador "N jugadores disponibles" + `GlassIconButton` /
  menú de orden (7 campos, descendente). Al cargar, la lista arranca **ordenada
  descendente por `value`** (orden por defecto, FR5.1/US4) y el selector refleja
  "Valor" preseleccionado.
- **Lista**: `LazyVStack` de `NeonGlassCard` por jugador:
  - Header: avatar (AsyncImage con placeholder), nombre, equipo + logo, badges
    Sofascore y % titular, chip(s) de posición.
  - Grid de métricas (2 filas): VALOR, TENDENCIA (↗/↘ + signo, color por signo),
    PRECIO MERCADO, SUGERIDA (acento neón), PUNTOS (+ nº partidos), MEDIA.
  - Acción: si **sin puja** → botón primario "PUJAR {suggested_bid}"; si **con
    puja activa** → fila "Puja activa: {current_bid}" + `GlassIconButton` cancelar.
  - Favorito: borde/acento distinto si `is_favorite`.
- **Estados**: reutiliza los componentes de estado de F2 (LoadingState,
  ErrorState con reintento, EmptyState con mensaje).

## M2 — Sheet de puja

- Presentación `.sheet` con `NeonGlassCard`; título "Pujar por {Nombre}".
- Dos tiles de límite: "Valor de mercado (mín)" y "Disponible (máx)". El tope
  efectivo es **`available_for_bids`** ("Disponible"), divergencia **intencionada**
  (Q1=A) respecto a la vista Angular, que usa `max_bid`.
- Campo numérico (`TextInputField` de F2 adaptado a teclado numérico) con prefijo
  €, default = `suggested_bid`.
- Mensaje de validación inline (money-negative) para vacío/≤0 o fuera de rango
  [`market_price`, `available_for_bids`].
- Acciones: "Cancelar" (secundario) y "Pujar" (primario, deshabilitado si
  inválido o escritura en curso).
- **Resultado**: tras confirmar, aviso según el patrón de `interaction-spec.md`
  (éxito → aviso + recarga; rechazo de backend → aviso con `message`, sin recarga;
  error de red/5xx → aviso genérico, sin recarga).

## M3 — Confirmación de cancelación

- `.alert` o `.confirmationDialog` nativo: "¿Cancelar puja de {X} por {Nombre}?"
  con acción destructiva "Cancelar puja" y "No". Tras confirmar, aviso de
  resultado según `interaction-spec.md` (éxito → aviso + recarga; rechazo/error →
  aviso, sin recarga).

## M4 — Sheet de detalle Sofascore

- Presentación `.sheet`; rating hero grande con color por tramo; grid de stats.
- Estados: spinner "Cargando stats de Sofascore…", error con icono, datos.

## Assumptions & Open Questions

None.
