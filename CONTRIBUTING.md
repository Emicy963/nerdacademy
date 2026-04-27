# Contributing

This document describes the conventions and workflow for contributing to
Acadêmico. Please read it before opening a pull request.

---

## Commit conventions

All commits must follow the Conventional Commits specification:

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

**Types:**

| Type       | When to use                                              |
|------------|----------------------------------------------------------|
| `feat`     | A new feature                                            |
| `fix`      | A bug fix                                                |
| `refactor` | Code change that neither adds a feature nor fixes a bug  |
| `chore`    | Tooling, config, dependency updates                      |
| `docs`     | Documentation only                                       |
| `test`     | Adding or correcting tests                               |
| `perf`     | Performance improvements                                 |

**Scopes** should identify the part of the codebase affected:

- `backend`, `frontend` — top-level area
- App names: `accounts`, `institutions`, `students`, `trainers`, `courses`, `classes`, `grades`
- `core`, `auth`, `api`, `ui`

**Examples:**

```
feat(students): add deactivation endpoint with soft-delete
fix(grades): include completed enrollments in student grade view
refactor(core): replace OR queryset union with Q() in list services
docs(frontend): add mock API usage instructions to README
chore(backend): upgrade Django to 5.1
```

---

## Branching strategy

- `main` — production-ready code only
- `develop` — integration branch; all feature branches merge here
- `feature/<description>` — new features
- `fix/<description>` — bug fixes
- `chore/<description>` — maintenance

Pull requests target `develop`. Releases are merged from `develop` to `main`
with a version tag.

---

## Code conventions

### Backend (Python)

- Format with `black` (included in development dependencies).
- Business logic belongs in `services.py`, not in views or serializers.
- Service methods must be `@staticmethod`.
- All new models require an institution `ForeignKey`.
- All new list endpoints must apply `PaginatedListMixin`.
- Every new endpoint must be tested before merging.

### Frontend (JavaScript)

- Vanilla ES6+ only. No framework dependencies.
- All API calls go through `js/api.js` or `js/api.mock.js`. No direct `fetch`
  calls in page scripts.
- Every list view must handle three states: loading (skeleton), loaded (data),
  and error (message + retry).
- Role checks must be applied at the UI level even when the API enforces them.

---

## Pull request checklist

Before requesting a review, confirm:

- [ ] Commits follow the Conventional Commits format
- [ ] Backend: migrations are included if models changed
- [ ] Backend: new service methods have docstrings
- [ ] Frontend: new pages load correctly in all three role views (admin, trainer, student)
- [ ] Frontend: mock API supports any new API calls added
- [ ] `CHANGELOG.md` has been updated under `[Unreleased]`
- [ ] No secrets, tokens or `.env` values are committed

---

## Reporting issues

Open a GitHub issue with:

1. A clear title describing the problem
2. Steps to reproduce
3. Expected behaviour
4. Actual behaviour
5. Environment (OS, browser, Python version if backend)
