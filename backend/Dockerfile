FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Create startup script
COPY <<EOF /app/start.sh
#!/bin/bash
set -e
echo "🌱 Running database migrations and seeding..."
python seed_data.py || echo "⚠️  Seeding skipped (may already be seeded)"
echo "🚀 Starting server..."
exec uvicorn main:app --host 0.0.0.0 --port 8000
EOF

RUN chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
