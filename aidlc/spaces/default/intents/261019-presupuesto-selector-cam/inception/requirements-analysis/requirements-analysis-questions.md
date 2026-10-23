# Requirements Analysis — Questions (F2)

> Fase: inception. Idioma: castellano; tokens técnicos verbatim en inglés.

## Consolidated Summary Confirmation

Resumen de Requirements Analysis:

- **FR1** Presupuesto: lista por equipo con los 9 campos de `TeamBudget`, formato M/K con tokens `money-positive`/`money-negative` (color + signo), desde `GET /api/v1/analytics/balances`.
- **FR2** Ordenación por las 6 claves de la web.
- **FR3** Selector en la navigation bar (`GET /api/v1/user/championships` con fallback a `/championships`); al cambiar recarga + persiste en `UserDefaults`; primer campeonato por defecto.
- **FR4** Estados de carga y error con reintento, sin corromper el campeonato activo.
- **FR5** Andamiaje de navegación `TabView` de una pestaña + `NavigationStack`.
- **NFR**: cero dependencias nuevas (NFR1); seguridad reutiliza F1, sin exponer credenciales (NFR2); fidelidad al tema Angular validada en dispositivo (NFR3); 60 fps / <100 ms percibidos (NFR4); accesibilidad VoiceOver + Dynamic Type + color no único (NFR5); verificación lógica pura en `FutmondoKit` con `swift test` (NFR6).
- Todo **trazable** a scope/backlog/codekb; endpoints y fórmula `performance = team_value + balance - initial_budget` verificados en reverse-engineering.

¿Does this all look correct?

[Answer]: Looks correct
