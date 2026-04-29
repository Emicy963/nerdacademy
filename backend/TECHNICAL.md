# Backend — Technical Reference

This document explains the internal architecture, design decisions and code
conventions of the Matrika Django backend. It is intended for developers
who need to understand, extend or audit the codebase.

---

## Architecture overview

The backend follows a layered monolithic architecture. All business logic is
confined to `services.py` in each app. Views handle HTTP only. This separation
means the service layer can be tested independently of HTTP, and views remain
thin and predictable.

```
HTTP request
    │
    ▼
View (views.py)
    │  validates input via Serializer
    │  calls Service with clean data
    ▼
Service (services.py)
    │  applies business rules
    │  queries/mutates the database
    ▼
Model (models.py)
    │  Django ORM
    ▼
PostgreSQL
```

---

## Core layer

### `core/settings/`

Three-tier settings split. The active module is selected by the environment
variable `DJANGO_SETTINGS_MODULE`.

`base.py` holds all shared configuration: installed apps, middleware stack,
DRF configuration, JWT settings, database (overridable by child settings),
internationalization, static and media paths.

`development.py` extends base with `DEBUG = True`, `CORS_ALLOW_ALL_ORIGINS`,
the browsable API renderer, and `django-debug-toolbar`.

`production.py` extends base with `DEBUG = False`, HSTS headers, SSL redirect,
CSRF and session cookie security flags, and `ManifestStaticFilesStorage`
(fingerprinted static files).

### `core/exceptions.py`

Replaces the default DRF exception handler. All error responses follow a
consistent envelope:

```json
{
  "error": true,
  "status_code": 400,
  "detail": { "field": ["message"] }
}
```

Unhandled Python exceptions are caught and returned as 500 with a generic
message, preventing stack trace exposure.

### `core/permissions.py`

Four permission classes:

- `IsAdminRole` — user.role == "admin"
- `IsTrainerRole` — user.role in ("admin", "trainer"); used for read access to trainer-facing resources
- `IsStudentRole` — user.role == "student"
- `IsInstitutionMember` — object-level check; obj.institution_id == request.user.institution_id
- `IsOwnerTrainer` — object-level check; grade's class trainer user == request.user

### `core/pagination.py`

`StandardResultsPagination` extends `PageNumberPagination`. Response envelope:

```json
{
  "count": 87,
  "pages": 5,
  "page": 1,
  "next": "http://...?page=2",
  "previous": null,
  "results": []
}
```

Supports `?page_size=N` override (capped at 100). Registered as
`DEFAULT_PAGINATION_CLASS` in `REST_FRAMEWORK` settings.

### `core/mixins.py`

`PaginatedListMixin` — adds `self.paginate(request, queryset, SerializerClass)`
to any `APIView` subclass. All list views in all apps use this mixin. This
was added because `APIView` does not paginate automatically — only `GenericAPIView`
does. The mixin provides the same result without migrating all views to generics.

`InstitutionQuerysetMixin` — intended for ViewSet-based views. Filters
querysets by `institution_id` automatically. Currently defined but not yet
used (views use explicit filtering via services).

---

## Multi-tenancy implementation

Every model that contains institution data carries a `ForeignKey` to
`institutions.Institution`. Institution isolation is enforced at two levels:

1. **Service level** — every service method that lists or retrieves records
   filters by the institution passed from the view (`request.user.institution`).
   Example from `StudentService.list_students`:

   ```python
   qs = Student.objects.filter(institution=institution)
   ```

2. **View level** — views extract the institution from the authenticated user:

   ```python
   students = StudentService.list_students(
       institution=request.user.institution,
       ...
   )
   ```

There is no global queryset filter. Each service call is explicit. This
makes the isolation visible and auditable at the code level without relying
on middleware magic.

The `User` model has `email = models.EmailField()` (no global unique) and a
`UniqueConstraint(["institution", "email"])`. This permits the same email
address to be used in different institutions, which is required for a
genuinely multi-tenant system.

---

## Authentication and JWT

Authentication uses `djangorestframework-simplejwt`. The custom serializer
`CustomTokenObtainPairSerializer` (in `accounts/serializers.py`) injects
`role` and `institution_id` into the JWT payload:

```python
@classmethod
def get_token(cls, user):
    token = super().get_token(user)
    token["role"] = user.role
    token["institution_id"] = str(user.institution_id) if user.institution_id else None
    return token
```

The login response also includes a `user` object with full profile data so
the frontend does not need a separate `/me/` call on login.

Token blacklisting is enabled (`BLACKLIST_AFTER_ROTATION = True`). On logout,
the refresh token is added to the blacklist table, invalidating the session.
Access tokens remain valid until expiry (default 60 minutes).

---

## App structure convention

Every app follows the same file structure:

```
apps/<name>/
├── models.py       Data model definition
├── serializers.py  DRF serializers (input validation, output shaping)
├── services.py     Business logic (the only place ORM queries are written)
├── views.py        HTTP request/response (calls services, returns responses)
├── urls.py         URL patterns for this app
└── admin.py        Django admin registration
```

### models.py

- All primary keys are `UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`.
- All models carry `institution` as a `ForeignKey` to enforce multi-tenancy.
- Timestamps use `auto_now_add` and `auto_now` for `created_at`/`updated_at`.
- Uniqueness constraints that involve multiple fields use `Meta.constraints`
  with `UniqueConstraint` rather than `unique_together` (deprecated).

### serializers.py

Serializers are split by use case rather than using a single serializer with
different field sets:

