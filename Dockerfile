# Build stage
FROM ubuntu:22.04 as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim as runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the project files
COPY . .

# Create results directory and make script executable
RUN mkdir -p results/figures results/data results/logs && \
    chmod +x run_bb84.sh

# Set environment variables
ENV PYTHONPATH=/app/src
ENV MPLBACKEND=Agg

# Default command
CMD ["python", "experiments/demo.py"]
