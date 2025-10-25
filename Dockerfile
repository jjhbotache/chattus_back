# Use an official lightweight Python image
FROM python:3.11-slim

# Do not write .pyc files and make stdout/stderr unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required to build some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user and use it
RUN useradd -m chattususer && chown -R chattususer /app
USER chattususer

# Expose the port FastAPI uses by default
EXPOSE 8000

CMD ["fastapi", "run", "main:app", "--port", "8000"]
