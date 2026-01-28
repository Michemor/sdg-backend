#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Create initial superuser (admin/admin123) if it doesn't exist
echo "Creating default superuser..."
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('Superuser created') if not User.objects.filter(username='admin').exists() and User.objects.create_superuser('admin', 'admin@example.com', 'admin123') else print('Superuser already exists')"

