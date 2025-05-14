# Build stage
FROM ubuntu:22.04 as builder

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install Python 3.11 and build dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    gcc \
    g++ \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set Python 3.11 as default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1

# Upgrade pip
RUN python3 -m pip install --upgrade pip setuptools wheel

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.11-slim as runtime

WORKDIR /app

# Copy installed packages from builder (matching Python versions)
COPY --from=builder /usr/local/lib/python3.11/dist-packages /usr/local/lib/python3.11/site-packages
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
