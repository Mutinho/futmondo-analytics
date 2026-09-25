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

`260925-limpieza-config-residuos` (scope `refactor`, Minimal) es una
intervención de **limpieza** brownfield: retirar ramas de BD muertas
(SQLite/Turso frente a Neon en producción), IDs hardcodeados residuo de la
etapa mono-usuario, el doble montaje de `matchdays` y artefactos basura
versionados. No añade funcionalidad de negocio; reduce deuda. Hallazgos y
riesgos en `code-quality-assessment.md`.
