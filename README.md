# Productivity Tracker REST API

A simple REST-style API for managing tasks and habits. Create, read, update, and delete tasks (with due date, priority, status) and habits (with frequency, streak, and daily completion) via JSON over HTTP.

## Overview

This project provides a coursework-style REST API with two main resources: **Task** and **Habit**. All endpoints return JSON and use standard HTTP methods and status codes. The API is built with plain Django views (no Django REST Framework).

The API demonstrates REST principles including resource-based URLs, appropriate use of HTTP methods, request validation, and automated testing.

## Features

- **Tasks** — Full CRUD: title, description, due date, priority (`low` / `medium` / `high`), status (`not_started` / `in_progress` / `completed`).
- **Habits** — Full CRUD: name, frequency (`daily` / `weekly`), streak count, and `completed_today` flag.
- **RESTful design** — Resource-based URLs, appropriate use of GET, POST, PUT, DELETE.
- **Filtering** — List endpoints support optional query parameters (e.g. `status`, `priority` for tasks; `frequency`, `completed_today` for habits).
- **Validation** — Request body validation with clear error responses (400) and 404 for missing resources.
- **Django admin** — Task and Habit are registered for easy data management during development.

## Technology Stack

- **Python 3.10+**
- **Django 6.0.3**
- **SQLite** (default database)

## Project Structure

```text
CW1/
├── api/                          # Django application containing the API
│   ├── migrations/               # Database migration files
│   │   └── 0001_initial.py
│   ├── templates/admin/api/      # Custom admin templates
│   │   ├── change_form_with_cancel.html
│   │   └── submit_line.html
│   ├── admin.py                  # Admin configuration
│   ├── models.py                 # Task and Habit database models
│   ├── tests.py                  # Automated API tests
│   ├── urls.py                   # API route definitions
│   └── views.py                  # API request handlers
│
├── productivity_tracker/         # Django project configuration
│   ├── settings.py               # Project settings
│   ├── urls.py                   # Root URL configuration
│   ├── asgi.py                   # ASGI entry point
│   └── wsgi.py                   # WSGI entry point
│
├── manage.py                     # Django management script
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── api-documentation.pdf         # API documentation PDF
└── Web.pptx                      # Presentation slides

```

## Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd CW1
```

1. **Create a virtual environment**

```bash
python3 -m venv venv
```

1. **Activate the virtual environment**

```bash
source venv/bin/activate # On Windows: venv\Scripts\activate
```

1. **Install dependencies**

```bash
pip install -r requirements.txt
```

1. **Run migrations**

```bash
python manage.py migrate
```

1. **(Optional)** Create a superuser to use the Django admin:

```bash
python manage.py createsuperuser
```

## Running the Server

From the project root:

```bash
python manage.py runserver
```

The API is available at [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/).
The Django admin interface is available at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## Root Endpoint

The root endpoint `/` returns a simple JSON message confirming that the API is running.

The root endpoint confirms the API is running.

```text
GET /
Example response:
{
  "message": "Productivity Tracker API is running"
}
```

## API Endpoints Overview

The following endpoints are available under the `/api/` prefix:


| Method | Endpoint            | Description     |
| ------ | ------------------- | --------------- |
| GET    | `/api/tasks/`       | List all tasks  |
| GET    | `/api/tasks/{id}/`  | Get one task    |
| POST   | `/api/tasks/`       | Create a task   |
| PUT    | `/api/tasks/{id}/`  | Update a task   |
| DELETE | `/api/tasks/{id}/`  | Delete a task   |
| GET    | `/api/habits/`      | List all habits |
| GET    | `/api/habits/{id}/` | Get one habit   |
| POST   | `/api/habits/`      | Create a habit  |
| PUT    | `/api/habits/{id}/` | Update a habit  |
| DELETE | `/api/habits/{id}/` | Delete a habit  |


Send JSON in the request body for POST and PUT. Success responses use 200 (GET/PUT), 201 (POST), or 204 (DELETE). Errors return 400 (validation) or 404 (not found).

## Filtering Examples

List endpoints support optional query parameters to filter results:

**Tasks by status**

```text
GET /api/tasks/?status=completed
```

**Tasks by priority**

```text
GET /api/tasks/?priority=high
```

Valid values for **tasks**:

- `status`: `not_started`, `in_progress`, `completed`
- `priority`: `low`, `medium`, `high`

**Habits by frequency**

```text
GET /api/habits/?frequency=daily
```

**Habits by whether completed today**

```text
GET /api/habits/?completed_today=true
```

Valid values for **habits**:

- `frequency`: `daily`, `weekly`
- `completed_today`: `true`, `false`

## Example Response

**GET /api/tasks/**

Returns a JSON array of task objects. Example:

```json
[
  {
    "id": 1,
    "title": "COMP3011 CW",
    "description": "Complete the API documentation, the technical report, 
	            and the presentation slides",
    "due_date": "2025-03-13",
    "priority": "high",
    "status": "in_progress",
    "created_at": "2025-03-10T14:30:00Z"
  }
]
```

**GET /api/habits/**

Returns a JSON array of habit objects. Example:

```json
[
  {
    "id": 2,	  
    "name": "Gym workout",
    "frequency": "weekly",
    "streak": 5,
    "completed_today": true,
    "created_at": "2025-03-09T09:00:00Z"
  }
]
```

## Running Tests

From the project root:

```bash
python manage.py test
```

## API Documentation

The full API specification, including endpoints, request/response examples, and field descriptions, is available in **api_documentation.pdf** in the project root.

The documentation was written in Markdown and exported to PDF for submission.

## Presentation Slides

The presentation slides for the project can be found in **Web.pptx** in the project root of this repository.

## Author

Faris N. Alqawasmi
Student ID: 201766141
