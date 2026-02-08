# Finding Your Project on Azure Web App SSH

If `manage.py` is not at `/home/site/wwwroot`, find it with:

```bash
# List what's in wwwroot
ls -la /home/site/wwwroot

# Search for manage.py
find /home/site -name "manage.py" 2>/dev/null

# Common alternate paths (list them)
ls -la /home/site/repository 2>/dev/null
ls -la /home/site/wwwroot/*/ 2>/dev/null
```

Then `cd` to the directory that contains `manage.py` and run:

```bash
python manage.py migrate
python manage.py createsuperuser
exit
```

**Alternative (no SSH):** Use `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, and `DJANGO_SUPERUSER_EMAIL` in Azure Application settings, then Restart the app. The superuser is created on startup.
