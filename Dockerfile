FROM python:3.11-slim

WORKDIR /srv

RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU-only torch first explicitly (unpinned — PyTorch periodically
# drops old +cpu wheels from their index, so pinning an exact version here
# breaks the build once that version is no longer served; this grabs
# whatever current CPU build is available instead).
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

ENV PORT=8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port $PORT"]