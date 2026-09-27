# Visión de Negocio — Futmondo Analytics

## Dominio

Aplicación web **multi-usuario** para gestionar y analizar campeonatos de
**Futmondo** (fantasy football). Cada usuario se autentica con sus propias
credenciales de Futmondo; los datos de campeonato (transacciones, jugadores,
clasificación) se comparten entre los usuarios de un mismo campeonato.

## Propósito

Dar a los participantes de una liga Futmondo una herramienta analítica sobre
su PWA (instalable en iPhone) para tomar decisiones de mercado y seguir sus
finanzas, apoyándose en datos externos (Futmondo, Sofascore) sin coste de
infraestructura (tiers gratuitos: Neon, Fly.io, GitHub Actions).

## Funcionalidad clave

- **Presupuesto**: saldos por equipo con detalle de altas/bajas y puja máxima.
- **Mercado**: jugadores del computer con puja sugerida, rating Sofascore y
  tendencia; pujar con validación min/max.
- **Sincronización asíncrona**: sync en background con progreso paso a paso
  (11 pasos: jugadores, transacciones, cláusulas, castigos, dream teams,
  rendimiento, plantillas, clasificación, odds, phantoms, sofascore).
- **Finanzas**: cálculo de dinero por usuario (presupuesto + puntos×€ + profit
  de transacciones + dream team + MVP + clasificación proporcional + castigos).
- **Analítica**: evolución, estadísticas, clausulables, analytics avanzado
  (Chart.js) y asistente conversacional (Gemini/Groq).
- **PWA / Dark Mode**: service worker, manifest, meta Apple; tema persistido.

## Actores e integraciones

- **Actor primario**: participante de una liga Futmondo (usuario multi-tenant).
- **Integraciones externas**: API Futmondo (fuente de verdad del juego), API
  Sofascore (ratings), Gemini/Groq (asistente).

> Detalle de superficie de API en `api-documentation.md`; componentes y
> responsabilidades en `component-inventory.md`.

## Contexto del intent activo

`260927-god-files-refactor` (scope `refactor`, Minimal) es una intervención
brownfield de **reducción de deuda estructural** en la capa de servicios del
backend (FR13): descomponer los god files
(`data_manager_v2.py`, `data_sync_service.py`, `assistant_service.py`,
`analytics_service.py`) que hoy mezclan lógica de negocio con acceso a datos
(SQL crudo inline). No añade funcionalidad de negocio; **preserva el
comportamiento observable** (characterization-first) y la superficie pública
consumida por routers y servicios. Responsabilidades mezcladas, seams de
extracción candidatos, superficie pública a preservar y cobertura de tests
por god file en `code-structure.md`; riesgos y estado de calidad en
`code-quality-assessment.md`.

> El intent previo `260925-limpieza-config-residuos` (limpieza de dead-path de
> BD, IDs hardcodeados y residuos versionados) sigue reflejado en los
> artefactos; su prosa se preserva fuera del área re-analizada aquí.
