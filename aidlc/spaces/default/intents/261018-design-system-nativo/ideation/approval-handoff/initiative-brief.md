# Initiative Brief — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: ideación (cierre). Idioma: castellano; tokens técnicos verbatim en inglés.
> One-pager que consolida la ideación para la decisión go/no-go y el handoff a Inception.

## Intent y problema

Entregar una **capa de diseño reutilizable en SwiftUI** (tokens de color claro/oscuro, tipografía Roboto con Dynamic Type, espaciado y componentes base: botón, campo, tarjeta, estados de carga/error) que **precede a F2**, la alimenta y reviste el login de F1. Sin una base común, construir F2+ causaría retrabajo, incoherencia visual y lentitud. [Q1 (intent-capture)] [intent-statement]

## Validación de mercado

NO-APLICA: intent interno para un proyecto personal de un único usuario; Market Research saltada. [stakeholder-map]

## Feasibility y riesgos

**GO** técnico: SwiftUI + SDK de Apple cubren la capa con holgura, a coste 0 €, sin AWS ni compliance. Riesgos clave (RAID): (1) fidelidad de reproducción del tema de Angular en SwiftUI — mitigada con un spike inicial, el catálogo de verificación y Apple HIG de relleno; (2) transversalidad claro/oscuro + Dynamic Type; (3) revestir F1 sin regresión; (4) curva de aprendizaje SwiftUI. [feasibility-assessment] [constraint-register]

## Boundary de alcance

- **Dentro**: tokens (color/tipografía/espaciado), componentes base, catálogo/preview, revestir F1. [scope-document]
- **Fuera**: tab bar nativa (B-08 → F2), aplicación a pantallas de F2, animaciones avanzadas, temas más allá de claro/oscuro, dependencias de pago. [scope-document]

## Visuales de concepto

Dos pantallas: catálogo/preview (Colores → Tipografía → Espaciado → Componentes) y login de F1 revestido (card sobre gradiente verde, basado en el layout real de Angular). Referencia de diseño: tema del frontend Angular (`angular-app/src/styles.scss`); Google Stitch descartado. [wireframes]

## Plan de equipo

Único mantenedor; sin mob ni asignación de capacidad (Team Formation saltada). [stakeholder-map]

## Recomendación go/no-go

**GO — proceder a Inception.** Alcance acotado, riesgos reconocidos con mitigaciones, coste 0 €, referencia de diseño decidida. [Q5]

## Assumptions & Open Questions

- [assumption] El mapeo exacto de roles de color Material 3 → SwiftUI y de la escala tipográfica se concreta en refined-mockups / diseño de Inception. [wireframes]
