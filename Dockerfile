FROM python:3.11-slim

WORKDIR /workspace

# Instalar paquetes necesarios
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
    git \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación y carpetas vacías
COPY app ./app
COPY data ./data
# COPY models ./models

# Configurar PYTHONPATH para que 'app' sea reconocible
ENV PYTHONPATH=/workspace

# Exponer puerto y ejecutar Streamlit
EXPOSE 8501
CMD ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--logger.level=debug"]
