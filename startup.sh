#!/bin/bash
# Azure Web App startup script for Django
cd /home/site/wwwroot
python manage.py collectstatic --noinput
gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 ranking_site.wsgi:application
