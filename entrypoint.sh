#!/bin/bash

set -e

echo "Esperando a PostgreSQL..."
while ! nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL está listo."

echo "Ejecutando migraciones..."
python manage.py migrate --noinput

if [ $# -gt 0 ]; then
    exec "$@"
fi

echo "Iniciando servidor Django..."
exec python manage.py runserver 0.0.0.0:8000
