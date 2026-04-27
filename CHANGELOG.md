# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.4.6] — 2026-04-27

### Added

- Self-service institution registration:
  - `POST /api/institutions/register/` — public endpoint; atomically creates
    Institution + admin User + Membership inside `transaction.atomic()`,
    auto-derives a unique URL slug from the institution name, and returns JWT
    tokens so the new admin is immediately logged in
  - `InstitutionService.register()` — service method handling the full signup flow
  - `InstitutionRegistrationSerializer` — validates `institution_name`,
    `admin_name`, `email`, `password` (min 8 chars)
  - `register.html` — public sign-up page; two-panel layout matching login;
    lang switcher; password visibility toggle; on success stores session and
    redirects to the dashboard
  - `institutions.register()` added to `api.js`
  - `register.*` i18n keys added in PT and EN
  - 3 service-level tests: happy-path creation, slug deduplication on collision,
    duplicate-email guard
- Deploy infrastructure:
  - `backend/Dockerfile` updated to Python 3.13, `collectstatic` moved out of
    build layer to runtime
  - `backend/entrypoint.sh` — runs migrate, collectstatic, then Gunicorn at
    container start; respects `PORT` and `GUNICORN_WORKERS` env vars
  - `backend/core/settings/production.py` — WhiteNoise middleware injected,
    `dj-database-url` parses `DATABASE_URL` (Railway), `SECURE_SSL_REDIRECT`
    replaced with `SECURE_PROXY_SSL_HEADER` to avoid Railway redirect loops
  - `backend/requirements/production.txt` — added `whitenoise[brotli]==6.9.0`
    and `dj-database-url==2.3.0`
  - `backend/railway.toml` — Railway build/deploy config with health-check
  - `backend/nginx/nginx.conf` — Nginx reverse-proxy config for VPS deployments
  - `vercel.json` (project root) — Vercel config for static frontend; rewrites
    `/api/*` to the Railway backend URL (requires manual `REPLACE_WITH_RAILWAY_URL`)
  - `.github/workflows/ci.yml` — GitHub Actions CI: runs pytest on push/PR to
    main and develop using SQLite (development settings)
  - `GET /api/health/` — unauthenticated health-check endpoint returning
    `{"status": "ok"}` for Railway and uptime monitors

---

## [0.4.5] — 2026-04-27

### Added

- Reports page (`/pages/reports.html`) — read-only analytics view separate
  from grade management:
  - **Admin / Trainer view:** class selector → 4 summary stat cards
    (students, class average, highest, lowest) → Chart.js horizontal bar
    chart (average per student, colour-coded green/amber/red) → full grade
    table (one column per assessment type present in that class)
  - **Student view:** overall stats (classes enrolled, overall average) →
    Chart.js horizontal bar chart (average per class) → per-class grade
    cards with progress bars for each assessment type
  - Print button triggers `window.print()` with CSS print rules that hide
    nav and controls
  - Chart.js 4.4 loaded from CDN
- `icon-reports` (bar chart) and `icon-print` added to `icons.html`
- "Relatórios / Reports" nav item added to the Academic section (all roles)
- `nav.item.reports` and `report.*` i18n keys added in PT and EN

---

## [0.4.4] — 2026-04-27

### Added

- In-app notification system:
  - `Notification` model (`apps.notifications`) — UUID PK, user FK, type
    (enrollment / grade / system), title, message, is_read, created_at
  - `NotificationService` — `create`, `list_recent`, `unread_count`,
    `mark_read`, `mark_all_read`, `notify_enrollment`, `notify_grade`
  - Enrollment trigger: trainer is notified when a student is enrolled in
    one of their classes
  - Grade trigger: student is notified when a grade is submitted for their
    enrollment
  - `GET /api/notifications/` — returns `{ unread_count, results[] }`
  - `POST /api/notifications/<id>/read/` — mark single notification as read
  - `POST /api/notifications/read-all/` — mark all notifications as read
  - 7 service-level tests covering creation, ordering, scoping, unread count,
    and mark-read operations
- Frontend notification panel in the topbar:
  - Bell button gets a live unread-count badge
  - Dropdown panel renders recent notifications with human-readable timestamps
  - Polling every 60 seconds to refresh unread count
  - "Mark all as read" action inside the panel
  - `notifications` API object added to `api.js`
  - i18n keys for the panel added in PT and EN

---

## [0.4.3] — 2026-04-27

### Added

- Self-service password recovery flow:
  - `POST /api/auth/password-reset/` — accepts email, sends a reset link (always
    returns 200 to prevent email enumeration; silently skips placeholder addresses
    and inactive accounts)
  - `POST /api/auth/password-reset/confirm/` — validates Django's built-in
    `PasswordResetTokenGenerator` token, sets new password, clears
    `must_change_password`
  - `FRONTEND_URL` setting (reads from env, defaults to `http://127.0.0.1:3000`)
    used to build the reset link
  - `send_password_reset_link()` email function added to `emails.py`
  - `PasswordResetRequestSerializer` and `PasswordResetConfirmSerializer` added
  - 6 new service tests covering success, token invalidation, and edge cases
