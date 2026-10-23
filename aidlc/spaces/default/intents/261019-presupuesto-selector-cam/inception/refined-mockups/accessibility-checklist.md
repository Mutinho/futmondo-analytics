# Accessibility Checklist — F2: Presupuesto nativo + selector de campeonato

> Fase: inception (refined-mockups). Idioma: castellano; tokens técnicos verbatim en inglés.
> Ancla NFR5 (accesibilidad) y NFR4 (rendimiento percibido) a ítems verificables por pantalla (resuelve el finding advisory de user-stories sobre anclaje transversal).

## VoiceOver (NFR5)

- [ ] Cada fila de equipo es un único elemento con label compuesto: "Equipo <nombre>, saldo <valor> <positivo|negativo>, rendimiento <valor>, puja máxima <valor>, premios <valor|ninguno>".
- [ ] El título de la navigation bar anuncia "Campeonato activo: <nombre>, botón, abre selector".
- [ ] El botón de orden anuncia la clave activa.
- [ ] En carga: anuncia "Cargando presupuesto"; en error: foco movido a [Reintentar] y anunciado.
- [ ] Estado vacío: el mensaje es leído por VoiceOver.

## Dynamic Type (NFR5)

- [ ] Todos los textos usan `DSFont` (que respeta Dynamic Type); la fila no se trunca ni solapa en tamaños grandes (usa layout que crece en vertical).

## Color / contraste (NFR5)

- [ ] money-positive/negative acompañados de signo (color no es único portador).
- [ ] Contraste ≥ 4.5:1 texto normal / ≥ 3:1 texto grande (reutiliza `ContrastRatio` de F1).

## Rendimiento percibido (NFR4)

- [ ] Scroll de la lista fluido (objetivo 60 fps) con `List`/`LazyVStack` (render perezoso).
- [ ] Indicador de carga visible <100 ms al iniciar/cambiar de campeonato.

Verificación: ítems VoiceOver/Dynamic Type/rendimiento se validan **en dispositivo** (iPhone 13 Pro); contraste se cubre con `ContrastRatio` en `swift test`.

## Sources

- `aidlc/spaces/default/intents/261019-presupuesto-selector-cam/inception/requirements-analysis/requirements.md` (NFR4, NFR5)
- `ios/Sources/FutmondoKit/DesignSystem/ContrastRatio.swift`

## Assumptions & Open Questions

None.
