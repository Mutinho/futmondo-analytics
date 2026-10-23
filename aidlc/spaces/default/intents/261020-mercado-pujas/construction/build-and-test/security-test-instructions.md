# Security Test Instructions — F3 Mercado (u1-market)

> F3 introduce **escritura** (pujar/cancelar) y un **2º endpoint externo**
> (Sofascore); ambos refuerzan garantías de seguridad ya afirmadas. Estas
> comprobaciones verifican que no hay fuga de credenciales y que la auth se
> preserva. El escaneo de secretos (gitleaks) y de dependencias
> (`pip-audit`/`npm audit`) del gate de CI siguen siendo bloqueantes, pero no
> cubren el subárbol `ios/` Swift; aquí se documentan las comprobaciones
> específicas de la Unit.

## Marco y configuración

- XCTest sobre `FutmondoKit` (`swift test --package-path ios`) con dobles
  in-memory; sin red ni credenciales reales.

## Comprobaciones de seguridad

| ID | Comprobación | Dónde / cómo |
|---|---|---|
| NFR3.6 | Ningún material de credencial en avisos de error ni en el `NetworkError` tipado (no refleja la URL, ni id/token) | `MarketServiceTests` aseveran que los avisos usan sólo `message`/`detail` del backend o texto genérico |
| NFR3.5 | Rechazo de base URL no-https en el `init` del cliente (SEC-N1) | Cubierto por los tests de `URLSessionNetworkClient` (F1, reutilizado) |
| NFR3.7 | Sin secretos/tokens hardcodeados en código ni tests | gitleaks (gate CI) escanea todo el árbol; los tests usan dobles/fixtures sintéticos |
| NFR3.1/NFR3.8 | Toda llamada (incl. escritura) viaja con `Bearer`; sin ruta sin auth | `MarketServiceTests` aseveran el header `Bearer` en cada `APIRequest` |
| NFR3.4 | Validación en dos capas (cliente + backend autoridad) | `BidAmountValidatorTests` (cliente) + el backend revalida `price>0`/`price≤5e9` |

## Cómo correr

```
swift test --package-path ios
```

## No aplica (justificado)

- SAST/DAST formal del target Swift: no hay herramienta en el tier gratuito
  integrada para Swift en este repo; la cobertura de seguridad de F3 se apoya en
  los tests de no-fuga + gitleaks del gate. (Deuda diferida conocida; sin coste.)

## Assumptions & Open Questions

None.
