# Dockerfile for Render
# Multi-stage build: Python API + Next.js Frontend
# Runs on single port via nginx reverse proxy

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

# Install system dependencies: nginx, supervisord, nodejs, npm, curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx \
    supervisor \
    nodejs \
    npm \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create required directories
RUN mkdir -p /var/cache/nginx /var/run/nginx /var/log/nginx /var/log/supervisor /var/run/supervisor

# Create www-data user for nginx (already exists in debian)
# Ensure nginx can run

# ============================================
# Stage 3: Install Python Dependencies (global)
# ============================================
FROM python-base AS python-deps

# Copy Python requirements
COPY api/requirements.txt ./requirements.txt

# Install Python dependencies globally
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r ./requirements.txt

# ============================================
# Stage 4: Final Runtime Image
# ============================================
FROM python-deps AS runtime

# Ensure standard binary paths are available in PATH
ENV PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${PATH}"

# Debug: Verify nginx is actually in the final image
RUN which nginx && nginx -v

# Create non-root user
RUN useradd -m -u 1000 user

# Copy Python API code
COPY --chown=user api/ /home/user/app/api/

# Copy built Next.js frontend (standalone output)
COPY --from=frontend-builder --chown=user /app/frontend/.next/standalone /home/user/app/frontend/
COPY --from=frontend-builder --chown=user /app/frontend/.next/static /home/user/app/frontend/.next/static/
COPY --from=frontend-builder --chown=user /app/frontend/public /home/user/app/frontend/public/

# Copy nginx and supervisord configs
COPY nginx.conf /etc/nginx/nginx.conf
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Fix permissions
RUN chown -R user:user /home/user/app /var/cache/nginx /var/run/nginx /var/log/nginx /var/log/supervisor /var/run/supervisor

# Ensure nginx can write pid file
RUN touch /var/run/nginx/nginx.pid && chown user:user /var/run/nginx/nginx.pid

WORKDIR /home/user/app
USER user

# Expose port (Render assigns via $PORT env var)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Start supervisord (manages nginx + FastAPI + Next.js)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]