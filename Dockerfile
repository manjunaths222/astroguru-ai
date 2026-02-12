FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render will set PORT env var)
EXPOSE 8002

# Default command: start the server
# Render sets PORT environment variable automatically
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8002}"]

