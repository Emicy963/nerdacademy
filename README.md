# Matrika

Academic management platform for technical training centres.
Multi-tenant SaaS built with Django REST Framework and vanilla JavaScript.

---

## Overview

Matrika provides training institutions with a centralised system to manage
students, trainers, courses, classes, enrolments and grade assessments.
Each institution operates in complete data isolation. Three roles —
administrator, trainer and student — have distinct interfaces and permissions.

Built for the Angolan market: Portuguese by default, resilient to poor
connectivity (offline detection, request timeouts, service worker caching),
and payable via bank transfer or Multicaixa.

## Repository structure

```
matrika/
├── backend/          Django REST API
├── frontend/         Vanilla HTML/CSS/JS client
├── docs/
│   ├── branding/     MATRIKA_BRAND.md
│   └── marketing/    CINFOTEC_PILOT_PITCH.md
├── CHANGELOG.md
├── PLATFORM_OVERVIEW.md
└── .gitignore
```

## Technology stack

| Layer     | Technology                                          |
|-----------|-----------------------------------------------------|
| Backend   | Python 3.13, Django 5.0, Django REST Framework 3.15 |
| Auth      | JWT via djangorestframework-simplejwt 5.3           |
| Database  | PostgreSQL 16 (dev: SQLite)                         |
| Frontend  | HTML5, CSS3 (no framework), ES6 modules             |
| Deploy    | Backend: Railway / any Linux host                   |
|           | Frontend: Vercel                                    |

## Quick start

**Prerequisites:** Python 3.13+ and PostgreSQL 16+ (or use SQLite for dev).

```bash
git clone https://github.com/Emicy963/matrika.git
cd matrika

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements/development.txt
cp .env.example .env        # edit DB credentials
python manage.py migrate
python manage.py runserver

# Frontend (separate terminal)
cd frontend
python -m http.server 3000
# Open http://localhost:3000/pages/login.html
```

For self-service institution registration, open `http://localhost:3000/pages/register.html`.
For development without the backend, see the mock API instructions in `frontend/README.md`.

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

| Document                              | Location                                                             |
|---------------------------------------|----------------------------------------------------------------------|
| Platform technical overview           | [PLATFORM_OVERVIEW.md](PLATFORM_OVERVIEW.md)                         |
| Brand identity guide                  | [docs/branding/MATRIKA_BRAND.md](docs/branding/MATRIKA_BRAND.md)     |
| Backend setup and architecture        | [backend/README.md](backend/README.md)                               |
| Backend technical reference           | [backend/TECHNICAL.md](backend/TECHNICAL.md)                         |
| API endpoint reference                | [backend/API_REFERENCE.md](backend/API_REFERENCE.md)                 |
| Frontend setup and architecture       | [frontend/README.md](frontend/README.md)                             |
| Frontend technical reference          | [frontend/TECHNICAL.md](frontend/TECHNICAL.md)                       |
| Changelog                             | [CHANGELOG.md](CHANGELOG.md)                                         |

## License

Proprietary — Copyright (c) 2026 PyNerd. All rights reserved.
See `LICENSE` for details.
