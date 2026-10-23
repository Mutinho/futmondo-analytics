# Unit Test Instructions — Favoritos nativa iOS

## Framework y setup

- **Framework**: XCTest (SDK de Apple, coste 0 €), target `FutmondoKitTests`.
  Runner ya existente. Metodología **test-after**.

## Comando (unit-scoped)

```bash
swift test --package-path ios --filter "FavoritePlayerTests|FavoritesSorterTests|FavoritesPreferencesTests|FavoritesServiceTests"
```

Suite completa (verificar verde, sin bajar nada):

```bash
swift test --package-path ios 2>&1 | grep -E "Executed [0-9]+ tests"
```

Build: `swift build --package-path ios`.

## Qué se testea (test-after)

- **`FavoritePlayer`**: decode happy-path; nulos (`starter_pct`,
  `sofascore_rating`, `change` ausentes → nil); los **dos** ratings (`rating`
  decodificado, `sofascore_rating` el del badge); respuesta tolerante
  array/wrapped.
- **`FavoritesSorter`**: orden descendente por cada campo; nils al final;
  estable.
- **`FavoritesPreferences`**: round-trip del orden en `UserDefaults`
  (`KeyValueStore` inyectable).
- **`FavoritesService`** (si procede, con doble en memoria de `NetworkClient`):
  endpoints exactos — `unfollow` usa **query params** (championship_id +
  player_id) con **body vacío**, NO body JSON (regresión de BR8.1).

## Cobertura / mocking

- Happy path + ≥2 casos de borde por componente; ~10-14 tests. Sin red
  (dobles en memoria). Vistas SwiftUI validadas en dispositivo
  (`install-app.sh`), fuera de cobertura.

## Datos de prueba

- Fixtures en memoria + JSON embebido para decode. Sin credenciales ni red
  reales.
