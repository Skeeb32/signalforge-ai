#!/bin/sh
set -eu
alembic upgrade head
if [ ! -f models/production/metadata.json ]; then
  python -m signalforge train
  python -m signalforge promote
fi
exec uvicorn signalforge.api:app --host 0.0.0.0 --port 8000
