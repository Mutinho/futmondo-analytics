# Drift Report — F2 (Feedback & Optimization)

> Fase: operación (cierre). Idioma: castellano; tokens técnicos verbatim en inglés.

## Deriva de diseño/datos

| Punto de deriva | Detección | Mitigación |
|-----------------|-----------|------------|
| Tema Angular evoluciona y los tokens nativos quedan desalineados | revisión al tocar `styles.scss` | re-sincronizar tokens de `FutmondoKit`/`FutmondoApp` DesignSystem |
| Endpoints de balances/championships cambian de forma | fallo de decode en la app | DTOs `Codable` estrictos; el `fetch` degrada a error con Reintentar |
| **Inconsistencia de "saldo" lista vs detalle** | ya observada | **deuda de backend registrada** (lista suma premios, detalle no); intent de backend aparte |
| Hueco WSL (errores arm64-only) | aparece al build en dispositivo | aprendizaje durable: declarar `Sendable`/`Equatable`, cualificar tipos vs SwiftUI, APIs `#available` |

## Deriva de infraestructura

NO-APLICA: F2 no provisiona infraestructura.

## Assumptions & Open Questions

None.
