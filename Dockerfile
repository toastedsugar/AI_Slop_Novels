# Use lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency file first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variable so Python sees src/
ENV PYTHONPATH=/app/src

# Default command (can override in docker-compose)
CMD ["python", "scripts/run_generation.py"]