# Deploying to Azure Web App

This guide walks you through deploying the Django Ranking application to Azure App Service (Web App).

## Prerequisites

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- An Azure subscription
- Git (for deployment)

## Option 1: Deploy via Azure Portal

### Step 1: Create a Web App in Azure Portal

1. Go to [Azure Portal](https://portal.azure.com) → **Create a resource** → **Web App**
2. Fill in:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or select existing
   - **Name**: e.g., `ranking-ganttguru`
   - **Publish**: Code
   - **Runtime stack**: Python 3.11 (or 3.12)
   - **Operating System**: Linux
   - **Region**: Your preferred region
3. Click **Review + create** → **Create**

### Step 2: Configure the Web App

1. Go to your Web App → **Configuration** → **General settings**
2. Set **Startup Command** to:
   ```
   gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 ranking_site.wsgi:application
   ```
3. Go to **Configuration** → **Application settings** and add:
   - `DJANGO_SECRET_KEY` - Generate a secure random key (e.g., use `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
   - `DJANGO_DEBUG` - `False`
   - `ALLOWED_HOSTS` - Your app URL, e.g., `ranking-ganttguru.azurewebsites.net`
   - `CSRF_TRUSTED_ORIGINS` - `https://ranking-ganttguru.azurewebsites.net` (replace with your app URL)
   - **To create an admin user (no SSH needed):** `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_PASSWORD`, `DJANGO_SUPERUSER_EMAIL` (optional). Save and Restart; the app creates this user on startup. Remove these vars after the first login for security.

### Step 3: Deploy from Local Git or GitHub

**Local Git deployment:**
1. Go to **Deployment Center** → Select **Local Git** or **GitHub**
2. Follow the prompts to connect your repository
3. Azure will auto-detect Python and run `pip install -r requirements.txt`
4. Ensure your project root (folder containing `manage.py`) is the deployment root

**Important:** If your project is in a subfolder (e.g., `ranking/`), configure the deployment path:
- In **Configuration** → **General settings**, set **Startup Command** to use the correct path:
  ```
  cd /home/site/wwwroot && python manage.py collectstatic --noinput && gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 ranking_site.wsgi:application
  ```

## Option 2: Deploy via Azure CLI

```bash
# Login to Azure
az login

# Create resource group
az group create --name ranking-rg --location eastus

# Create App Service plan (B1 is the cheapest paid tier)
az appservice plan create --name ranking-plan --resource-group ranking-rg --sku B1 --is-linux

# Create Web App with Python 3.11 runtime
az webapp create --resource-group ranking-rg --plan ranking-plan --name ranking-ganttguru --runtime "PYTHON:3.11"

# Configure startup command
az webapp config set --resource-group ranking-rg --name ranking-ganttguru --startup-file "gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 2 ranking_site.wsgi:application"

# Set environment variables
az webapp config appsettings set --resource-group ranking-rg --name ranking-ganttguru --settings \
  DJANGO_SECRET_KEY="your-secret-key-here" \
  DJANGO_DEBUG="False" \
  ALLOWED_HOSTS="ranking-ganttguru.azurewebsites.net" \
  CSRF_TRUSTED_ORIGINS="https://ranking-ganttguru.azurewebsites.net"

# Deploy from local directory (from the ranking/ folder containing manage.py)
az webapp up --resource-group ranking-rg --name ranking-ganttguru --runtime "PYTHON:3.11"
```

## Project Structure for Deployment

Ensure the deployment root contains:
- `manage.py`
- `requirements.txt`
- `ranking_site/` (settings, urls, wsgi.py)
- `core/` app
- `templates/`
- `static/`

If your repo has a nested structure (`ranking/ranking/`), either:
- Deploy from the inner `ranking/` folder as root, or
- Configure Azure to use the subfolder (see [Azure docs](https://docs.microsoft.com/en-us/azure/app-service/configure-language-python))

## Post-Deployment: Run Migrations

After first deployment, run migrations via Azure CLI or Kudu console:

```bash
az webapp ssh --resource-group ranking-rg --name ranking-ganttguru
# Then in the SSH session:
cd /home/site/wwwroot
python manage.py migrate
python manage.py createsuperuser
exit
```

Or use the **SSH** blade in Azure Portal → **Advanced Tools** → **SSH**.

Alternatively, use the superuser env vars (DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD) in Application settings and Restart the app—no SSH needed.

## Database Note

This app uses **SQLite** by default. SQLite works on Azure Web App but has limitations:
- Data may be lost on app restart or scaling
- Not suitable for production with multiple instances

For production, consider:
- **Azure Database for PostgreSQL** or **MySQL**
- Update `DATABASES` in `settings.py` to use the cloud database connection string
- Set the connection string in Application settings (e.g., `DATABASE_URL`)

## Troubleshooting

- **502 Bad Gateway**: Check startup command and logs (Azure Portal → Log stream)
- **Static files not loading**: Ensure `collectstatic` runs; WhiteNoise serves static files
- **CSRF errors**: Add your Azure URL to `CSRF_TRUSTED_ORIGINS`
- **Module not found**: Verify `requirements.txt` includes all dependencies and deployment root is correct
