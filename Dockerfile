FROM python:3.11-slim

# XGBoost needs the OpenMP runtime on Linux
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

# model.joblib is gitignored, so train it at build time
RUN python -m app.ml.train

ENV PORT=10000
CMD exec uvicorn app.api.main:app --host 0.0.0.0 --port $PORT