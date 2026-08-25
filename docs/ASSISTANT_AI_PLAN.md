# Plan de Implementación — Asistente IA Futmondo

## Resumen

Agente de IA conversacional integrado en la app como botón flotante (FAB). Usa Gemini 2.0 Flash (gratis) con contexto real del campeonato del usuario para dar recomendaciones de fichajes, ventas, clausulaciones y estrategia.

---

## Arquitectura

```
┌─────────────────────────────────────────────┐
│  Frontend (Angular)                         │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  FAB flotante (🤖) → abre chat      │   │
│  │  ┌──────────────────────────────┐   │   │
│  │  │  Historial mensajes          │   │   │
│  │  │  ├ User: "¿A quién vendo?"   │   │   │
│  │  │  └ Bot: "Recomiendo vender..." │   │   │
│  │  │  Input + botón enviar        │   │   │
│  │  └──────────────────────────────┘   │   │
│  └─────────────────────────────────────┘   │
└────────────────────┬────────────────────────┘
                     │ POST /api/v1/assistant/ask
                     ▼
┌─────────────────────────────────────────────┐
│  Backend (FastAPI)                          │
│                                             │
│  1. Recibe pregunta + championship_id       │
│  2. Determina contexto necesario            │
│  3. Consulta BD (plantilla, mercado, etc.)  │
│  4. Construye prompt con datos reales       │
│  5. Llama a Gemini 2.0 Flash API           │
│  6. Devuelve respuesta                      │
└────────────────────┬────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────┐
│  Google Gemini 2.0 Flash                    │
│  - Gratis (15 RPM, 1M tokens/día)          │
│  - API key desde aistudio.google.com        │
│  - Contexto hasta 1M tokens                 │
└─────────────────────────────────────────────┘
```

---

## Frontend

### Componente: AssistantFabComponent (siempre visible)
- FAB circular fijo abajo-derecha (encima del scroll-top)
- Icono: `smart_toy` (robot de Material Icons)
- Click abre/cierra el panel de chat
- Badge con punto si hay respuesta nueva

### Componente: AssistantChatComponent (panel overlay)
- Panel flotante anclado abajo-derecha (no ocupa toda pantalla)
- Tamaño: ~380px ancho × 500px alto (desktop), fullscreen en móvil
- Header: "🤖 Asistente Futmondo" + botón cerrar
- Body: scroll de mensajes (burbujas user/bot con markdown básico)
- Footer: input de texto + botón enviar
- Estado: loading (typing indicator), error
- Historial en memoria (se pierde al recargar — sin persistencia)

### Ubicación
- En `app.ts` (shell), fuera del router-outlet
- Solo visible si el usuario está autenticado
- Se muestra en TODAS las páginas

### Interacción
- Enter o botón para enviar
- Sugerencias rápidas (chips): "¿Qué vendo?", "¿Qué ficho?", "Analiza mi plantilla"
- Respuestas con formato markdown (negrita, listas)

---

## Backend

### Endpoint: POST /api/v1/assistant/ask

```python
Request:
{
    "message": "¿A quién debería vender de mi plantilla?",
    "championship_id": "6a5f82a09c06c8d0ceaa40ee",
    "history": [  # últimos 5 mensajes para contexto conversacional
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ]
}

Response:
{
    "response": "Basándome en tu plantilla, recomiendo vender a...",
    "context_used": ["roster", "market"]  # para debug
}
```

### Módulo: AssistantService

```python
class AssistantService:
    def ask(self, user_id, championship_id, message, history) -> str:
        # 1. Detectar intención (qué contexto necesita)
        context = self.build_context(user_id, championship_id, message)
        # 2. Construir prompt
        prompt = self.build_prompt(context, message, history)
        # 3. Llamar a Gemini
        response = self.call_gemini(prompt)
        return response
```

### Contexto inyectado (según la pregunta)

| Tipo | Datos | Cuándo se inyecta |
|------|-------|-------------------|
| **Plantilla** | Jugadores del user: nombre, posición, valor, media, tendencia, sofascore | Siempre |
| **Presupuesto** | Saldo actual, valor plantilla, premios acumulados | Siempre |
| **Mercado** | Jugadores del computer hoy: nombre, valor, media, puja sugerida | Si pregunta por fichajes |
| **Agentes libres** | Top 20 por ratio: nombre, media, precio, sofascore | Si pregunta por fichajes |
| **Clausulables** | Top 10 clausulables: nombre, dueño, media, cláusula, score | Si pregunta por cláusulas |
| **Clasificación** | Posiciones, puntos, momentum de todos los equipos | Si pregunta por estrategia |
| **Transacciones** | Últimas 10 compras/ventas del user | Si pregunta por historial |

