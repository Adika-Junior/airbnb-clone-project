#!/bin/bash
# Startup script for Render deployment
# This script runs migrations and collects static files before starting the app

set -e

echo "🚀 Starting Airbnb Clone application on Render..."

# Wait for database to be ready (Render handles this, but good to have)
echo "⏳ Waiting for database connection..."
python << END
import sys
import time
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airbnb_clone.settings')
django.setup()
from django.db import connection
max_attempts = 30
for i in range(max_attempts):
    try:
        connection.ensure_connection()
        print("✅ Database connection successful!")
        break
    except Exception as e:
        if i == max_attempts - 1:
            print(f"❌ Database connection failed after {max_attempts} attempts")
            sys.exit(1)
        print(f"⏳ Attempt {i+1}/{max_attempts}: Waiting for database...")
        time.sleep(2)
END

# Run migrations
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (optional - can be done via Django admin)
# Uncomment if you want to auto-create a superuser
# echo "👤 Creating superuser (if needed)..."
# python manage.py shell << END
# from apps.messaging.models import User
# if not User.objects.filter(is_superuser=True).exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'changeme')
#     print("Superuser created: admin/changeme")
# END

echo "✅ Startup complete! Starting application server..."

# Execute the command passed as arguments
exec "$@"
