# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- `pytest.ini` and `conftest.py` with factory-boy factories and fixtures
- Test suite for all seven service layers (107 tests total):
  accounts (14), institutions (10), students (15), trainers (14),
  courses (12), classes (20), grades (22)
- Django admin registration for all models with list display, filters,
  search, fieldsets and inline enrollment view inside ClassAdmin

### Fixed

- `core/settings/development.py`: replaced PostgreSQL with SQLite for local
  development to avoid `psycopg2` Unicode errors on Windows paths with spaces
  or non-ASCII characters
- `core/settings/base.py`: added `encoding='utf-8'` to `load_dotenv()` call
  for consistent behaviour on Windows
- `apps/institutions/models.py`: implemented `Institution` model (was empty),
  unblocking all FK references across the project
- `apps/institutions/serializers.py`, `services.py`, `views.py`, `urls.py`:
  implemented all institution app files (were empty)
- `apps/accounts/views.py`: implemented auth views (login, logout, me,
  change-password)
- `apps/accounts/urls.py`: implemented URL routes for auth endpoints
- `apps/students/urls.py`: implemented URL routes
- `apps/trainers/urls.py`: implemented URL routes
- `apps/students/serializers.py`: implemented all student serializers
  including `StudentSummarySerializer` required by classes app
- `apps/trainers/serializers.py`: implemented all trainer serializers
  including `TrainerSummarySerializer` required by classes app

### Planned

- Automated test suite (pytest + factory-boy) for all backend services
- End-to-end tests for critical UI flows
- Rate limiting on authentication endpoints
- Email notifications for enrollment and grade events
- Export grade reports to PDF

---

## [0.2.0] — 2026-03-09

### Added — Backend

- `accounts/services.py`: `UserService` with full user lifecycle management (create, update, deactivate, change password, list)
- `institutions/management/commands/create_institution.py`: Django management command replacing the root-level bootstrap script; supports interactive and non-interactive (`--flag`) modes; wraps creation in `transaction.atomic()`
- `core/pagination.py`: `StandardResultsPagination` with extended response envelope (`count`, `pages`, `page`, `next`, `previous`, `results`)
- `core/mixins.py`: `PaginatedListMixin` exposing `self.paginate()` for use in `APIView` subclasses
- Pagination applied to all list endpoints across all seven apps

### Fixed — Backend

- `accounts/models.py`: removed conflicting `unique=True` on `email` field that overrode the compound `UniqueConstraint(["institution", "email"])`, which broke multi-tenant email isolation
- `students/services.py`, `trainers/services.py`, `courses/services.py`: replaced `|` queryset union with `Q()` objects to eliminate duplicate results on OR searches
- `classes/services.py`: corrected inverted guard logic in `update_class` — closed classes now block all mutations unconditionally
- `grades/services.py`: `get_grades_for_student` now includes `completed` enrollments, not only `active`, so historical grades are visible to students
- `core/urls.py`: wrapped `debug_toolbar` import in `try/except ImportError` to prevent crash when the package is absent in production

### Added — Frontend

- Complete frontend application (8 pages, vanilla HTML/CSS/JS)
- `js/api.js`: central API client with Bearer token injection, silent JWT refresh on 401, normalised error objects
- `js/api.mock.js`: drop-in mock layer with realistic fixture data for frontend development without the backend
- `js/layout.js`: shared layout module (nav rendering by role, breadcrumbs, auth guard, mobile sidebar)
- `css/global.css`: full design system (tokens, reset, typography, buttons, forms, badges, cards, tables, modals, toasts, skeleton loaders)
- `css/layout.css`: app shell layout (sidebar, topbar, content area, pagination, responsive breakpoints)
- `pages/login.html`: two-panel authentication page with inline validation, password toggle, loading state
- `pages/dashboard.html`: role-based dashboard with real API data, skeleton loading, `Promise.allSettled` for parallel requests
- `pages/students.html`: full CRUD with paginated table, debounced search, filter pills, slide-in detail panel, create/edit modal
- `pages/trainers.html`: full CRUD matching students pattern; detail panel with Profile and Classes tabs (lazy-loaded)
- `pages/courses.html`: card grid with list-view toggle; course code immutable after creation; classes sub-resource tab
- `pages/classes.html`: table for admin/trainer, enrollment card grid for students; class lifecycle actions (close, delete); live student enrol search with dropdown
- `pages/grades.html`: grade report table with clickable grade pills and popover for admin/trainer; animated grade bars by class for students

---

## [0.1.0] — 2024-12-01

### Added — Backend

- Initial Django 5.0 project with modular app structure
- Three-tier settings split: `base`, `development`, `production`
- `core/permissions.py`: `IsAdminRole`, `IsTrainerRole`, `IsStudentRole`, `IsInstitutionMember`, `IsOwnerTrainer`
- `core/exceptions.py`: global exception handler returning `{error, status_code, detail}` envelope
- `apps/accounts`: custom `User` model (UUID PK, role choices, institution FK, JWT serializers with role in payload)
- `apps/institutions`: `Institution` model as multi-tenant root entity
- `apps/students`: `Student` model with institution isolation and unique student code per institution
- `apps/trainers`: `Trainer` model with optional `User` link
- `apps/courses`: `Course` model with unique code per institution
- `apps/classes`: `Class` and `Enrollment` models with status state machines
- `apps/grades`: `Grade` model with assessment types, value/max_value validation, unique constraint per enrollment and type
- Docker Compose stack: PostgreSQL 16, Django/Gunicorn, Nginx
- `.env.example` documenting all required environment variables
- `API_REFERENCE.md` documenting all endpoints

---

[Unreleased]: https://github.com/your-org/academico/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/your-org/academico/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/your-org/academico/releases/tag/v0.1.0
