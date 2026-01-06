# Ranking Model Web Application

A Django-based web application that allows users to rank tasks within configurable stages. Administrators can manage stages and tasks through the Django admin interface, and users can log in to view stages and rank tasks accordingly.

## Features

- **User Authentication**: Secure login/logout functionality
- **Landing Page**: Displays all configured stages as cards with images and descriptions
- **Stage Pages**: 
  - Left sidebar menu showing all stages for easy navigation
  - Dynamic ranking system based on the number of active tasks
  - Each task can be ranked from 1 to N (where N = number of active tasks)
- **Admin Configuration**:
  - Full CRUD operations for stages (name, description, image URL, order)
  - Full CRUD operations for tasks (name, description, order, active status)
  - View user rankings
- **Dynamic Ranking**: Ranking options automatically adjust based on the number of active tasks in each stage

## Technologies Used

- **Python 3.11+**
- **Django 5.2.9**
- **Bootstrap 5.3.3** (via CDN)
- **SQLite** (default database)

## Project Structure

```
Ranking model/
├── core/                    # Main application
│   ├── models.py           # Stage, Task, TaskRanking models
│   ├── views.py            # LandingView, StageDetailView
│   ├── urls.py             # URL routing
│   ├── admin.py            # Django admin configuration
│   └── templatetags/       # Custom template filters
├── ranking_site/           # Django project settings
│   ├── settings.py         # Project configuration
│   └── urls.py             # Main URL configuration
├── templates/              # HTML templates
│   ├── core/
│   │   ├── base.html       # Base template with navbar
│   │   ├── landing.html    # Landing page with stage cards
│   │   └── stage_detail.html # Stage detail with ranking form
│   └── registration/
│       └── login.html      # Login page
├── static/                 # Static files
│   └── css/
│       └── styles.css      # Custom styles
├── manage.py               # Django management script
├── db.sqlite3              # SQLite database (created after migrations)
└── README.md               # This file
```

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Step 1: Navigate to Project Directory

```powershell
cd "C:\Users\HariharanRajan\OneDrive - APG eCommerce\Desktop\RAG\Ranking model"
```

### Step 2: Activate Virtual Environment

The virtual environment (`.venv`) is already created. Activate it:

**PowerShell:**
```powershell
.\.venv\Scripts\Activate.ps1
```

**Command Prompt:**
```cmd
.venv\Scripts\activate.bat
```

You should see `(.venv)` at the start of your command prompt.

### Step 3: Install Dependencies

Dependencies are already installed, but if you need to reinstall:

```powershell
pip install django
```

### Step 4: Run Database Migrations

```powershell
python manage.py migrate
```

This creates the necessary database tables.

### Step 5: Create Admin User

Create a superuser account to access the admin panel:

```powershell
python manage.py createsuperuser
```

Follow the prompts to set:
- Username
- Email (optional)
- Password (twice)

### Step 6: Start Development Server

```powershell
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## Usage Guide

### Admin Configuration

1. **Access Admin Panel**
   - Navigate to `http://127.0.0.1:8000/admin/`
   - Login with your superuser credentials

2. **Create Stages**
   - Go to **Core → Stages → Add Stage**
   - Fill in:
     - **Name**: Stage name (e.g., "Stage 1", "Stage 2")
     - **Description**: Optional description
     - **Image URL**: Optional image URL for the landing page card
     - **Order**: Display order (1, 2, 3, etc.)
   - Click **Save**
   - Repeat for all stages (up to 10 or more as needed)

3. **Create Tasks for Each Stage**
   - Go to **Core → Tasks → Add Task**
   - Fill in:
     - **Stage**: Select the stage this task belongs to
     - **Name**: Task name
     - **Description**: Optional task description
     - **Order**: Display order within the stage
     - **Is active**: Check this box to make the task visible for ranking
   - Click **Save**
   - Repeat for all tasks in each stage

4. **Managing Task Count**
   - To change the number of ranking options (1-N):
     - **Add more tasks**: Create new tasks and set `Is active = True`
     - **Remove tasks**: Set `Is active = False` for tasks you want to hide
   - The ranking dropdowns automatically adjust to show ranks 1 through N (where N = number of active tasks)

### User Experience

1. **Login**
   - Navigate to `http://127.0.0.1:8000/login/`
   - Enter username and password
   - Click **Login**

2. **View Landing Page**
   - After login, you'll see the landing page with all configured stages
   - Each stage is displayed as a card with:
     - Stage image (if configured)
     - Stage name
     - Stage description
     - "Go to Stage" button

3. **Rank Tasks in a Stage**
   - Click on any stage card or use the "Go to Stage" button
   - You'll see:
     - **Left sidebar**: List of all stages (current stage highlighted)
     - **Main content**: 
       - Stage name and description
       - Table of tasks with ranking dropdowns
   - Select a rank (1-N) for each task from the dropdown
   - **Important**: Each rank value must be unique (no duplicates)
   - Click **Save Rankings** to submit
   - If validation fails, errors will be displayed
   - Previously saved rankings are automatically loaded and pre-selected

4. **Navigate Between Stages**
   - Click any stage name in the left sidebar to switch stages
   - Your rankings are saved per stage and per user

## Models

### Stage
- `name`: Stage name
- `description`: Optional description
- `image_url`: Optional image URL for landing page
- `order`: Display order

### Task
- `stage`: Foreign key to Stage
- `name`: Task name
- `description`: Optional task description
- `order`: Display order within stage
- `is_active`: Boolean to show/hide task

### TaskRanking
- `user`: Foreign key to User
- `stage`: Foreign key to Stage
- `task`: Foreign key to Task
- `rank`: Ranking value (1-N)
- `created_at`: Timestamp when created
- `updated_at`: Timestamp when last updated

## Key Features Explained

### Dynamic Ranking System
- The ranking options (1-N) are automatically determined by the number of **active** tasks in each stage
- Example: If Stage 1 has 8 active tasks, users can only rank from 1-8
- Example: If Stage 2 has 10 active tasks, users can rank from 1-10
- This ensures rankings always match the available tasks

### Validation
- All tasks must be ranked (no empty selections)
- Each rank value must be unique (no duplicates)
- Rankings are validated on the server side before saving

### User-Specific Rankings
- Each user has their own set of rankings
- Rankings are saved per user, per stage, per task
- Users can update their rankings at any time

## Development

### Running Tests
```powershell
python manage.py test
```

### Creating New Migrations
After modifying models:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Collecting Static Files (for production)
```powershell
python manage.py collectstatic
```

## Troubleshooting

### Issue: "No stages configured yet"
- **Solution**: Log into the admin panel and create at least one stage

### Issue: "Please provide a unique rank for every task"
- **Solution**: Ensure every task has a rank selected and no two tasks have the same rank

### Issue: Virtual environment not activating
- **Solution**: Make sure you're in the project directory and the `.venv` folder exists

### Issue: Port 8000 already in use
- **Solution**: Use a different port: `python manage.py runserver 8001`

## Future Enhancements

Potential features that could be added:
- Summary/analytics view of rankings across users
- Export rankings to CSV/Excel
- Multiple ranking rounds per stage
- Custom admin UI for non-technical users
- User registration functionality
- Email notifications

## License

This project is for internal use.

## Support

For issues or questions, please contact the development team.

