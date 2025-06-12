FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app

# --- System dependencies ---
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-dev python-is-python3 python3-pip \
    build-essential cmake ninja-build git curl unzip \
    libgl1-mesa-glx libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# --- Install Python dependencies ---
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# --- Copy code, models, assets ---
COPY . .

# --- Build and install custom rasterizer ---
WORKDIR /app/hy3dgen/texgen/custom_rasterizer
RUN python3 setup.py bdist_wheel && pip install dist/custom_rasterizer*.whl

# --- Go back to app directory ---
WORKDIR /app

# --- Run your script on container start ---
CMD ["python3", "run_pipeline.py"]
