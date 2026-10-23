# Unit Test Instructions — U2 `u2-login-theming`

> Fase: construcción. Idioma: identificadores/comentarios en INGLÉS; prosa en castellano.

## Framework y configuración

- No se añaden tests nuevos: U2 reviste una pantalla SwiftUI (`LoginView`) en `FutmondoApp`, que no se testea con `swift test` en WSL (SwiftUI no compila en Linux; se valida en dispositivo). `AuthViewModel`/`AuthService` ya están cubiertos por los tests de F1 y U2 no los modifica.

## Comando (scoped)

```
cd ios && swift build && swift test
```

Obligación de testing de U2: tras el revestimiento, `swift build` compila y la suite existente sigue en verde (43 tests: 29 de F1 + 14 de U1), **sin regresión**. No hay tests específicos de U2 ejecutables en WSL.

## Cobertura esperada

- Sin cambio de cobertura numérica (no se añade lógica testeable; la cobertura line vía llvm-cov no es medible de forma fiable en WSL — aprendizaje durable). La no-regresión funcional del login se valida manualmente en el iPhone 13 Pro.

## Verificación manual (dispositivo)

- login → auto-login (Keychain) → logout funcionan igual que F1.
- Aspecto coherente con el sistema de diseño en claro y oscuro; Dynamic Type escala el texto.

## Assumptions & Open Questions

None.
