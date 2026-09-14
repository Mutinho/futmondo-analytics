---
name: analysis-plan
depth: Standard
keywords: []
change_control: relaxed
---

# analysis-plan scope

Scope compuesto a medida para un trabajo centrado en el análisis y el diseño,
sin llegar a la construcción ni al despliegue. Recorre las etapas de
comprensión y definición —captura de intención, definición de alcance,
ingeniería inversa del código existente, análisis de requisitos, diseño de
dominio y requisitos no funcionales— y detiene ahí el flujo: no genera código,
no ejecuta pruebas ni despliega nada.

Está pensado para producir un plan de análisis razonado sobre la base de código
brownfield actual, dejando los artefactos de diseño listos para que una fase de
construcción posterior (por ejemplo `feature` o `mvp`) los retome.

Control de cambios: `relaxed` — si una entrada cambia después de una aprobación,
se registra y se anuncia en una línea, y el flujo continúa en lugar de reabrir
la aprobación.

## Membresía

Inicialización (workspace-scaffold, workspace-detection, state-init),
intent-capture, scope-definition, reverse-engineering, requirements-analysis,
domain-design y nfr-requirements se ejecutan; el resto de las etapas se omite.

Este scope se compuso a medida y NO es inferible por palabras clave
(`keywords: []`); solo se resuelve por nombre explícito con `--scope
analysis-plan`.
