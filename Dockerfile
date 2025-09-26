FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential default-libmysqlclient-dev pkg-config dos2unix \
    && rm -rf /var/lib/apt/lists/*

# copia tudo (incluindo entrypoint.sh)
COPY . /app

# garante que entrypoint exista, conserta line endings e permissão
RUN if [ -f /app/entrypoint.sh ]; then \
      sed -i '1s/^\xEF\xBB\xBF//' /app/entrypoint.sh || true; \
      dos2unix /app/entrypoint.sh || true; \
      chmod +x /app/entrypoint.sh; \
    else echo "WARN: /app/entrypoint.sh not found during build"; fi

RUN pip install --upgrade pip && pip install -r /app/requirements.txt

ENTRYPOINT ["/app/entrypoint.sh"]
