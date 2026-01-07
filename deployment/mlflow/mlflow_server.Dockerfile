FROM python:3.11-slim

# Install git and clean up apt lists to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    # Clean up
    apt-get purge -y --auto-remove && \
    rm -rf /var/lib/apt/lists/*
# Verify installation (optional)
RUN git --version

RUN pip install mlflow \
    boto3 \
    pymysql \
    cryptography

EXPOSE 5000

RUN mkdir -p /mlflow
WORKDIR /mlflow