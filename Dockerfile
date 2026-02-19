# ─── Agentic Game Builder — Dockerfile ───────────────────────────────────────
# Python 3.11 slim base for minimal image size
FROM python:3.11-slim

# Metadata
LABEL maintainer="Agentic Game Builder"
LABEL description="CrewAI + Gemini powered game generation agent"

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create output directory with proper permissions
RUN mkdir -p generated_game && chmod 777 generated_game

# Environment variables (override at runtime)
# Set your Gemini API key when running:
# docker run -e GEMINI_API_KEY=your_key_here ...
ENV GEMINI_API_KEY=""
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Volume mount point for extracting generated game files
VOLUME ["/app/generated_game"]

# Run the agent (interactive mode required for user Q&A)
CMD ["python", "main.py"]
