#!/bin/bash
cpu_cores=$(nproc)
worker_count=$((cpu_cores*2+1))

echo "Making database migrations..."
python manage.py migrate

echo "Starting Gunicorn with $worker_count worker threads..."

exec gunicorn website.wsgi:application --bind 0.0.0.0:8000 --workers $worker_count
