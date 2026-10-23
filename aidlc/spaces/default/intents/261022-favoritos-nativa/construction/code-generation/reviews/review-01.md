## Review

**Verdict:** READY
**Reviewer:** aidlc-architecture-reviewer-agent
**Date:** 2026-10-22T15:01:00Z
**Iteration:** 1

### Findings

| ID | Severity | Location | Finding | Required action | Status |
|---|---|---|---|---|---|
| R-01 | Minor | ios/Sources/FutmondoApp/Favorites/FavoritePlayerCard.swift > métrica PUNTOS / MEDIA | En la web (vista cards) el recuento de partidos `(NJ)` aparece pegado a PUNTOS (`p.points > 0 ? p.points : '-'` seguido de `@if (p.matches > 0) { (NJ) }`); la card nativa no lo pone junto a PUNTOS y en su lugar lo baja a la línea secundaria de MEDIA (`N j`). Es la adaptación nativa documentada (BR3.2), no una pérdida de dato, pero sí una diferencia de ubicación respecto a la fuente Angular que conviene que el revisor humano confirme como deseada. | Ninguna acción obligatoria; confirmar en el gate que reubicar el recuento de partidos a la línea de MEDIA (en vez de junto a PUNTOS como la web) es el comportamiento deseado. | New |

### Validation Tool Results

| Tool | Result | Interpretation |
|---|---|---|
| swift build --package-path ios | PASS (Build complete, exit 0) | El paquete compila sin errores ni avisos nuevos en Favorites. |
| swift test --package-path ios | PASS (Executed 232 tests, 0 failures) | Confirma el recuento 232 verde reclamado en code-summary.md (204 previos + 28 nuevos). |
| grep "static var" (Favorites) | Sin coincidencias | No hay estado mutable `static var`; solo `static let` (seguro bajo Swift 6 device-strict). |

### Summary

La implementación es fiel al contrato: `unfollow` usa POST con `championship_id`+`player_id` como QUERY PARAMS y body vacío (idéntico a `favorites.service.ts`), aseverado por test con `lastHadBody()==false` y ruta exacta (regresión BR8.1); los dos ratings se decodifican con `rating` oculto y `sofascoreRating` como badge/orden; nulos y `0` renderizan `-` replicando la lógica condicional de la card Angular; la guardia `isWriting`, la recarga solo en `.accepted` y la lista intacta en fallo (BR5.2/5.3/5.4) son correctas; la recarga por cambio de campeonato observa `budgetViewModel.activeChampionship?.championshipId` (el fix conocido, no el getter de UserDefaults); la 4.ª pestaña `star` con tinte verde está en ambas ramas del `TabView`; los tests aseveran comportamiento real (sin assert-true); los targets de trazabilidad existen y no hay dependencias de pago. Un único hallazgo Minor no bloqueante sobre la ubicación del recuento de partidos. READY.
