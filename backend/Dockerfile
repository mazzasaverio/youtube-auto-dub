# Use an official Python runtime with NVIDIA CUDA support
FROM python:3.9-slim


WORKDIR /app

# Copy your application files
COPY . /app

# Install Python and FastAPI dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD uvicorn main:app --port=${PORT:-8080} --host=0.0.0.0
