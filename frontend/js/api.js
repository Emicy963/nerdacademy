/**
 * api.js
 * Central API client for all backend communication.
 *
 * - All requests go through `apiFetch()` which attaches the Bearer token
 * - On 401 the client attempts a silent token refresh once, then redirects to login
 * - Errors are normalised to { message, status, detail }
 * - No hardcoded data anywhere — every call hits the backend
 */

const API_BASE = 'http://localhost:8000/api';

// ── Token helpers ─────────────────────────────────────────
export const token = {
  getAccess:  () => localStorage.getItem('access'),
  getRefresh: () => localStorage.getItem('refresh'),
  getUser:    () => {
    try { return JSON.parse(localStorage.getItem('user') ?? 'null'); }
    catch { return null; }
  },
  set(access, refresh, user) {
    localStorage.setItem('access',  access);
    localStorage.setItem('refresh', refresh);
    localStorage.setItem('user',    JSON.stringify(user));
  },
  clear() {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user');
  },
  isLoggedIn: () => !!localStorage.getItem('access'),
};

// ── Normalise error responses ─────────────────────────────
async function parseError(res) {
  let detail = `HTTP ${res.status}`;
  try {
    const body = await res.json();
    // Backend wraps errors: { error: true, status_code: N, detail: ... }
    if (body?.detail) {
      detail = typeof body.detail === 'string'
        ? body.detail
        : JSON.stringify(body.detail);
    } else if (body?.non_field_errors) {
      detail = body.non_field_errors[0];
    } else if (typeof body === 'object') {
      // Field-level errors — flatten to first message
      const first = Object.values(body)[0];
      detail = Array.isArray(first) ? first[0] : String(first);
    }
  } catch { /* ignore */ }
  const err = new Error(detail);
  err.status = res.status;
  err.detail = detail;
  return err;
}

// ── Silent token refresh ──────────────────────────────────
let _refreshing = null; // single in-flight refresh promise

async function silentRefresh() {
  if (_refreshing) return _refreshing;
  _refreshing = (async () => {
    const refresh = token.getRefresh();
    if (!refresh) throw new Error('No refresh token');

    const res = await fetch(`${API_BASE}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });

    if (!res.ok) throw await parseError(res);

    const data = await res.json();
    localStorage.setItem('access', data.access);
    return data.access;
  })().finally(() => { _refreshing = null; });
  return _refreshing;
}

// ── Core fetch wrapper ────────────────────────────────────
let _retrying = false;

export async function apiFetch(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const access = token.getAccess();
  if (access) headers['Authorization'] = `Bearer ${access}`;

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  // 401 → try silent refresh once
  if (res.status === 401 && !_retrying) {
    _retrying = true;
    try {
      await silentRefresh();
      _retrying = false;
      return apiFetch(path, options); // retry with new token
    } catch {
      _retrying = false;
      token.clear();
      window.location.href = '/frontend/pages/login.html';
      throw new Error('Session expired');
    }
  }

  _retrying = false;

  if (!res.ok) throw await parseError(res);

  // 204 No Content
  if (res.status === 204) return null;

  return res.json();
}

// ── Auth endpoints ────────────────────────────────────────
export const auth = {
  async login(email, password) {
    const data = await apiFetch('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    // data: { access, refresh, user: { id, email, role, institution_id, institution_name } }
    token.set(data.access, data.refresh, data.user);
    return data;
  },

  async logout() {
    const refresh = token.getRefresh();
    if (refresh) {
      try {
        await apiFetch('/auth/logout/', {
          method: 'POST',
          body: JSON.stringify({ refresh }),
        });
      } catch { /* ignore — clear locally regardless */ }
    }
    token.clear();
    window.location.href = '/frontend/pages/login.html';
  },

  async me() {
    return apiFetch('/auth/me/');
  },

  async changePassword(old_password, new_password) {
    return apiFetch('/auth/change-password/', {
      method: 'POST',
      body: JSON.stringify({ old_password, new_password }),
    });
  },
};

// ── Students ──────────────────────────────────────────────
export const students = {
  list: (params = {}) => apiFetch('/students/?' + new URLSearchParams(params)),
  get:  (id)          => apiFetch(`/students/${id}/`),
  create: (data)      => apiFetch('/students/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data)  => apiFetch(`/students/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deactivate: (id)    => apiFetch(`/students/${id}/`, { method: 'DELETE' }),
  me:  ()             => apiFetch('/students/me/'),
};

// ── Trainers ──────────────────────────────────────────────
export const trainers = {
  list:   (params = {}) => apiFetch('/trainers/?' + new URLSearchParams(params)),
  get:    (id)          => apiFetch(`/trainers/${id}/`),
  create: (data)        => apiFetch('/trainers/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data)    => apiFetch(`/trainers/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deactivate: (id)      => apiFetch(`/trainers/${id}/`, { method: 'DELETE' }),
  me:     ()            => apiFetch('/trainers/me/'),
  classes: (id)         => apiFetch(`/trainers/${id}/classes/`),
};

// ── Courses ───────────────────────────────────────────────
export const courses = {
  list:   (params = {}) => apiFetch('/courses/?' + new URLSearchParams(params)),
  get:    (id)          => apiFetch(`/courses/${id}/`),
  create: (data)        => apiFetch('/courses/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data)    => apiFetch(`/courses/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deactivate: (id)      => apiFetch(`/courses/${id}/`, { method: 'DELETE' }),
  classes: (id)         => apiFetch(`/courses/${id}/classes/`),
};

// ── Classes ───────────────────────────────────────────────
export const classes = {
  list:   (params = {}) => apiFetch('/classes/?' + new URLSearchParams(params)),
  get:    (id)          => apiFetch(`/classes/${id}/`),
  create: (data)        => apiFetch('/classes/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data)    => apiFetch(`/classes/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id)          => apiFetch(`/classes/${id}/`, { method: 'DELETE' }),
  close:  (id)          => apiFetch(`/classes/${id}/close/`, { method: 'POST' }),
  enrollments: {
    list:   (classId, params = {}) => apiFetch(`/classes/${classId}/enrollments/?` + new URLSearchParams(params)),
    enroll: (classId, studentId)   => apiFetch(`/classes/${classId}/enrollments/`, {
      method: 'POST',
      body: JSON.stringify({ student_id: studentId }),
    }),
    drop: (classId, enrollmentId)  => apiFetch(`/classes/${classId}/enrollments/${enrollmentId}/`, { method: 'DELETE' }),
  },
  myEnrollments: (params = {}) => apiFetch('/classes/my-enrollments/?' + new URLSearchParams(params)),
};

// ── Grades ────────────────────────────────────────────────
export const grades = {
  list:   (params = {}) => apiFetch('/grades/?' + new URLSearchParams(params)),
  get:    (id)          => apiFetch(`/grades/${id}/`),
  launch: (data)        => apiFetch('/grades/', { method: 'POST', body: JSON.stringify(data) }),
  update: (id, data)    => apiFetch(`/grades/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id)          => apiFetch(`/grades/${id}/`, { method: 'DELETE' }),
  report: (classId)     => apiFetch(`/grades/report/?class_id=${classId}`),
  myGrades: ()          => apiFetch('/grades/my-grades/'),
  byEnrollment: (enrollmentId) => apiFetch(`/grades/enrollment/${enrollmentId}/`),
};

// ── Institutions ──────────────────────────────────────────
export const institutions = {
  me:     ()     => apiFetch('/institutions/me/'),
  update: (data) => apiFetch('/institutions/me/', { method: 'PATCH', body: JSON.stringify(data) }),
};
