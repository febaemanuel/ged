# ============================================
# Dockerfile - Sistema GED EBSERH
# ============================================
FROM python:3.11-slim

LABEL maintainer="Sistema GED EBSERH"
LABEL description="Sistema de Gestão Eletrônica de Documentos para EBSERH"

# Define variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório da aplicação
WORKDIR /app

# Copia requirements primeiro (cache de layer)
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/app/uploads/documentos \
    /app/app/uploads/publicados \
    /app/uploads/assinaturas \
    /app/logs

# Cria usuário não-root para segurança
RUN useradd -m -u 1000 geduser && \
    chown -R geduser:geduser /app

# Muda para usuário não-root
USER geduser

# Expõe porta da aplicação
EXPOSE 5000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health', timeout=5)" || exit 1

# Script de inicialização
COPY --chown=geduser:geduser docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
