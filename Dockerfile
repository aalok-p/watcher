FROM node:20-alpine AS frontend-builder

WORKDIR /build/frontend
COPY frontend/package*.json ./

RUN npm ci

COPY frontend/src ./src
COPY frontend/public ./public
COPY frontend/index.html ./
COPY frontend/vite.config.js ./
COPY frontend/eslint.config.js ./

RUN npm run build

RUN cp -r public/* dist/ 2>/dev/null || true

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/

COPY --from=frontend-builder /build/frontend/dist ./frontend/dist

#.env placeholder
RUN echo "# Watcher Configuration\n\
POLL_INTERVAL_SEC=3\n\
SCREENSHOT_ENABLED=true\n\
PORT=8000\n\
\n\
# OpenAI Configuration (required for AI features)\n\
OPENAI_API_KEY=your-api-key-here\n\
OPENAI_BASE_URL=https://api.openai.com/v1\n\
OPENAI_MODEL=gpt-4o-mini\n" > backend/.env

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

WORKDIR /app
RUN echo '#!/bin/bash\n\
cd /app/backend\n\
python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}\n' > /entrypoint.sh && chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
