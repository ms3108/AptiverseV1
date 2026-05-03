FROM python:3.11-slim

WORKDIR /app

# No system dependencies needed - psycopg2-binary bundles libpq,
# all pip packages ship prebuilt wheels (no gcc required)

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
