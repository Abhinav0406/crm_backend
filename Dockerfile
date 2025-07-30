FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make build script executable
RUN chmod +x build.sh

# Create necessary directories
RUN mkdir -p /app/media /app/staticfiles /app/logs

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Django application..."\n\
echo "📊 Running migrations..."\n\
python manage.py migrate --noinput\n\
echo "👤 Creating admin user..."\n\
python manage.py create_admin\n\
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then\n\
    echo "🔑 Creating superuser..."\n\
    python manage.py shell << EOF\n\
from django.contrib.auth import get_user_model\n\
User = get_user_model()\n\
if not User.objects.filter(username="$DJANGO_SUPERUSER_USERNAME").exists():\n\
    User.objects.create_superuser("$DJANGO_SUPERUSER_USERNAME", "$DJANGO_SUPERUSER_EMAIL", "$DJANGO_SUPERUSER_PASSWORD")\n\
    print("Superuser created successfully")\n\
else:\n\
    print("Superuser already exists")\n\
EOF\n\
fi\n\
echo "🚀 Starting gunicorn..."\n\
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"] 