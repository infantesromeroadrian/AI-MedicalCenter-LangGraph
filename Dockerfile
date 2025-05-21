FROM python:3.10-slim

WORKDIR /app

# Instalar dependencias del sistema incluyendo lo necesario para generación de PDF
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wkhtmltopdf \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libpq-dev \
    fontconfig \
    libfontconfig1 \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    xfonts-75dpi \
    xfonts-base \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Eliminar archivos de caché de Python para evitar problemas
RUN find . -name __pycache__ -type d -exec rm -rf {} +
RUN find . -name "*.pyc" -delete

# Puerto que expondrá la aplicación
EXPOSE 3567

# Configurar variable de entorno para Flask
ENV FLASK_APP=src.app
ENV FLASK_DEBUG=0
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Comando para ejecutar la aplicación
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=3567"] 