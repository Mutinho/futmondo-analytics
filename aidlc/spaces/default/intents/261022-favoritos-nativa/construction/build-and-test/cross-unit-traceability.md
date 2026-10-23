# Cross-Unit Final Coverage Gate — Favoritos nativa iOS

## Veredicto: PASS

Todos los `FR` (FR1–FR8) y `NFR` (NFR1–NFR7) de `requirements.md` están
cubiertos (status `OK`) vía la cadena functional-design (FR→BR) +
code-generation (BR→fichero), y los ficheros destino existen. No hay etapa
`user-stories`, así que no hay `AC` de tres segmentos que enumerar.

## Cobertura de requisitos funcionales (FR)
| ID | BR | Fichero(s) | Estado |
|---|---|---|---|
| FR1 (carga/frescura, reactiva a campeonato) | BR1.1, BR1.2 | FavoritesViewModel.swift, FavoritesView.swift | OK |
| FR2 (estado vacío) | BR2.1 | FavoritesView.swift | OK |
| FR3 (cards, contenido, nulos/cero, media) | BR3.1–BR3.4 | FavoritePlayerCard.swift, FavoritePlayer.swift, FavoritesView.swift | OK |
| FR4 (orden + persistencia) | BR4.1 | FavoritesSorter.swift, FavoritesPreferences.swift | OK |
| FR5 (quitar de favoritos) | BR5.1–BR5.4 | FavoritesView.swift, FavoritesViewModel.swift, ConfirmSheet.swift | OK |
| FR6 (Sofascore) | BR6.1 | FavoritePlayerCard.swift | OK |
| FR7 (sin cross-invalidación) | — | (decisión UI; N/A) | OK |
| FR8 (4.ª pestaña) | BR7.1 | RootTabView.swift | OK |

Contrato de backend inmutable (rutas exactas) BR8.1 → FavoritesService.swift.

## Cobertura de NFR
| ID | Evidencia | Estado |
|---|---|---|
| NFR1 (coste 0 €) | `Package.swift` `dependencies: []` | OK |
| NFR2 (idioma) | identificadores inglés / UI castellano | OK |
| NFR3 (testabilidad) | lógica en FutmondoKit con XCTest (232 verde) | OK |
| NFR4 (look&feel) | cards estilo Mercado + design system + skeleton aurora | OK |
| NFR5 (rendimiento) | caché DataFreshness; sin estado por frame; skeleton | OK |
| NFR6 (accesibilidad) | labels, no solo-color, Reduce Motion en animaciones/skeleton | OK |
| NFR7 (seguridad) | sin credenciales; NetworkClient autenticado; NetworkError no filtra | OK |

## Elementos sin cubrir
Ninguno.
