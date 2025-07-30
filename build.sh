#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Force migrations if environment variable is set
if [ "$FORCE_MIGRATE" = "true" ]; then
    echo "🔄 Force migrating database..."
    python manage.py migrate --run-syncdb
else
    # Make migrations for all apps
    python manage.py makemigrations users
    python manage.py makemigrations clients
    python manage.py makemigrations stores
    python manage.py makemigrations sales
    python manage.py makemigrations products
    python manage.py makemigrations integrations
    python manage.py makemigrations analytics
    python manage.py makemigrations automation
    python manage.py makemigrations tasks
    python manage.py makemigrations escalation
    python manage.py makemigrations feedback
    python manage.py makemigrations announcements
    python manage.py makemigrations marketing
    python manage.py makemigrations support
    python manage.py makemigrations telecalling
    python manage.py makemigrations tenants

    # Apply all migrations
    python manage.py migrate --noinput
fi

# Create admin user using management command
python manage.py create_admin

# Also create superuser if environment variables are set
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
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
python manage.py collectstatic --noinput