### System Prompt

```
Eres el asistente de Futmondo Analytics. Ayudas al usuario a tomar decisiones 
en su liga de fantasy football (Futmondo - Liga española).

REGLAS:
- Responde en español, de forma concisa y directa
- Basa tus recomendaciones SOLO en los datos que se te proporcionan
- Cuando recomiendes vender/comprar, justifica con datos (media, tendencia, valor)
- Usa formato con negrita y listas para claridad
- Si no tienes datos suficientes, dilo
- No inventes datos ni jugadores

CONTEXTO DEL USUARIO:
{context}
```

---

## Gemini 2.0 Flash — Integración

### Librería
```
google-genai (Python SDK oficial)
pip install google-genai
```

### Llamada
```python
from google import genai

client = genai.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        {"role": "user", "parts": [{"text": system_prompt}]},
        *history,
        {"role": "user", "parts": [{"text": user_message}]}
    ]
)
return response.text
```

### Configuración
- API Key: variable de entorno `GEMINI_API_KEY`
- Obtener gratis en: https://aistudio.google.com/apikey
- Límites free tier: 15 requests/min, 1M tokens/día, 32K tokens output
- Más que suficiente para 1 usuario

---

## Plan de implementación por pasos

### Paso 1: Setup (30 min)
- [ ] Obtener API key de Gemini
- [ ] Añadir `google-genai` a requirements.txt
- [ ] Añadir `GEMINI_API_KEY` a .env y Docker
- [ ] Crear `backend/app/services/assistant_service.py`

### Paso 2: Backend — Endpoint + Context Builder (1-2h)
- [ ] Endpoint POST `/api/v1/assistant/ask`
- [ ] Context builder: construir datos de plantilla, mercado, etc.
- [ ] System prompt con reglas
- [ ] Llamada a Gemini con historial
- [ ] Manejo de errores y rate limiting

### Paso 3: Frontend — FAB + Chat Panel (1-2h)
- [ ] `AssistantFabComponent` — botón flotante
- [ ] `AssistantChatComponent` — panel de chat overlay
- [ ] Servicio `AssistantService` (HTTP)
- [ ] Burbujas de mensaje (user/bot)
- [ ] Loading indicator (typing...)
- [ ] Chips de sugerencias rápidas
- [ ] Responsive: fullscreen en móvil

### Paso 4: Pulido (30 min)
- [ ] Markdown rendering en respuestas (negrita, listas)
- [ ] Auto-scroll al último mensaje
- [ ] Persistir historial en sessionStorage (opcional)
- [ ] Animación de entrada del panel

### Total estimado: 3-4 horas

---

## Costes

| Concepto | Coste |
|----------|-------|
| Gemini 2.0 Flash API | **Gratis** (15 RPM, 1M tok/día) |
| Almacenamiento | Ninguno (historial en memoria) |
| Infraestructura | Ninguno (usa el backend existente en Fly.io) |
| **Total mensual** | **0€** |

Si algún día superas los 15 RPM (improbable con 1 usuario), Gemini cobra $0.10/1M tokens input y $0.40/1M tokens output — aun así serían céntimos al mes.

---

## Ejemplos de uso

**Usuario:** "¿A quién debería vender?"
**Asistente:** "Basándome en tu plantilla, recomiendo considerar vender:
- **Tchouameni** — Media 2.0, valor 32M€. Rendimiento muy bajo para su precio.
- **Cubarsí** — No ha jugado (0 pts), valor 46M€. Libera mucho presupuesto.
- **Rodri** — 0 pts, 55M€ invertidos. Sin actividad.

Los tres tienen valor alto pero no están rindiendo. Venderlos liberaría ~133M€ para fichar jugadores activos."

**Usuario:** "¿Merece la pena clausular a Pablo Barrios?"
**Asistente:** "**Pablo Barrios** (Atlético, MC):
- Media: 8.5 pts/jornada
- Cláusula: 54.4M€
- Score clausulable: 45%

No lo recomiendo. Su cláusula es alta (54M€) para una media de 8.5. Hay opciones mejores como **Riquelme** (media 21, cláusula 7.6M€) o **Camello** (media 8.5, cláusula 7.2M€) con mucha mejor relación calidad/precio."

---

## Notas técnicas

- El contexto total raramente superará los 5K tokens (plantilla ~20 jugadores + mercado ~30 + metadata)
- Gemini 2.0 Flash responde en ~1-2 segundos
- No se persiste ningún dato en BD — todo es stateless
- El historial se manda desde el frontend (últimos 5-10 mensajes)
- Si Gemini falla (rate limit/error), mostrar mensaje amigable
