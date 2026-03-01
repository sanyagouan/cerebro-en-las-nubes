# Dockerfile optimizado para Coolify - Cerebro En Las Nubes
# v3.4 - Fix booking_repo field names + force cache invalidation

# ==================== Stage 1: Builder ====================
FROM python:3.11-slim AS builder

# Labels para metadata
LABEL maintainer="En Las Nubes Team"
LABEL version="3.4"
LABEL description="Backend API para sistema de reservas"

# ARG para invalidar cache (DEBE usarse para que funcione)
ARG CACHEBUST=3
RUN echo "Cache bust: $CACHEBUST"

WORKDIR /app

# Instalar dependencias de compilación
# Combined run para reducir capas
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar e instalar requirements (antes del código para cache)
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt \
    && find /root/.local -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ==================== Stage 2: Runtime ====================
FROM python:3.11-slim AS runtime

# Crear usuario no-root para seguridad
RUN groupadd -r cerebro && useradd -r -g cerebro cerebro

WORKDIR /app

# Instalar solo runtime dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
        procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copiar dependencias desde builder
COPY --from=builder --chown=cerebro:cerebro /root/.local /home/cerebro/.local
ENV PATH=/home/cerebro/.local/bin:$PATH

# Crear directorios necesarios
RUN mkdir -p /app/logs \
    && chown -R cerebro:cerebro /app

# Copiar código fuente (último para mejor cache)
COPY --chown=cerebro:cerebro src/ ./src/

# Forzar invalidación de cache después del COPY
ARG CACHEBUST_SRC=3
RUN echo "Source cache bust: $CACHEBUST_SRC" && ls -la ./src/core/logic/

# Switch a usuario no-root
USER cerebro

# Environment optimizado
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PYTHONHASHSEED=random

EXPOSE 8000

# Health check optimizado (reducido de 40s a 15s start-period)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando optimizado para producción
CMD ["uvicorn", "src.main:app", \
    "--host", "0.0.0.0", \
    "--port", "8000", \
    "--workers", "4", \
    "--proxy-headers", \
    "--forwarded-allow-ips", "*"]
