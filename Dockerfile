
# Usar una imagen base oficial de Python completa para evitar problemas de dependencias del sistema
FROM python:3.11

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias (aunque la imagen completa suele tenerlas)
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    ca-certificates \
    procps \
    net-tools \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código de la aplicación
COPY . .

# Exponer el puerto en el que correrá la aplicación
EXPOSE 8000

# Healthcheck explícito
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para ejecutar la aplicación usando Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
