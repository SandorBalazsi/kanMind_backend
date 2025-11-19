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

Below are the current API routes generated from the project's URL and view configuration. All API paths are rooted under the project base, most board/task routes are prefixed with `/api/` (see `boards_app/api/urls.py`).

### Authentication (`/api/auth/`)
- `POST /api/auth/register/` - Register a new user (returns token + user info)
- `POST /api/auth/login/` - Authenticate user and receive token
- `POST /api/auth/logout/` - Logout user (requires auth)
- `GET  /api/auth/me/` - Get current authenticated user (requires auth)
- `GET  /api/auth/email-check/?email=<email>` - Check if an email exists (public)

Notes: these endpoints are defined in `auth_app/api/urls.py` and implemented in `auth_app/api/views.py`.

### Boards (`/api/boards/`)
- `GET    /api/boards/` - List boards accessible by the authenticated user (owner or member)
- `POST   /api/boards/` - Create a new board (owner is set to request user)
- `GET    /api/boards/{id}/` - Retrieve board details
- `PUT/PATCH /api/boards/{id}/` - Update board
- `DELETE /api/boards/{id}/` - Delete board
- `POST   /api/boards/{id}/add_member/` - Add a member to the board (body: `{ "member_id": <user_id> }`)
- `POST   /api/boards/{id}/remove_member/` - Remove a member from the board (body: `{ "member_id": <user_id> }`)

The board endpoints are provided by `BoardViewSet` (see `boards_app/api/views.py`). The `add_member` and `remove_member` endpoints are ViewSet actions.

### Tasks (`/api/tasks/`)
- `GET    /api/tasks/` - List tasks that belong to boards the user can access
- `POST   /api/tasks/` - Create a task. Request body must include `board` (board id) and may include `assignee_id` / `reviewer_id`. Example request body:

   ```json
   {
     "board": 15,
     "title": "Code-Review durchführen",
     "description": "Den neuen PR für das Feature X überprüfen",
     "status": "review",
     "priority": "medium",
     "assignee_id": 8,
     "reviewer_id": 8,
     "due_date": "2025-02-27"
   }
   ```

- `GET    /api/tasks/{id}/` - Retrieve task details
- `PUT/PATCH /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `GET    /api/tasks/assigned-to-me/` - List tasks where the authenticated user is the assignee
- `GET    /api/tasks/reviewing/` - List tasks where the authenticated user is the reviewer
- `POST   /api/tasks/boards/tasks/` - (helper action) alternative create endpoint that accepts board id in the body (this action exists on the TaskViewSet as `boards/tasks`)

Notes: Tasks are provided by `TaskViewSet` and registered on the router at `/api/tasks/` (see `boards_app/api/urls.py` and `boards_app/api/views.py`).

Permission and error behaviour (important):

- Boards: `GET /api/boards/{id}/` — returns `404 Not Found` if the board id does not exist. If the board exists but the authenticated user is not the owner or a member, the endpoint returns `403 Forbidden`.
- Creating tasks: `POST /api/tasks/` — if the `board` id does not exist the API returns `404 Not Found`; if the board exists but the authenticated user is not a member/owner the API returns `403 Forbidden`.
- Updating tasks: `PATCH /api/tasks/{id}/` — returns `404 Not Found` if the task id does not exist; if the task exists but the authenticated user is not the board owner/member, the API returns `403 Forbidden`.

### Comments (task-scoped)
Comments are managed per-task. The following endpoints are implemented using `CommentViewSet` and explicit URL patterns in `boards_app/api/urls.py`:

- `GET  /api/tasks/{task_id}/comments/` - List comments for a task
- `POST /api/tasks/{task_id}/comments/` - Create a comment for a task (body example: `{ "content": "Nice work" }`)
- `DELETE /api/tasks/{task_id}/comments/{comment_id}/` - Delete a comment (requires appropriate permission)

The TaskViewSet also exposes a `comments` action (`/api/tasks/{id}/comments/`) for GET/POST; additionally the separate `CommentViewSet` URL patterns are used to support comment-specific list/create/destroy routes using the `task_id` path parameter.

### Authentication header
All endpoints that require authentication use DRF token auth. Include the token header in requests:

```
Authorization: Token <your-token-here>
```

### Example: create a comment
Request:

```
POST /api/tasks/42/comments/
Authorization: Token <token>
Content-Type: application/json

{ "content": "Please review the edge-case handling." }
```

Response (201 Created):

```json
{
   "id": 7,
   "created_at": "2025-11-16T12:34:56Z",
   "author": "Test User 1",
   "content": "Please review the edge-case handling."
}
```


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


## Support

For issues and questions, please open an issue in the repository.

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Maintainer**: Sandor Balazsi