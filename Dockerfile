# Usar imagen oficial ligera de Python
FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# Añadir Poetry al PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema y Poetry
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY pyproject.toml poetry.lock* ./

# Instalar dependencias del proyecto (solo runtime para produccion)
RUN poetry install --no-root --only main

# Copiar el código fuente
COPY src/ ./src/

# Exponer el puerto
EXPOSE 8000

# Comando de inicio
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
