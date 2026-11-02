// Cloudflare Pages Function — proxy de /api/* al backend FastAPI en Fly.io.
//
// Reemplaza el proxy inverso que hacía nginx (nginx.prod.conf). Cloudflare Pages
// no permite proxy a dominios externos vía _redirects, así que el reenvío se
// hace aquí. Soporta todos los métodos (POST, etc.), cabeceras y streaming (SSE
// del asistente en /api/v1/assistant/ask/stream).
//
// Ruta: functions/api/[[path]].js  →  captura /api/*

const BACKEND = "https://futmondo-api.fly.dev";

export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);

  // Reconstruir la URL destino conservando path (/api/...) y query string.
  const target = BACKEND + url.pathname + url.search;

  // Clonar la petición hacia el backend. `redirect: "manual"` evita que el
  // edge siga redirects del backend de forma opaca.
  const init = {
    method: request.method,
    headers: request.headers,
    body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
    redirect: "manual",
    // duplex requerido al enviar un body como stream (p. ej. POST con cuerpo).
    duplex: "half",
  };

  return fetch(target, init);
}
