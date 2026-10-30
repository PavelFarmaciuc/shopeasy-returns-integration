# Dockerfile – one image for all ShopEasy Python services (REST API, gRPC service, messaging)

# 1. Start from the official Python 3.13 image (small "slim" variant based on Debian Linux)
FROM python:3.13-slim

# 2. Python settings: print logs immediately, don't write .pyc cache files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 3. All following commands run in /app inside the image
WORKDIR /app

# 4. Install the libraries first (this layer is cached as long as requirements.txt doesn't change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy our code
COPY rest_api ./rest_api
COPY grpc_service ./grpc_service
COPY messaging ./messaging

# 6. Security: don't run as the all-powerful root user
RUN useradd --create-home appuser
USER appuser

# 7. Ports the services listen on (documentation; publishing happens with -p / compose)
EXPOSE 8000 50051

# 8. Default command: start the REST API (compose overrides this for the other services)
CMD ["python", "-m", "uvicorn", "rest_api.main:app", "--host", "0.0.0.0", "--port", "8000"]