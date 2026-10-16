# Business Overview — futmondo-analytics

## Dominio de negocio

Futmondo Analytics es una aplicación web **multi-usuario** para gestionar y
analizar campeonatos de **Futmondo** (fantasy football). Da a cada usuario un
cuadro de mando sobre su liga: control de presupuestos, análisis de mercado,
ratings de Sofascore, pujas por jugadores y cálculo de finanzas, accesible como
PWA desde el móvil (iPhone en particular).

## Propósito

Convertir los datos crudos de la API de Futmondo (más señales externas de
Sofascore) en analítica accionable que un mánager de fantasy no obtiene en la
app oficial: evolución histórica, puja sugerida por jugador, finanzas
proyectadas por usuario y un asistente conversacional (LLM) sobre esos datos.

## Funcionalidad clave

- **Autenticación delegada en Futmondo**: el usuario entra con su email/password
  de Futmondo; el backend valida contra la API de Futmondo y emite JWT propios.
- **Multi-usuario / multi-campeonato**: cada usuario auto-detecta sus campeonatos
  al primer login; la configuración (presupuesto, premios, cláusulas) se obtiene
  de la API de Futmondo con las credenciales del usuario logado. Los datos del
  campeonato (transacciones, jugadores, standings) se comparten entre usuarios.
- **Presupuesto**: saldos por equipo con detalle de altas/bajas, puja máxima y
  rendimiento.
- **Mercado**: jugadores del computer con puja sugerida (historial), rating
  Sofascore y tendencia; modal de puja con min/max validados.
- **Sincronización asíncrona**: sync en background con progreso paso a paso
  (jugadores, transacciones, cláusulas, castigos, dream teams, rendimiento,
  plantillas, clasificación, odds, phantoms, sofascore); reconexión al task vía
  `localStorage` si se cierra el modal.
- **Finanzas**: dinero por usuario (presupuesto + puntos×€ + profit de
  transacciones + dream team + MVP + clasificación + castigos/bonificaciones).
- **Evolución, Estadísticas, Clausulables, Analytics**: gráficos (Chart.js) y
  tablas interactivas con analítica avanzada por sub-pestañas.
- **Asistente IA**: respuestas en lenguaje natural (Gemini con fallback a Groq)
  sobre los datos del campeonato, renderizadas como markdown.
- **PWA**: service worker, manifest y meta tags Apple; instalable en iPhone.

## Usuarios y valor

- **Mánager de fantasy (usuario final)**: decide pujas y traspasos con datos de
  mercado, rendimiento y finanzas que la app oficial no expone.
- El valor diferencial es el **cruce de fuentes** (Futmondo + Sofascore) y el
  **cálculo de premios/finanzas** replicando la fórmula de Futmondo.

## Contexto del intent activo

El intent `angular-native-feasibili` evalúa la **viabilidad** de llevar esta
presentación web (Angular 22 PWA + Material) a una **app nativa con Angular
Native (NativeScript + Angular)**, conservando el backend FastAPI intacto. Es un
intent de ANÁLISIS, no de implementación. Ver detalle arquitectónico en
`architecture.md` y la deuda/riesgos de portabilidad en
`code-quality-assessment.md`.
