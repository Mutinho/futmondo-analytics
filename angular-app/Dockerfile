# ===========================================
# Futmondo Analytics — Frontend (Angular 22)
# Multi-stage: Node build → nginx serve
# ===========================================

# --- Stage 1: Build ---
FROM node:24-alpine AS build

WORKDIR /app

# Copiar package files para layer caching
COPY package.json package-lock.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Build de producción (NODE_TLS necesario para Google Fonts)
RUN NODE_TLS_REJECT_UNAUTHORIZED=0 npx ng build --configuration=production

# --- Stage 2: Serve con nginx ---
FROM nginx:alpine

# Select nginx config: use NGINX_CONF build arg (default: nginx.conf for local docker-compose)
ARG NGINX_CONF=nginx.conf
COPY ${NGINX_CONF} /etc/nginx/conf.d/default.conf

# Copiar build de Angular
COPY --from=build /app/dist/angular-app/browser /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -q --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
