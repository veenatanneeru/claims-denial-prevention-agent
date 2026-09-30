FROM python:3.11-slim

# XGBoost needs the OpenMP runtime on Linux
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY data ./data

# Train the model at build time (model.joblib is gitignored) and pre-download the embedding model
RUN python -m app.ml.train
RUN python -c "from app.rag.store import search; search('warmup', k=1)"

ENV PORT=8080
CMD exec uvicorn app.api.main:app --host 0.0.0.0 --port $PORT