# KanMind Backend

A Django REST Framework-based backend for KanMind, a collaborative Kanban board management application.

## Overview

KanMind Backend provides a robust API for managing boards, tasks, and user authentication. It enables teams to collaborate on projects using a Kanban workflow with task tracking, prioritization, and team member management.

## Features

- **User Authentication**: Token-based authentication with custom user model
- **Board Management**: Create, manage, and share boards with team members
- **Task Management**: Create, update, and track tasks across different workflow stages
- **Team Collaboration**: Add members to boards and manage permissions
- **Priority & Status Tracking**: Track task progress with status and priority levels
- **CORS Support**: Seamless integration with frontend applications

## Tech Stack

- **Framework**: Django 5.2.7
- **API**: Django REST Framework 3.16.1
- **Database**: SQLite (default, easily configurable)
- **Authentication**: Token-based via DRF
- **CORS**: django-cors-headers 4.9.0
- **Python**: 3.13+

## Project Structure

```
backend/
├── auth_app/               # Authentication & User management
│   ├── api/
│   │   ├── views.py       # Auth endpoints
│   │   ├── serializers.py # User serialization
│   │   ├── permissions.py # Custom permissions
│   │   └── urls.py        # Auth routes
│   ├── models.py          # Custom User model
│   └── authentication.py   # Auth logic
├── boards_app/            # Board & Task management
│   ├── api/
│   │   ├── views.py       # Board & Task endpoints
│   │   ├── serializers.py # Board/Task serialization
│   │   ├── permissions.py # Custom permissions
│   │   └── urls.py        # Board/Task routes
│   └── models.py          # Board & Task models
├── core/                  # Django project settings
│   ├── settings.py        # Project configuration
│   ├── urls.py            # Root URL configuration
│   ├── asgi.py           # ASGI config
│   └── wsgi.py           # WSGI config
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## Installation

### Prerequisites

- Python 3.13+
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project.KanMind-main/backend
   ```

2. **Create and activate virtual environment** (if not already done)
   ```bash
   python3 -m venv env
   source env/bin/activate  # On macOS/Linux
   # or
   env\Scripts\activate     # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file in the backend directory:
   ```
   DJANGO_SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (optional, for admin access)
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication (`/api/auth/`)
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Authenticate user and receive token
- `POST /api/auth/logout` - Logout user

### Boards (`/api/boards/`)
- `GET /api/boards/` - List all boards for user
- `POST /api/boards/` - Create new board
- `GET /api/boards/{id}/` - Get board details
- `PUT /api/boards/{id}/` - Update board
- `DELETE /api/boards/{id}/` - Delete board

### Tasks
- `GET /api/boards/{board_id}/tasks/` - List tasks for board
- `POST /api/boards/{board_id}/tasks/` - Create new task
- `GET /api/tasks/{id}/` - Get task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task

## Data Models

### User Model
```python
class User(AbstractUser):
    email: str          # Unique email
    fullname: str       # User's full name
    username: str       # Django username field
```

### Board Model
```python
class Board:
    title: str                    # Board name
    owner: User                   # Board creator
    members: List[User]          # Team members
    created_at: datetime          # Creation timestamp
    updated_at: datetime          # Last update timestamp
```

### Task Model
```python
class Task:
    board: Board                  # Associated board
    title: str                    # Task name
    description: str              # Task details
    status: str                   # 'to-do', 'in-progress', 'review', 'done'
    priority: str                 # 'low', 'medium', 'high'
    assigned_to: User            # Task assignee
    created_at: datetime          # Creation timestamp
    updated_at: datetime          # Last update timestamp
```

## Development

### Running Tests
```bash
python manage.py test
```

### Django Admin
Access the Django admin panel at `http://localhost:8000/admin/`
(Requires superuser account)

### Database Management

View current migrations:
```bash
python manage.py showmigrations
```

Create new migrations after model changes:
```bash
python manage.py makemigrations
```

Apply migrations:
```bash
python manage.py migrate
```

Reset database (development only):
```bash
python manage.py flush
```

## Configuration

### CORS Settings
CORS is enabled for frontend integration. Configure allowed origins in `core/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
]
```

### Authentication
Token-based authentication is configured. Include token in request headers:
```
Authorization: Token <your-token-here>
```

## Environment Variables

Configure these in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Django secret key | unsafe-default-key |
| `DEBUG` | Debug mode | True |
| `ALLOWED_HOSTS` | Allowed host domains | [] |

## Deployment

### Production Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Set strong `DJANGO_SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Use production database (PostgreSQL recommended)
- [ ] Set up HTTPS/SSL
- [ ] Configure static files serving
- [ ] Set up logging
- [ ] Configure CORS for production domains

### Using Gunicorn

```bash
pip install gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

## Troubleshooting

### Database Locked Error
```bash
rm db.sqlite3
python manage.py migrate
```

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## License

See LICENSE.md in the root directory

## Support

For issues and questions, please open an issue in the repository.

## API Documentation

Detailed API documentation is available in the project's frontend integration guide.

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Maintainer**: KanMind Development Team
