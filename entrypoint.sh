#!/bin/sh
set -e

echo "Esperando MySQL em ${DB_HOST}:${DB_PORT}..."
until python - <<'PYCODE'
import os, socket
host = os.environ.get("DB_HOST","db")
port = int(os.environ.get("DB_PORT","3306"))
s = socket.socket()
try:
    s.connect((host, port))
    print("MySQL OK")
except Exception as e:
    print("Aguardando MySQL...", e)
    raise SystemExit(1)
finally:
    s.close()
PYCODE
do
  sleep 2
done

echo "Aplicando migrações..."
python manage.py migrate --noinput

echo "Subindo Django em 0.0.0.0:8000"
python manage.py runserver 0.0.0.0:8000
