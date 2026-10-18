# Intent Statement — App nativa iOS desde Angular (viabilidad)

## Problem Statement

El propietario mantiene una PWA Angular (Futmondo Analytics) accesible desde iPhone,
pero quiere evaluar y planificar su conversión a una **aplicación nativa iOS** por dos
motivos combinados: lograr una experiencia más "app" nativa (menú inferior iOS, gestos,
widgets de pantalla de inicio) que la PWA no ofrece bien, y abordarlo como ejercicio
técnico/de aprendizaje con NativeScript y la herramienta `xtool` para compilar iOS desde
Windows. [Q1]

Este trabajo es un **análisis de viabilidad y planificación**, no la construcción de la
app: el entregable es un documento de viabilidad más una ruta de implementación por
fases. [desc] [Q3]

El reto de fondo es compatibilizar el objetivo nativo con el mandato durable de **coste
recurrente 0 €** del proyecto, frente al coste anual del Apple Developer Program (~99 €/año,
contemplado como excepción acotada de coste de distribución). [desc] [memory:M1]

## Target Customer

Usuario único: el propietario del proyecto, en uso personal, con el iPhone como único
dispositivo objetivo del estudio (iOS-only). [Q2] [Q7]

El beneficio es doble: una experiencia de uso más nativa de la herramienta que ya usa, y
el aprendizaje técnico de la cadena NativeScript + `xtool` + firma iOS desde Windows. [Q1]

## Success Metrics

Este análisis se considera exitoso si entrega, de forma conservadora y con supuestos
marcados: [desc]

- Un **go/no-go** sobre migrar a nativo con NativeScript, con esfuerzo estimado y riesgos
  de portabilidad del código Angular existente. [Q3]
- La confirmación (o refutación) de que el **flujo técnico a coste recurrente 0 €** es
  viable: compilar iOS en Windows con `xtool` e instalar en el iPhone mediante firma
  gratuita, asumiendo el refirmado cada ~7 días. [Q3] [Q4] [Q5]
- Una **comparativa explícita de las dos rutas de distribución** —firma gratuita que
  caduca cada ~7 días vs. Apple Developer Program ~99 €/año— con pros/contras y una
  recomendación. [Q3] [Q5] [memory:M1]
- Una **ruta de implementación por fases** (qué se reutiliza del backend/Angular, qué se
  reescribe y en qué orden), mantenida a nivel de fases y bloques reutilizables, lista para
  abrir un intent de construcción posterior. [Q3]

## Initiative Trigger

Oportunidad personal: el deseo de una experiencia nativa iOS sobre una app que ya existe
como PWA, combinado con la aparición de una vía técnica (`xtool`) que, en principio,
permitiría compilar y firmar iOS sin Mac, usando sólo Windows —la única máquina
disponible—. No hay presión de mercado ni de regulación. [Q1] [Q4]

## Initial Scope Signal

- **Workflow-selected scope**: `bugfix` (plan a medida `feasibility-ios-native` sobre esa
  base, sólo para esta pieza de trabajo). [scope]
- **User-confirmed product boundary** (lo que esta primera versión / análisis deja fuera):
  [Q8]
  - Fuera: publicación en App Store para terceros (distribución pública masiva); el estudio
    se centra en instalación personal/privada. [Q8]
  - Fuera: Android / NativeScript-Android; el estudio es iOS-only. [Q2] [Q8]
  - Fuera: cualquier cambio en el backend FastAPI o la infraestructura Fly.io/Neon; se asume
    el backend intacto. [Q8]
  - **Dentro**: la portabilidad de la UI al modelo nativo (controles iOS, menú inferior) se
    analiza como parte del esfuerzo de migración, no como rediseño visual desde cero. [Q8]
- **Alcance funcional objetivo de la primera versión nativa** (subconjunto núcleo, no
  paridad total con la PWA): Login, Mercado, Presupuesto, Favoritos y Calculadora. [Q6]

## Assumptions & Open Questions

- [assumption] "Favoritos" y "Calculadora" son funciones nombradas por el propietario que
  no aparecen literalmente en el README de la PWA; se asume que "Calculadora" corresponde a
  la función de Finanzas y "Favoritos" a una vista de jugadores marcados. A confirmar en
  reverse-engineering contra el código Angular real. [Q6]
- [assumption] Se asume que la firma gratuita de Apple (free provisioning) caduca a los
  ~7 días y obliga a reinstalar/refirmar; el valor exacto y el flujo concreto se verificarán
  en la etapa de feasibility. [Q5]
- [assumption] Se asume que `xtool` permite compilar y firmar iOS desde Windows sin Mac; su
  alcance real, requisitos y límites son objeto del estudio de feasibility. [Q4] [desc]
