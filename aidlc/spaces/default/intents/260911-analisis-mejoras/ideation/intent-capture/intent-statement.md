# Enunciado de Intención — Análisis y Plan de Mejoras de futmondo-analytics

## Problem Statement

El proyecto futmondo-analytics es una aplicación web multi-usuario (PWA) para gestionar y analizar campeonatos de Futmondo, ya en producción. Antes de seguir añadiendo funcionalidades, se quiere reducir la deuda técnica y consolidar la base para poder crecer con mayor seguridad, apoyándose en un análisis general y amplio de arquitectura, código e infraestructura. [desc] [Q1]

El análisis debe ser transversal (no centrado en un único dolor), pero usando como lente de priorización el objetivo de "preparar el proyecto para crecer con seguridad". [Q1]

## Target Customer

El sistema lo usa un grupo reducido (uso personal o de amigos jugando su liga de fantasy). El cliente de este análisis es el propio autor, que actúa como único desarrollador-mantenedor del proyecto. En consecuencia, el plan debe favorecer mejoras que reduzcan el trabajo manual y el riesgo operativo de un mantenedor único. [Q2]

## Success Metrics

Un buen resultado combina tres entregables (que este trabajo producirá a lo largo de sus etapas): [Q3]

- Un backlog priorizado y accionable de mejoras y puntos críticos-débiles, para abordar en futuros intents. [Q3] [Q6]
- Un mapa claro de la arquitectura actual (documentación de la que hoy se carece o está incompleta). [Q3]
- Criterios objetivos de calidad en los ejes no funcionales: seguridad, fiabilidad y rendimiento. [Q3]

Cada elemento del backlog debe llevar una etiqueta de prioridad (crítico / importante / opcional) con su justificación, para que el mantenedor decida el orden. [Q6]

## Initiative Trigger

No hay una urgencia única ni un incidente concreto que dispare el trabajo; el disparador es el deseo de consolidar la base técnica antes de escalar en funcionalidad. [Q1]

Existen áreas señaladas de antemano como candidatas a debilidad, que el análisis debe mirar con especial atención sin renunciar al barrido general: [Q4]

- Integraciones externas (API de Futmondo y API de Sofascore vía `curl_cffi`) y su fragilidad frente a cambios o límites de tasa. [Q4]
- La sincronización asíncrona de 11 pasos (fiabilidad, reintentos, gestión del estado de las tareas). [Q4]
- Tests y CI (el frontend no muestra specs de test; conviene revisar la cobertura del backend). [Q4]

La autenticación y gestión de sesiones/tokens se analizará igualmente por tratarse de un área sensible, aunque no se haya marcado como sospecha previa. [Q4]

## Initial Scope Signal

- **Alcance seleccionado por el workflow** (workflow-selected): `analysis-plan` — analizar y producir un plan, sin escribir código de aplicación ni desplegar. [scope]
- **Límite de producto confirmado por el usuario**: solo análisis + plan en este trabajo; la implementación de cada mejora se abordará en futuros intents independientes. [Q7]

## Restricciones (constraints)

- Mantener el stack tecnológico actual (Angular + FastAPI + Neon PostgreSQL + Fly.io); las mejoras propuestas no deben implicar reescrituras grandes. [Q5]
- **Restricción dura de coste 0 €**: el proyecto debe mantenerse siempre sin coste. El plan solo puede proponer mejoras sostenibles en tiers gratuitos (p. ej. Neon free, la franja gratuita de Fly.io, GitHub Actions free) y debe descartar explícitamente cualquier recomendación que implique gasto recurrente. [Q5]

## Assumptions & Open Questions

None.
