# GitHub Actions → Azure Web App Setup

## Required GitHub Secrets

Add these secrets in **GitHub repo** → **Settings** → **Secrets and variables** → **Actions**:

| Secret Name | Description |
|-------------|-------------|
| `AZURE_WEBAPP_NAME` | Your Azure Web App name (e.g., `ranking-ganttguru`) |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | Download from Azure Portal (see below) |

## How to get the Publish Profile

1. Go to [Azure Portal](https://portal.azure.com) → Your Web App
2. Click **Get publish profile** (top menu)
3. Save the downloaded `.PublishSettings` file
4. Open it in a text editor and copy the **entire** contents
5. In GitHub → **Settings** → **Secrets** → **New repository secret**
6. Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
7. Value: Paste the full publish profile content

## Azure Web App Configuration

In **Configuration** → **General settings**, set **Startup Command**:

```
python manage.py collectstatic --noinput && gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 ranking_site.wsgi:application
```

In **Configuration** → **Application settings**, add:

- `DJANGO_SECRET_KEY` – secure random string
- `DJANGO_DEBUG` – `False`
- `ALLOWED_HOSTS` – `your-app.azurewebsites.net`
- `CSRF_TRUSTED_ORIGINS` – `https://your-app.azurewebsites.net`

## Important: Remove .venv from Git

If `.venv` was previously committed, remove it to fix build failures:

```bash
git rm -r --cached .venv
git commit -m "Remove .venv from repository"
git push
```
