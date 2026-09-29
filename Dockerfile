FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 MLFLOW_DISABLE_AGENT_HINT=1 MPLCONFIGDIR=/tmp/matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 curl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements-lock.txt pyproject.toml ./
RUN pip install -r requirements-lock.txt
COPY src ./src
RUN pip install --no-deps . && useradd --uid 10001 --create-home signalforge
COPY . .
RUN mkdir -p models data/raw data/processed data/features mlruns docs/assets && chown -R signalforge:signalforge /app
USER signalforge
EXPOSE 8000
CMD ["sh", "scripts/start-api.sh"]
