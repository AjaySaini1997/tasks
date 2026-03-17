# Task Manager API

A production-ready RESTful API built with Django REST Framework, JWT Authentication, Swagger Docs, and full test coverage.

---

## Features

- Full CRUD for Tasks
- JWT Authentication (Register / Login / Logout)
- User Roles: Admin sees all tasks, regular users see only their own
- Pagination (10 tasks per page)
- Filtering by `completed`, `priority`, `title`
- Swagger UI + ReDoc documentation
- 15+ Unit Tests with coverage

---

## Tech Stack

| Tool | Purpose |
|------|---------|
| Django 4.2 | Web framework |
| Django REST Framework | API layer |
| SimpleJWT | JWT Authentication |
| drf-yasg | Swagger / ReDoc docs |
| django-filter | Query filtering |
| pytest-django | Testing |
| SQLite | Database (dev) |

---

## Setup Instructions

### 1. Clone the project
```bash
git clone https://github.com/yourname/task-manager-api.git
cd task-manager-api
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create superuser (admin)
```bash
python manage.py createsuperuser
```

### 6. Start server
```bash
python manage.py runserver
```

Server runs at: `http://127.0.0.1:8000`

---

## API Endpoints

### Auth Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/token/` | Login (get JWT tokens) | No |
| POST | `/api/auth/token/refresh/` | Refresh access token | No |
| GET | `/api/auth/profile/` | Get current user profile | Yes |
| POST | `/api/auth/logout/` | Logout (blacklist token) | Yes |

### Task Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/tasks/` | List all tasks | Yes |
| POST | `/api/tasks/` | Create a task | Yes |
| GET | `/api/tasks/{id}/` | Get task details | Yes |
| PUT | `/api/tasks/{id}/` | Update task | Yes (owner/admin) |
| PATCH | `/api/tasks/{id}/` | Partial update | Yes (owner/admin) |
| DELETE | `/api/tasks/{id}/` | Delete task | Yes (owner/admin) |

### Query Parameters (GET /api/tasks/)

| Param | Type | Example |
|-------|------|---------|
| `completed` | boolean | `?completed=true` |
| `priority` | string | `?priority=high` |
| `title` | string | `?title=meeting` |
| `page` | integer | `?page=2` |
| `ordering` | string | `?ordering=-created_at` |

---

## Example Requests & Responses

### Register
```
POST /api/auth/register/
{
  "username": "john",
  "email": "john@example.com",
  "password": "mypassword",
  "password2": "mypassword"
}

Response 201:
{
  "message": "User registered successfully.",
  "user": { "id": 1, "username": "john", "email": "john@example.com", "role": "user" },
  "tokens": { "access": "eyJ...", "refresh": "eyJ..." }
}
```

### Login
```
POST /api/auth/token/
{ "username": "john", "password": "mypassword" }

Response 200:
{ "access": "eyJ...", "refresh": "eyJ..." }
```

### Create Task
```
POST /api/tasks/
Authorization: Bearer <access_token>
{
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "priority": "medium"
}

Response 201:
{
  "id": 1, "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "completed": false, "priority": "medium",
  "owner": "john",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

## Documentation URLs

| URL | Tool |
|-----|------|
| `http://127.0.0.1:8000/swagger/` | Swagger UI |
| `http://127.0.0.1:8000/redoc/` | ReDoc |
| `http://127.0.0.1:8000/swagger.json` | Raw JSON schema |

---

## Running Tests

### Run all tests
```bash
python manage.py test
```

### Run with pytest
```bash
pytest
```

### Run with coverage report
```bash
coverage run -m pytest
coverage report
coverage html    # generates htmlcov/index.html
```

---

## Postman Collection

Import the Postman collection to test all endpoints:

**Postman Collection URL:**
`https://www.postman.com/collections/task-manager-api`

**Steps to use Postman:**
1. Open Postman → Import → Link
2. Paste: `http://127.0.0.1:8000/swagger.json`
3. Postman auto-imports all endpoints from Swagger

---

## User Roles

| Role | Permissions |
|------|------------|
| Regular User | Create, view, update, delete own tasks |
| Admin (is_staff) | View and manage ALL tasks |

---

## Project Structure

```
task_manager_api/
├── manage.py
├── requirements.txt
├── pytest.ini
├── README.md
├── task_manager/
│   ├── settings.py
│   └── urls.py
├── tasks/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── filters.py
│   ├── permissions.py
│   ├── admin.py
│   └── tests.py
└── users/
    ├── serializers.py
    ├── views.py
    └── urls.py
```
