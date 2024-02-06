# Use an official Python runtime with NVIDIA CUDA support
FROM nvidia/cuda:11.2.2-cudnn8-runtime-ubuntu20.04

WORKDIR /app

# Copy your application files
COPY . /app

# Install Python and FastAPI dependencies
RUN apt-get update && apt-get install -y python3-pip && \
    pip3 install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD uvicorn main:app --port=${PORT:-8000} --host=0.0.0.0
