#!/bin/sh
set -e
exec gunicorn mpaeureview.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-3}" \
  --threads "${GUNICORN_THREADS:-2}" \
  --timeout "${GUNICORN_TIMEOUT:-120}" \
  --worker-tmp-dir /dev/shm \
  --access-logfile - \
  --error-logfile - \
  --capture-output
