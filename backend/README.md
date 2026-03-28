# Backend — Acadêmico API

Django REST Framework API for the Acadêmico academic management platform.

---

## Requirements

- Python 3.12+
- PostgreSQL 16+
- pip

## Local development setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements/development.txt

# Configure environment
cp .env.example .env
# Edit .env — set DB_NAME, DB_USER, DB_PASSWORD at minimum

# Run migrations
python manage.py migrate

# Create first institution and admin user
python manage.py create_institution

# Start development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api`.

## Docker setup

```bash
cd backend
cp .env.example .env
docker compose up -d
docker compose exec django python manage.py create_institution
```

## Environment variables

| Variable                  | Required | Default                     | Description                        |
|---------------------------|----------|-----------------------------|------------------------------------|
| `SECRET_KEY`              | Yes      | —                           | Django secret key                  |
| `DJANGO_SETTINGS_MODULE`  | No       | `core.settings.development` | Settings module                    |
| `DB_NAME`                 | Yes      | `academico_db`              | PostgreSQL database name           |
| `DB_USER`                 | Yes      | `academico_user`            | PostgreSQL user                    |
| `DB_PASSWORD`             | Yes      | —                           | PostgreSQL password                |
| `DB_HOST`                 | No       | `localhost`                 | PostgreSQL host                    |
| `DB_PORT`                 | No       | `5432`                      | PostgreSQL port                    |
| `JWT_ACCESS_TOKEN_MINUTES`| No       | `60`                        | JWT access token lifetime          |
| `JWT_REFRESH_TOKEN_DAYS`  | No       | `7`                         | JWT refresh token lifetime         |
| `ALLOWED_HOSTS`           | Prod     | —                           | Comma-separated hostnames          |
| `CORS_ALLOWED_ORIGINS`    | Prod     | —                           | Comma-separated frontend origins   |

## Management commands

```bash
# Bootstrap: create institution + admin user (interactive)
python manage.py create_institution

# Non-interactive (for CI/scripts)
python manage.py create_institution \
  --name "My Institution" \
  --slug "my-institution" \
  --admin-email "admin@institution.ao" \
  --admin-password "securepassword"

# Standard Django commands
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
```

## Project structure

```
backend/
├── core/
│   ├── settings/
│   │   ├── base.py          Shared settings
│   │   ├── development.py   Dev overrides (debug toolbar, browsable API)
│   │   └── production.py    Production (HSTS, SSL redirect, manifested static)
│   ├── exceptions.py        Global exception handler
│   ├── mixins.py            PaginatedListMixin, InstitutionQuerysetMixin
│   ├── pagination.py        StandardResultsPagination
│   ├── permissions.py       IsAdminRole, IsTrainerRole, IsStudentRole, IsInstitutionMember
│   └── urls.py              Root URL configuration
├── apps/
│   ├── accounts/            User model, JWT auth, UserService
│   ├── institutions/        Institution model, management command
│   ├── students/            Student profiles and management
│   ├── trainers/            Trainer profiles and management
│   ├── courses/             Course catalogue
│   ├── classes/             Classes, enrolments, lifecycle
│   └── grades/              Grade assessment and reporting
├── requirements/
│   ├── base.txt             Production dependencies
│   ├── development.txt      Dev extras (pytest, factory-boy, debug toolbar)
│   └── production.txt       (inherits base)
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

## Running tests

```bash
# Install development dependencies
pip install -r requirements/development.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html
```

## API base URL

```
http://localhost:8000/api      (development)
https://api.yourdomain.ao/api  (production)
```

Authentication uses JWT Bearer tokens. See `API_REFERENCE.md` for the full
endpoint reference.

## Production deployment

1. Set `DJANGO_SETTINGS_MODULE=core.settings.production` in the environment.
2. Set all required environment variables (see table above).
3. Run `python manage.py migrate` before starting the application server.
4. Run `python manage.py collectstatic --noinput`.
5. The Docker Compose stack runs Gunicorn behind Nginx automatically.

## License

MIT — see root `LICENSE`.
