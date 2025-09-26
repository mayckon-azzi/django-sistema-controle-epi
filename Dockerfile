FROM python:3.12-slim

# Evita .pyc e ativa stdout sem buffer
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema para compilar mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential default-libmysqlclient-dev pkg-config dos2unix \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copia o projeto
COPY . /app

# Converte entrypoint para Unix LF (remove CRLF do Windows) e garante permissão
RUN dos2unix /app/entrypoint.sh || true
RUN chmod +x /app/entrypoint.sh

# Define entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
