FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    default-libmysqlclient-dev \
    pkg-config \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Collect static files (will be done at runtime for production)
# This allows environment variables to be set properly
# RUN python manage.py collectstatic --noinput || true

# Copy startup script
COPY render-start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Use startup script as entrypoint
ENTRYPOINT ["/app/start.sh"]

# Default command (can be overridden in render.yaml or Render dashboard)
CMD ["gunicorn", "airbnb_clone.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