- `forgot-password.html` — email form; always shows success state after submit
- `reset-password.html` — new password form; reads `uid` and `token` from URL
  params; shows invalid-link state if params are missing or token is rejected
- Login page "Esqueceu a palavra-passe?" link now navigates to `forgot-password.html`
- `auth.requestPasswordReset()` and `auth.confirmPasswordReset()` added to `api.js`
- i18n keys for both new pages added in PT and EN

---

## [0.4.2] — 2026-04-27

### Added

- `GET /api/auth/me/` now also handles `PATCH` — authenticated users can update
  their own email; `full_name` remains read-only (managed exclusively by admins)
- `UserService.update_me(user, email)` — validates uniqueness excluding the
  current user, then persists the new email
- `UserUpdateMeSerializer` — single-field serializer accepting `email`
- Profile page (`/pages/profile.html`) — shows user info (name, code,
  institution, role, member since) and provides a form to update email;
  accessible from the sidebar user footer link for all roles
- `auth.updateMe(data)` added to `api.js`
- `sidebar__user-link` in `layout.js` — avatar and name in the sidebar footer
  are now a clickable link to the profile page; injected once by `renderUser()`
- i18n keys for the profile page added in both PT and EN locales

### Fixed

- `test_create_student_without_email` and `test_create_trainer_without_email`
  updated to reflect v0.4.1 behaviour: user account is always created, password
  is `pass123` when no email is provided

---

## [0.4.1] — 2026-04-27

### Added

- Internationalisation (i18n) system — PT and EN locales across the entire
  frontend; `i18n.js` exports `t(key)` for use in JS and drives `data-i18n`
  attribute rendering via `applyTranslations()`; locale persisted in
  `localStorage` under `academico_locale`
- Landing page (`index.html`) redesigned as a real public page with hero,
  feature cards, role showcase, and footer; supports PT/EN lang switcher
- Static pages: `about.html`, `contact.html`, `privacy.html`, `terms.html`;
  footer links on the landing page now point to these pages
- Code-based login: `POST /api/auth/login/` now accepts a student or trainer
  code (no `@` character) in the `email` field; `CustomTokenObtainPairSerializer`
  resolves the code to the corresponding user before simplejwt authentication
- Users without an email address now always get a user account on creation;
  placeholder email format `{code}@local.academico` is used internally and
  never exposed to the client; initial password is `pass123`
- Dashboard (`dashboard.html`) fully translated — all strings moved from
  hardcoded JS template literals to `t()` calls (admin, trainer, and student
  views)

### Changed

- `UserMeSerializer` masks placeholder emails: returns `""` when email ends
  with `@local.academico`
- Login input changed from `type="email"` to `type="text"` to accept both
  email addresses and alphanumeric codes
- `UserService.create_managed_user()` now accepts a `code` parameter; password
  strategy depends on whether a real email is provided

---

## [0.4.0] — 2026-04-21

### Added

- Auto-generation of student and trainer codes scoped to institution
  (`{PREFIX}{YEAR}{SEQ:04d}` — e.g. `CIN20260001`); `student_code` and
  `trainer_code` become optional on creation
- `institution_prefix` field on `Institution` (3-char, e.g. `CIN`)
  used as base for all code generation
- `must_change_password` flag on `User`; set to `True` on account creation
  via admin; login response includes the flag so the frontend can redirect
- Default password auto-generated with `secrets.token_urlsafe(8)` on
  student/trainer creation; returned once in the creation response
- `POST /api/students/{id}/reset-password/` — admin resets any student
  password and triggers `must_change_password`
- `POST /api/trainers/{id}/reset-password/` — same for trainers
- Welcome email sent on student/trainer creation (Django email backend;
  console in dev, SMTP/Gmail in prod)
- Dashboard wired to real API data for all three roles (admin, trainer, student)

---

## [0.3.0] — 2026-03-28

### Added

- `apps/accounts/authentication.py`: `MembershipJWTAuthentication` extending
  `JWTAuthentication`; reads `X-Institution-Id` header, loads the active
  `Membership`, and attaches it to `request.membership`
- `GET /api/auth/memberships/`: returns all active memberships for the
  authenticated user (used by the frontend institution picker)
- `frontend/js/config.js`: exports `API_BASE` from `window.ACADEMICO_CONFIG`
  with fallback to `localhost:8000`; eliminates hardcoded URLs in `api.js`
- Institution switcher (`renderInstitutionSwitcher`) wired in `initLayout()`;
  container added to all six authenticated pages
- `conftest.py`: `make_auth_client(user, institution)` helper for HTTP tests;
  generates JWT and sets `X-Institution-Id` header automatically
- HTTP view tests for all seven apps — 94 new tests covering auth gates,
  permission gates, institution isolation, and happy paths (224 total)

### Fixed

- `core/settings/base.py`: `DEFAULT_AUTHENTICATION_CLASSES` now points to
  `MembershipJWTAuthentication` instead of plain `JWTAuthentication`
- `core/permissions.py`: all permission classes (`IsAdminRole`, `IsTrainerRole`,
  `IsStudentRole`) now read `request.membership.role` — previously referenced
  the non-existent `request.user.role`
