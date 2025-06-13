# Use official Python slim base image for small footprint
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (you can remove unused ones later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake ninja-build git curl unzip \
    libgl1-mesa-glx libglib2.0-0 python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Pre-copy only requirements to leverage Docker layer caching
COPY requirements.txt .

# Install Python packages (cached if requirements.txt doesn’t change)
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Now copy the actual codebase (slower step, done after installing packages)
COPY . .

# Build and install the custom rasterizer wheel
WORKDIR /app/hy3dgen/texgen/custom_rasterizer
RUN python setup.py bdist_wheel && pip install dist/*.whl

# Set working dir back to app
WORKDIR /app

# Run your main script
CMD ["python3", "-u", "rp_handler.py"]
