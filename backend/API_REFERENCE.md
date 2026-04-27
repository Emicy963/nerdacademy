# AcadémicoPro — API Reference

Base URL: `http://localhost:8000/api`
Authentication: `Authorization: Bearer <access_token>`

---

## Authentication — `/api/auth/`

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | `/auth/login/` | Public | Login — returns JWT access + refresh + user |
| POST | `/auth/logout/` | Auth | Blacklist refresh token |
| POST | `/auth/token/refresh/` | Public | Refresh access token |
| GET | `/auth/me/` | Auth | Current user profile |
| PATCH | `/auth/me/` | Auth | Update own profile |
| POST | `/auth/change-password/` | Auth | Change own password |
| GET | `/auth/users/` | Admin | List institution users |
| POST | `/auth/users/` | Admin | Create user |
| GET | `/auth/users/{id}/` | Admin | User detail |
| PATCH | `/auth/users/{id}/` | Admin | Update user role/status |
| DELETE | `/auth/users/{id}/` | Admin | Deactivate user |

### Login request/response
```json
// POST /api/auth/login/
{ "email": "admin@centro.ao", "password": "secret123" }

// 200 OK
{
  "access": "<jwt>",
  "refresh": "<jwt>",
  "user": {
    "id": "uuid", "email": "admin@centro.ao",
    "role": "admin",
    "institution_id": "uuid",
    "institution_name": "Centro Angola"
  }
}
```

---

## Institutions — `/api/institutions/`

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/institutions/` | Superadmin | List all institutions |
| POST | `/institutions/` | Superadmin | Create institution |
| GET | `/institutions/{id}/` | Superadmin | Institution detail |
| PATCH | `/institutions/{id}/` | Superadmin | Update institution |
| DELETE | `/institutions/{id}/` | Superadmin | Deactivate institution |
| GET | `/institutions/me/` | Auth | Own institution |
| PATCH | `/institutions/me/` | Admin | Update own institution |

---

## Students — `/api/students/`

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/students/` | Admin, Trainer | List students (`?search=`, `?is_active=`) |
| POST | `/students/` | Admin | Create student |
| GET | `/students/{id}/` | Admin, Trainer | Student detail |
| PATCH | `/students/{id}/` | Admin | Update student |
| DELETE | `/students/{id}/` | Admin | Deactivate student |
| GET | `/students/me/` | Auth | Own student profile |

---

## Trainers — `/api/trainers/`

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/trainers/` | Admin | List trainers (`?search=`, `?is_active=`) |
| POST | `/trainers/` | Admin | Create trainer |
| GET | `/trainers/{id}/` | Admin | Trainer detail |
| PATCH | `/trainers/{id}/` | Admin | Update trainer |
| DELETE | `/trainers/{id}/` | Admin | Deactivate trainer |
| GET | `/trainers/{id}/classes/` | Admin, own Trainer | Trainer's classes |
| GET | `/trainers/me/` | Auth | Own trainer profile |

---

## Courses — `/api/courses/`

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/courses/` | All Auth | List courses (`?search=`, `?is_active=`) |
| POST | `/courses/` | Admin | Create course |
| GET | `/courses/{id}/` | All Auth | Course detail |
| PUT | `/courses/{id}/` | Admin | Full update |
| PATCH | `/courses/{id}/` | Admin | Partial update |
| DELETE | `/courses/{id}/` | Admin | Deactivate course |
| GET | `/courses/{id}/classes/` | Admin, Trainer | Classes for this course |

---

## Classes — `/api/classes/`

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/classes/` | All Auth (filtered by role) | List classes |
| POST | `/classes/` | Admin | Create class |
| GET | `/classes/{id}/` | Admin, own Trainer | Class detail + enrollments |
| PATCH | `/classes/{id}/` | Admin | Update class |
| DELETE | `/classes/{id}/` | Admin | Delete class (only if empty) |
| POST | `/classes/{id}/close/` | Admin | Close class + complete enrollments |
| GET | `/classes/{id}/enrollments/` | Admin, own Trainer | List enrollments |
| POST | `/classes/{id}/enrollments/` | Admin | Enroll student |
| GET | `/classes/{id}/enrollments/{eid}/` | Admin, Trainer | Enrollment detail |
| DELETE | `/classes/{id}/enrollments/{eid}/` | Admin | Drop enrollment |
| GET | `/classes/my-enrollments/` | Student | Own enrollments |

### Create class body
```json
{
  "course_id": "uuid",
  "trainer_id": "uuid",
  "name": "Turma A 2024",
  "start_date": "2024-02-01",
  "end_date": "2024-07-31"
}
```

---

## Grades — `/api/grades/`

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `/grades/` | Admin, Trainer | List grades (`?class_id=`, `?student_id=`, `?enrollment_id=`) |
| POST | `/grades/` | Admin, own Trainer | Launch grade |
| GET | `/grades/{id}/` | Admin, Trainer | Grade detail |
| PATCH | `/grades/{id}/` | Admin, own Trainer | Update grade |
| DELETE | `/grades/{id}/` | Admin, own Trainer | Delete grade |
| GET | `/grades/report/?class_id={id}` | Admin, own Trainer | Full class grade report |
| GET | `/grades/my-grades/` | Student | Own grades grouped by class |
| GET | `/grades/enrollment/{eid}/` | Admin, Trainer | Grades for enrollment |

### Launch grade body
```json
{
  "enrollment_id": "uuid",
  "assessment_type": "exam",
  "value": 14.50,
  "max_value": 20.00,
  "assessed_at": "2024-06-15",
  "notes": "Exame final módulo 3"
}
```

### My grades response (student)
```json
[
  {
    "class_id": "uuid",
    "class_name": "Turma A 2024",
    "course_name": "Redes Informáticas",
    "trainer_name": "João Pereira",
    "average": "15.25",
    "grades": [
      { "assessment_type": "continuous", "value": "16.00", "max_value": "20.00", "assessed_at": "2024-04-10" },
      { "assessment_type": "exam",       "value": "14.50", "max_value": "20.00", "assessed_at": "2024-06-15" }
    ]
  }
]
```

---

## Assessment types
`continuous` | `exam` | `practical` | `project` | `other`

## Class statuses
`open` | `in_progress` | `closed`

## Enrollment statuses
`active` | `dropped` | `completed`

## User roles
`admin` | `trainer` | `student`
