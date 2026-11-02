// Cloudflare Pages Function — proxy de /auth/* al backend FastAPI en Fly.io.
//
// Mismo propósito que functions/api/[[path]].js pero para las rutas de
// autenticación (/auth/login, /auth/refresh, /auth/logout, ...).
//
// Ruta: functions/auth/[[path]].js  →  captura /auth/*

const BACKEND = "https://futmondo-api.fly.dev";

export async function onRequest(context) {
  const { request } = context;
  const url = new URL(request.url);

  const target = BACKEND + url.pathname + url.search;

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
