# Acadêmico

Academic management platform for technical training centres.
Multi-tenant SaaS built with Django REST Framework and vanilla JavaScript.

---

## Overview

Acadêmico provides training institutions with a centralised system to manage
students, trainers, courses, classes, enrolments and grade assessments.
Each institution operates in complete data isolation. Three roles —
administrator, trainer and student — have distinct interfaces and permissions.

## Repository structure

```
academico/
├── backend/          Django REST API
├── frontend/         Vanilla HTML/CSS/JS client
├── CHANGELOG.md
├── LICENSE
└── .gitignore
```

## Technology stack

| Layer     | Technology                                          |
|-----------|-----------------------------------------------------|
| Backend   | Python 3.12, Django 5.0, Django REST Framework 3.15 |
| Auth      | JWT via djangorestframework-simplejwt 5.3           |
| Database  | PostgreSQL 16                                       |
| Frontend  | HTML5, CSS3 (no framework), ES6 modules             |
| Container | Docker + Docker Compose                             |
| Proxy     | Nginx (production)                                  |
| Deploy    | Backend: any Linux VPS / Docker host                |
|           | Frontend: Vercel                                    |

## Quick start

**Prerequisites:** Docker and Docker Compose installed.

```bash
git clone https://github.com/Emicy963/nerdacademic.git
cd nerdacademic

# Copy environment template
cp backend/.env.example backend/.env
# Edit backend/.env with your values

# Start all services
docker compose -f backend/docker-compose.yml up -d

# Create the first institution and admin user
docker compose -f backend/docker-compose.yml exec django \
  python manage.py create_institution

# The API is now available at http://localhost:8000/api
```

For local development without Docker, see `backend/README.md`.
For frontend development and mock mode, see `frontend/README.md`.

## Roles and access

| Action                         | Admin | Trainer | Student |
|--------------------------------|-------|---------|---------|
| Manage students                | Write | Read    | Self    |
| Manage trainers                | Write | Read    | —       |
| Manage courses                 | Write | Read    | Read    |
| Manage classes                 | Write | Read    | Self    |
| Manage enrolments              | Write | Read    | Self    |
| Launch and edit grades         | Write | Write*  | Read    |
| View grade reports             | Yes   | Own*    | Self    |

\* Trainers can only manage grades and view reports for classes assigned to them.

## Documentation

| Document                              | Location                                                |
|---------------------------------------|---------------------------------------------------------|
| Backend setup and architecture        | [backend/README.md](backend/README.md)                  |
| Backend technical reference           | [backend/TECHNICAL.md](backend/TECHNICAL.md)            |
| API endpoint reference                | [backend/API_REFERENCE.md](backend/API_REFERENCE.md)    |
| Frontend setup and architecture       | [frontend/README.md](frontend/README.md)                |
| Frontend technical reference          | [frontend/TECHNICAL.md](frontend/TECHNICAL.md)          |
| Changelog                             | [CHANGELOG.md](CHANGELOG.md)                            |

## License

MIT — see `LICENSE`.
