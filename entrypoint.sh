#!/bin/bash
cpu_cores=$(nproc)
worker_count=$((cpu_cores*2+1))

echo "Making database migrations..."
python manage.py migrate

# Start Celery in the background
echo "Starting Celery..."
celery -A core worker -l info &

# Start Daphne with ASGI application
echo "Starting Daphne with $worker_count worker threads..."
exec daphne -u /tmp/daphne.sock core.asgi:application
