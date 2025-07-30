#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "🚀 Starting build process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Force migrations if environment variable is set
if [ "$FORCE_MIGRATE" = "true" ]; then
    echo "🔄 Force migrating database..."
    python manage.py migrate --run-syncdb
else
    echo "🔄 Running migrations..."
    # Make migrations for all apps
    python manage.py makemigrations users --noinput || true
    python manage.py makemigrations clients --noinput || true
    python manage.py makemigrations stores --noinput || true
    python manage.py makemigrations sales --noinput || true
    python manage.py makemigrations products --noinput || true
    python manage.py makemigrations integrations --noinput || true
    python manage.py makemigrations analytics --noinput || true
    python manage.py makemigrations automation --noinput || true
    python manage.py makemigrations tasks --noinput || true
    python manage.py makemigrations escalation --noinput || true
    python manage.py makemigrations feedback --noinput || true
    python manage.py makemigrations announcements --noinput || true
    python manage.py makemigrations marketing --noinput || true
    python manage.py makemigrations support --noinput || true
    python manage.py makemigrations telecalling --noinput || true
    python manage.py makemigrations tenants --noinput || true

    # Apply all migrations
    echo "📊 Applying migrations..."
    python manage.py migrate --noinput
fi

# Create admin user using management command
echo "👤 Creating admin user..."
python manage.py create_admin

# Also create superuser if environment variables are set
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "🔑 Creating superuser..."
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF
fi

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "✅ Build process completed!"