- `core/settings/development.py` + `production.py`: added `CORS_ALLOW_HEADERS`
  with `X-Institution-Id`; without this the browser blocked all requests after
  the OPTIONS preflight
- `apps/students/views.py`, `apps/trainers/views.py`, `apps/courses/views.py`,
  `apps/institutions/views.py`: replaced `request.user.institution` with
  `request.membership.institution` throughout; fixed `get_student_by_user` and
  `get_trainer_by_user` calls that were missing the `institution` argument
- `backend/create_institution.py`: rewritten to use `UserService.create_user()`
  and `MembershipService.create_membership()` — the old call passed `institution`
  and `role` arguments that no longer exist on `UserService`
- `frontend/js/layout.js`: `initLogout()` now calls `auth.logout()` so the
  refresh token is blacklisted on the backend; previously only called
  `session.clear()` client-side
- `apps/courses/tests/test_service.py`: `test_list_search_by_code` now uses
  explicit course names to avoid Faker generating names that contain "net"
  (e.g. "monetize"), which caused intermittent failures on `icontains` search

### Changed

- `apps/accounts/urls.py`: `MembershipsView` added to URL routes

---

## [0.2.0] — 2026-03-09

### Added — Backend

- `accounts/services.py`: `UserService` with full user lifecycle management
  (create, update, deactivate, change password, list)
- `institutions/management/commands/create_institution.py`: Django management
  command replacing the root-level bootstrap script; supports interactive and
  non-interactive (`--flag`) modes; wraps creation in `transaction.atomic()`
- `core/pagination.py`: `StandardResultsPagination` with extended response
  envelope (`count`, `pages`, `page`, `next`, `previous`, `results`)
- `core/mixins.py`: `PaginatedListMixin` exposing `self.paginate()` for use
  in `APIView` subclasses
- Pagination applied to all list endpoints across all seven apps
- `pytest.ini` and `conftest.py` with factory-boy factories and fixtures
- Test suite for all seven service layers (130 tests):
  accounts (23), institutions (10), students (21), trainers (19),
  courses (15), classes (23), grades (19)
- Django admin registration for all models with list display, filters,
  search, fieldsets and inline enrollment view inside `ClassAdmin`

### Fixed — Backend

- `accounts/models.py`: removed conflicting `unique=True` on `email` field
  that overrode the compound `UniqueConstraint(["institution", "email"])`,
  which broke multi-tenant email isolation
- `students/services.py`, `trainers/services.py`, `courses/services.py`:
  replaced `|` queryset union with `Q()` objects to eliminate duplicate
  results on OR searches
- `classes/services.py`: corrected inverted guard logic in `update_class` —
  closed classes now block all mutations unconditionally
- `grades/services.py`: `get_grades_for_student` now includes `completed`
  enrollments, not only `active`, so historical grades are visible
- `core/urls.py`: wrapped `debug_toolbar` import in `try/except ImportError`
  to prevent crash when the package is absent in production
- `core/settings/development.py`: replaced PostgreSQL with SQLite for local
  development to avoid `psycopg2` Unicode errors on Windows paths
- `core/settings/base.py`: added `encoding='utf-8'` to `load_dotenv()` call

### Added — Frontend

- Complete frontend application (8 pages, vanilla HTML/CSS/JS)
- `js/api.js`: central API client with Bearer token injection, silent JWT
  refresh on 401, normalised error objects
- `js/layout.js`: shared layout module (nav, breadcrumbs, auth guard, mobile sidebar)
- `css/global.css`: full design system (tokens, reset, typography, buttons,
  forms, badges, cards, tables, modals, toasts, skeleton loaders)
- `pages/login.html`: two-panel auth page with institution picker for
  multi-membership users
- `pages/dashboard.html`: role-based dashboard (skeleton loading,
  `Promise.allSettled` for parallel requests)
- `pages/students.html`, `pages/trainers.html`, `pages/courses.html`,
  `pages/classes.html`, `pages/grades.html`: full CRUD pages

---

## [0.1.0] — 2026-02-05

### Added — Backend

- Initial Django 5.0 project with modular app structure
- Three-tier settings split: `base`, `development`, `production`
- `core/permissions.py`: `IsAdminRole`, `IsTrainerRole`, `IsStudentRole`,
  `IsInstitutionMember`, `IsOwnerTrainer`
- `core/exceptions.py`: global exception handler returning
  `{error, status_code, detail}` envelope
- `apps/accounts`: custom `User` model (UUID PK, email as username, JWT auth)
- `apps/institutions`: `Institution` model as multi-tenant root entity
- `apps/students`: `Student` model with institution isolation
- `apps/trainers`: `Trainer` model with optional `User` link
- `apps/courses`: `Course` model with unique code per institution
- `apps/classes`: `Class` and `Enrollment` models with status state machines
- `apps/grades`: `Grade` model with assessment types and unique constraint
- `.env.example` documenting all required environment variables

---

[Unreleased]: https://github.com/Emicy963/SchoolAI/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/Emicy963/SchoolAI/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Emicy963/SchoolAI/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/Emicy963/SchoolAI/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Emicy963/SchoolAI/releases/tag/v0.1.0
