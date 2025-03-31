#!/bin/bash

# Функция для проверки готовности PostgreSQL
wait_for_pg() {
    until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' >/dev/null 2>&1; do
        echo "Waiting for PostgreSQL..."
        sleep 2
    done
}

# Ждем готовности БД
echo "Waiting for PostgreSQL to be ready..."
wait_for_pg

# Проверяем наличие миграций
if [ -z "$(ls -A /app/app/migration/versions)" ]; then
    echo "No migrations found, creating initial migration..."
    alembic revision --autogenerate -m "Initial revision"

    if [ $? -ne 0 ]; then
        echo "Failed to create initial migration!"
        exit 1
    fi
fi

# Применяем миграции
echo "Applying database migrations..."
alembic upgrade head

if [ $? -ne 0 ]; then
    echo "Failed to apply migrations!"
    exit 1
fi

# Проверяем существование основных таблиц
echo "Checking required tables..."
if ! PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\dt' | grep -q -E 'users|links'; then
    echo "ERROR: Required tables not found after migrations!"
    exit 1
fi

# Запускаем приложение
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8001