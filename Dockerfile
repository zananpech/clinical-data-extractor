# Use Astral's official uv image for installing dependencies
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

# Set the working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy only dependency files first to leverage Docker caching
COPY pyproject.toml uv.lock ./

# Install dependencies without installing the project itself
RUN uv sync --frozen --no-install-project

# Final runtime image (keep it small and clean)
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy source code and files
COPY main.py ./
COPY src/ ./src/

# Create empty directories for data mounting
RUN mkdir -p data/raw data/parsed data/output/audit data/output/db

# Put virtual environment bin path on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Set the default entrypoint to python main.py
ENTRYPOINT ["python", "main.py"]
