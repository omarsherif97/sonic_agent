#==================================
# Base Image Configuration
#==================================
FROM ghcr.io/astral-sh/uv:0.6.14-python3.10-bookworm AS base
WORKDIR /app

#==================================
# System Dependencies
#==================================
RUN apt-get update && apt-get install -y \
  build-essential libavif-dev pkg-config libjpeg-dev gcc unzip zip python3-dev \
  libxml2-dev libxslt1-dev libffi-dev curl && rm -rf /var/lib/apt/lists/*

#==================================
# Python Dependencies
#==================================
COPY requirements.txt .
RUN uv pip install -r requirements.txt --system

#==================================
# Environment Configuration
#==================================
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONPATH=/app

#==================================
# Copy Application Code
#==================================
COPY src/ ./src/
COPY main.py .
COPY run_chatbot.py .

#==================================
# Backend Service Configuration
#==================================
FROM base AS backend
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

#==================================
# Frontend Service Configuration
#==================================
FROM base AS frontend
EXPOSE 8001

# Create necessary directories for Chainlit
RUN mkdir -p /app/src/Frontend/.files /app/src/Frontend/.chainlit && \
    chmod 755 /app/src/Frontend/.files /app/src/Frontend/.chainlit

# Create startup script
RUN printf '#!/bin/bash\ncd /app/src/Frontend\nexec python -m chainlit run app.py --port 8001 --host 0.0.0.0\n' > /app/start_frontend.sh && \
    chmod +x /app/start_frontend.sh

CMD ["/app/start_frontend.sh"]