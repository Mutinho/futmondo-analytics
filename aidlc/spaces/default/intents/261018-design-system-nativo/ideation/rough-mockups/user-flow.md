# User Flow — Sistema de diseño / theming nativo iOS (SwiftUI)

> Fase: ideación. Idioma: castellano; tokens técnicos verbatim en inglés.
> Flujo principal (happy path) de las dos superficies del intent. No es UI de producto final: la del catálogo es una pantalla de desarrollo/verificación.

## Flujo principal (happy path)

El flujo verificable es el del catálogo; el login revestido no cambia su flujo funcional respecto a F1. [Q2]

```
  Abrir app (modo desarrollo)
            │
            ▼
   ┌─────────────────────┐
   │  Catálogo / Preview  │
   └─────────┬───────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
 Alternar          Cambiar tamaño
 claro/oscuro      de texto (Dynamic Type)
     │                │
     └───────┬────────┘
             ▼
  Verificar visualmente tokens y
  componentes contra el tema Angular
```

> Nota de trazabilidad (IN-5 / Success Metrics): la verificación cubre **ambas** dimensiones a la vez — tema claro/oscuro **y** varios tamaños de Dynamic Type — no como ramas alternas sino como comprobación conjunta del catálogo.

```
  (en paralelo, flujo real de F1, sin cambios funcionales)
  Login revestido → email + contraseña → Iniciar sesión
        │                                      │
        │                                 (éxito) → app
        └── (error) → estado de error del sistema
```

## Information architecture (resumen)

- **Catálogo**: una pantalla con scroll, secciones Colores → Tipografía → Espaciado → Componentes. [Q3]
- **Login revestido**: una pantalla, card centrada sobre gradiente verde, con los componentes del sistema (campo, botón, estado de error). [Q1]

## Assumptions & Open Questions

None.
