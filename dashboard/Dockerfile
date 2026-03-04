# Dockerfile para Dashboard En Las Nubes
# Multi-stage build para React + Vite

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# Stage 2: Producción con nginx
FROM nginx:alpine

# Instalar curl para el healthcheck más robusto que wget en Alpine
RUN apk add --no-cache curl

# Copiar la configuración nginx externa (incluye cabecera anti-QUIC Alt-Svc: clear)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar build desde stage anterior
COPY --from=builder /app/dist /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://127.0.0.1/ || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