- `<Model>Serializer` — full read serializer returned on GET responses
- `<Model>CreateSerializer` — validated input for POST; includes only writable fields
- `<Model>UpdateSerializer` — validated input for PATCH; may differ from create
- `<Model>SummarySerializer` — compact nested serializer used when embedding in other responses

### services.py

All service methods are `@staticmethod` on a class named `<Model>Service`.
They accept plain Python values (not request objects), which keeps them
testable in isolation. The service is responsible for:

- Duplicate/conflict checks before writes
- Business rule validation that spans multiple models
- ORM queries and mutations
- Raising `rest_framework.exceptions.ValidationError` or `NotFound` on failure

Example service method structure:

```python
@staticmethod
def create_student(institution, full_name: str, student_code: str, **kwargs) -> Student:
    if Student.objects.filter(institution=institution, student_code=student_code).exists():
        raise ValidationError({"student_code": "Already in use."})
    try:
        return Student.objects.create(
            institution=institution,
            full_name=full_name,
            student_code=student_code,
            **kwargs,
        )
    except IntegrityError:
        raise ValidationError({"student_code": "Already in use."})
```

The double check (pre-check + IntegrityError catch) handles race conditions.

### views.py

Views contain no business logic. A typical pattern:

```python
def post(self, request):
    serializer = StudentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    student = StudentService.create_student(
        institution=request.user.institution,
        **serializer.validated_data,
    )
    return Response(StudentSerializer(student).data, status=status.HTTP_201_CREATED)
```

---

## App-by-app reference

### accounts

`User` extends `AbstractBaseUser` and `PermissionsMixin`. Fields: `id` (UUID),
`institution` (FK, nullable for superusers), `email`, `role` (admin/trainer/student),
`is_active`, `is_staff`.

`UserService` provides: `create_user`, `get_user`, `update_user`,
`change_password`, `deactivate_user`, `list_users`.

Authentication views: `LoginView` (wraps `TokenObtainPairView`),
`RefreshView`, `LogoutView` (blacklists refresh token), `MeView`,
`ChangePasswordView`.

### institutions

`Institution` is the multi-tenant root entity. Fields: `id`, `name`, `slug`
(globally unique), `email`, `phone`, `address`, `is_active`.

`InstitutionService` provides: `create_institution` (validates slug
uniqueness globally), `get_institution`, `update_institution`,
`list_institutions`.

The management command `create_institution` delegates entirely to
`InstitutionService` and `UserService`. The command wraps both operations
in `transaction.atomic()` so that if user creation fails, the institution
is also rolled back.

### students and trainers

Both follow identical patterns. The `user` field is a nullable `OneToOneField`
to `accounts.User`. This allows a `Student` or `Trainer` profile to exist
without a linked login account (e.g. students who do not use the portal).
The `link_user` service method validates institution match and role before
associating an account with a profile.

### courses

`code` is validated to uppercase and checked for uniqueness within the
institution before creation. The `CourseUpdateSerializer` does not include
`code` — course codes cannot be changed after creation. This constraint is
enforced at the serializer level (by omission) rather than at the model level.

### classes

`Class` has a three-state status machine: `open` → `in_progress` → `closed`.

`ClassService.close_class` marks the class as closed and bulk-updates all
`active` enrolments to `completed` in a single query:

```python
Enrollment.objects.filter(
    class_instance=class_instance,
    status=Enrollment.Status.ACTIVE,
).update(status=Enrollment.Status.COMPLETED)
```

`ClassService.delete_class` only permits deletion of classes with zero
enrolments. Classes with enrolments must be closed instead.

`EnrollmentService.enroll_student` performs three checks before writing:

1. Class status is `open`
2. Student and class belong to the same institution
3. Student is not already enrolled

The database `UniqueConstraint(["class_instance", "student"])` provides a
final guard against race conditions.

### grades

`Grade` has a `UniqueConstraint(["enrollment", "assessment_type"])` — one
grade per assessment type per enrolment.

`GradeService._validate_trainer_owns_class` is called on every write
operation. Admins bypass this check. Trainers without a linked `Trainer`
profile get a `PermissionDenied` exception.

`GradeService.calculate_average` normalises all grades to a 0–20 scale
using `(value / max_value) * 20` and returns a weighted average:

```python
normalised = (grade.value / grade.max_value) * Decimal("20")
```

This handles assessments with different max values consistently.

`GradeService.get_class_report` builds the full per-student report used by
the grade report endpoint. It queries enrollments and grades separately to
avoid N+1 queries per student.

---

## Query performance notes

- All list queries use `select_related` for FK fields that are accessed in
  serializers (e.g. `Student.objects.select_related("institution", "user")`).
- The `enrollment_count` field on `ClassSerializer` uses a per-object query
  (`obj.enrollments.filter(status="active").count()`). In list responses,
  this produces N+1 queries. The fix — using `annotate` on the queryset — is
  documented in the codebase as a known improvement.
- Grade report queries iterate enrollments and issue one grade query per
  enrolment. For large classes (100+ students), this should be refactored to
  a single query with `prefetch_related`.

---

## Error response reference

All errors follow the envelope defined in `core/exceptions.py`:

```json
{
  "error": true,
  "status_code": 400,
  "detail": {
    "field_name": ["Error message."]
  }
}
```

For non-field errors (e.g. `ValidationError` raised in a service without a
field key):

```json
{
  "error": true,
  "status_code": 400,
  "detail": { "detail": "Human-readable message." }
}
```

HTTP 500 responses always return a generic message; the actual exception is
logged server-side.
