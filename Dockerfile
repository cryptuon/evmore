# syntax=docker/dockerfile:1.6

############################
# 1. Build Astro website (includes Vue islands)
############################
FROM node:20-alpine AS website-build
WORKDIR /build

# Install frontend deps (needed for tsconfig resolution via path alias)
COPY frontend/package.json frontend/package-lock.json* ./frontend/
RUN cd frontend && npm ci

# Copy frontend source (consumed by Astro via path alias)
COPY frontend/ ./frontend/

# Install website deps
COPY website/package.json website/package-lock.json* ./website/
WORKDIR /build/website
RUN npm ci

# Copy website source and build
COPY website/ ./
RUN npm run build

############################
# 2. Build Rust backend
############################
FROM rust:1.82-slim AS backend-build
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
        pkg-config libssl-dev ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY backend/Cargo.toml backend/Cargo.lock* ./
RUN mkdir -p src && echo "fn main() {}" > src/main.rs \
    && cargo build --release \
    && rm -rf src target/release/deps/evmore_dashboard*

COPY backend/ ./
RUN cargo build --release

############################
# 3. Runtime image
############################
FROM debian:bookworm-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r app && useradd -r -g app app

WORKDIR /app

COPY --from=backend-build /build/target/release/evmore-dashboard /app/evmore-dashboard
COPY --from=website-build /build/website/dist /app/public

ENV PORT=8080 \
    STATIC_DIR=/app/public \
    RUST_LOG=info

EXPOSE 8080
USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT}/api/health || exit 1

CMD ["/app/evmore-dashboard"]
