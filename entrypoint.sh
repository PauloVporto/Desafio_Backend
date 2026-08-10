#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py collectstatic --noinput >/dev/null 2>&1 || true

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ] && [ -n "${DJANGO_SUPERUSER_PASSWORD:-}" ]; then
  python manage.py shell <<'PY'
import os
from users.models import User

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

if username and password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password, email=email)
PY
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
