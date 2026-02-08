import os
from django.apps import AppConfig


def create_superuser_from_env():
    """Create a superuser from env vars (e.g. on Azure) when none exist."""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')
        if username and password and not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email or '', password=password)
    except Exception:
        pass


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        create_superuser_from_env()
