# Dockerfile for Hugging Face Spaces
# Multi-stage build: Python API + Next.js Frontend
# Runs on single port 7860 via nginx reverse proxy
# Target: https://huggingface.co/spaces/Praveit/praveit-cvd-risk

# ============================================
# Stage 1: Build Next.js Frontend
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files first for better caching
COPY clinical-dashboard/package*.json ./

# Install dependencies (including dev deps for build)
RUN npm ci

# Copy frontend source
COPY clinical-dashboard/ ./

# Build Next.js for production
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ============================================
# Stage 2: Python Base with System Dependencies
# ============================================
FROM python:3.11-slim AS python-base

# Install system dependencies: nginx, supervisord, node (for runtime), curl (health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    nodejs \
    npm \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (HF Spaces requirement)
RUN useradd -m -u 1000 user
USER user
WORKDIR /home/user/app

# ============================================
# Stage 3: Install Python Dependencies
# ============================================
FROM python-base AS python-deps

# Copy Python requirements from api/
COPY --chown=user api/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ./requirements.txt

# ============================================
# Stage 4: Final Runtime Image
# ============================================
FROM python-deps AS runtime

# Copy Python API code
COPY --chown=user api/ ./api/

# Copy built Next.js frontend (standalone output)
COPY --from=frontend-builder --chown=user /app/frontend/.next/standalone ./frontend/
COPY --from=frontend-builder --chown=user /app/frontend/public ./frontend/public/
COPY --from=frontend-builder --chown=user /app/frontend/.next/static ./frontend/.next/static/

# Copy nginx and supervisord configs
COPY --chown=user nginx.conf /etc/nginx/nginx.conf
COPY --chown=user supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create nginx dirs with proper permissions
USER root
RUN mkdir -p /var/cache/nginx /var/run/nginx /var/log/nginx \
    && chown -R user:user /var/cache/nginx /var/run/nginx /var/log/nginx \
    && chmod 755 /var/run/nginx
USER user

# Expose port 7860 (HF Spaces requirement)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Start supervisord (manages nginx + FastAPI + Next.js)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]