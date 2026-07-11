web: gunicorn grenadye.wsgi --workers 2 --bind 0.0.0.0:$PORT --log-file -
release: python manage.py migrate --noinput
