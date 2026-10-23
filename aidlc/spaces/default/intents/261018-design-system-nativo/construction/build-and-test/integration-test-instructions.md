# Integration Test Instructions — Sistema de diseño nativo iOS

> Fase: construcción. Idioma: castellano; tokens técnicos verbatim en inglés.

## Boundary clave: U2 (login revestido) ↔ U1 (librería del sistema de diseño)

La integración entre Units es **in-process** (API pública Swift de la librería `DesignSystem` consumida por `LoginView`). Se verifica a nivel de compilación y de tests unitarios:

```
cd ios && swift build && swift test
```

- **Integración de compilación**: que `FutmondoApp` (que consume los componentes/tokens de U1) compile contra `FutmondoKit`/el módulo de diseño confirma que el contrato público (tipos, firmas) encaja. Un cambio rompiente en la API de U1 fallaría el build (red de seguridad del compilador, como fija contract-summary).
- **Tests unitarios de la lógica de U1**: `swift test --filter FutmondoKitTests.DesignSystem` ejercita la lógica de tokens (resolución claro/oscuro, espaciado, tipografía, contraste) que consumen ambos componentes y el login.

## Integración con F1 (no-regresión)

El login revestido (U2) reutiliza `AuthViewModel`/`AuthService` de F1 sin cambios; la suite existente (29 tests de F1) corriendo en verde confirma que la integración con auth no se rompió.

## Dimensión en dispositivo (manual)

La integración visual completa (claro/oscuro, Dynamic Type, cadena de foco del login — riesgo abierto) se valida en el iPhone 13 Pro con `xtool`, fuera de `swift test`.

## Assumptions & Open Questions

None.
