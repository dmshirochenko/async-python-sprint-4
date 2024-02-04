#!/bin/sh

. /usr/src/app/.env

# Use a SQL query to check if the alembic_version table exists and store the result
TABLE_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -tAc "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'alembic_version');" 2>/dev/null)

if [ "$TABLE_EXISTS" = 't' ]; then
    echo "Migrations have already been applied"
else
    echo "Running migrations"
    alembic revision --autogenerate -m "Create tables in url_shorter schema"
    alembic upgrade head
fi

exec uvicorn src.main:app --host 0.0.0.0 --port 8000
