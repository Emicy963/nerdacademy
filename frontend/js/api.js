/**
 * api.js
 * Central API client for all backend communication.
 *
 * Architecture — Membership model:
 * - The backend uses User (global identity) + Membership (role per institution).
 * - Every authenticated request must send the header:
 *     X-Institution-Id: <institution_uuid>
 *   so the backend knows which institution context to use.
 * - On login the server returns { access, refresh, user, memberships[] }.
 *   The frontend stores the active membership in localStorage and uses its
 *   institution_id for the X-Institution-Id header on every subsequent request.
 * - If the user belongs to multiple institutions, they select one at login.
 *   The active membership can be switched without logging out.
 */

import { API_BASE } from './config.js';

// ── Session helpers ───────────────────────────────────────────────
export const session = {
  // Raw JWT tokens
  getAccess:  () => localStorage.getItem('access'),
  getRefresh: () => localStorage.getItem('refresh'),

  // The authenticated User object (global identity — no role/institution)
  getUser: () => {
    try { return JSON.parse(localStorage.getItem('user') ?? 'null'); }
    catch { return null; }
  },

  // All memberships returned on login
  getMemberships: () => {
    try { return JSON.parse(localStorage.getItem('memberships') ?? '[]'); }
    catch { return []; }
  },

  // The currently active membership { id, role, institution_id, institution_name }
  getActiveMembership: () => {
    try { return JSON.parse(localStorage.getItem('active_membership') ?? 'null'); }
    catch { return null; }
  },

  // Derived helpers used by layout.js and pages
  getRole:            () => session.getActiveMembership()?.role ?? null,
  getInstitutionId:   () => session.getActiveMembership()?.institution_id ?? null,
  getInstitutionName: () => session.getActiveMembership()?.institution_name ?? null,

  // Convenience — kept for backward compat with pages that call token.getUser()
  // Merges role + institution into the user object so existing code still works
  getUserWithRole: () => {
    const user       = session.getUser();
    const membership = session.getActiveMembership();
    if (!user) return null;
    return {
      ...user,
      role:             membership?.role            ?? null,
      institution_id:   membership?.institution_id  ?? null,
      institution_name: membership?.institution_name ?? null,
    };
  },

  set(access, refresh, user, memberships, activeMembership) {
    localStorage.setItem('access',            access);
    localStorage.setItem('refresh',           refresh);
    localStorage.setItem('user',              JSON.stringify(user));
    localStorage.setItem('memberships',       JSON.stringify(memberships));
    localStorage.setItem('active_membership', JSON.stringify(activeMembership));
  },

  setActiveMembership(membership) {
    localStorage.setItem('active_membership', JSON.stringify(membership));
  },

  clear() {
    ['access', 'refresh', 'user', 'memberships', 'active_membership']
      .forEach(k => localStorage.removeItem(k));
  },

  isLoggedIn: () => !!localStorage.getItem('access'),
};

// Keep legacy `token` export so existing page code doesn't break
export const token = {
  getAccess:  session.getAccess,
  getRefresh: session.getRefresh,
  getUser:    session.getUserWithRole,  // returns user merged with role/institution
  set:        (...args) => session.set(...args),
  clear:      session.clear,
  isLoggedIn: session.isLoggedIn,
};

// ── Error normalisation ───────────────────────────────────────────
async function parseError(res) {
  let detail = `HTTP ${res.status}`;
  try {
    const body = await res.json();
    if (body?.detail) {
      detail = typeof body.detail === 'string'
        ? body.detail
        : JSON.stringify(body.detail);
    } else if (body?.non_field_errors) {
      detail = body.non_field_errors[0];
    } else if (typeof body === 'object') {
      const first = Object.values(body)[0];
      detail = Array.isArray(first) ? first[0] : String(first);
    }
  } catch { /* ignore */ }
  const err = new Error(detail);
  err.status = res.status;
  err.detail = detail;
  return err;
}

// ── Silent token refresh ──────────────────────────────────────────
let _refreshing = null;

async function silentRefresh() {
  if (_refreshing) return _refreshing;
  _refreshing = (async () => {
    const refresh = session.getRefresh();
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

// ── Core fetch wrapper ────────────────────────────────────────────
let _retrying = false;

export async function apiFetch(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const access = session.getAccess();
  if (access) headers['Authorization'] = `Bearer ${access}`;

  // Always send the active institution context
  const institutionId = session.getInstitutionId();
  if (institutionId) headers['X-Institution-Id'] = institutionId;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  // 401 → try silent refresh once
  if (res.status === 401 && !_retrying) {
    _retrying = true;
    try {
      await silentRefresh();
      _retrying = false;
      return apiFetch(path, options);
    } catch {
      _retrying = false;
      session.clear();
      window.location.href = '/pages/login.html';
      throw new Error('Session expired');
    }
  }

  _retrying = false;

  if (!res.ok) throw await parseError(res);
  if (res.status === 204) return null;
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────
export const auth = {
  /**
   * Login — returns { access, refresh, user, memberships }.
   * The caller is responsible for choosing the active membership
   * (login page handles this) and calling session.set().
   */
  async login(email, password) {
    const res = await fetch(`${API_BASE}/auth/login/`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ email, password }),
    });
    if (!res.ok) throw await parseError(res);
    return res.json();
  },

  async logout() {
    const refresh = session.getRefresh();
    if (refresh) {
      try {
        await apiFetch('/auth/logout/', {
          method: 'POST',
          body:   JSON.stringify({ refresh }),
        });
      } catch { /* clear locally regardless */ }
    }
    session.clear();
    window.location.href = '/pages/login.html';
  },

  async me() {
    return apiFetch('/auth/me/');
  },

  async changePassword(old_password, new_password) {
    return apiFetch('/auth/change-password/', {
      method: 'POST',
      body:   JSON.stringify({ old_password, new_password }),
    });
  },

  async memberships() {
    return apiFetch('/auth/memberships/');
  },
};

// ── Students ──────────────────────────────────────────────────────
export const students = {
  list:          (params = {}) => apiFetch('/students/?' + new URLSearchParams(params)),
  get:           (id)          => apiFetch(`/students/${id}/`),
  create:        (data)        => apiFetch('/students/', { method: 'POST', body: JSON.stringify(data) }),
  update:        (id, data)    => apiFetch(`/students/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deactivate:    (id)          => apiFetch(`/students/${id}/`, { method: 'DELETE' }),
  resetPassword: (id)          => apiFetch(`/students/${id}/reset-password/`, { method: 'POST' }),
  me:            ()            => apiFetch('/students/me/'),
};

// ── Trainers ──────────────────────────────────────────────────────
export const trainers = {
  list:          (params = {}) => apiFetch('/trainers/?' + new URLSearchParams(params)),
  get:           (id)          => apiFetch(`/trainers/${id}/`),
  create:        (data)        => apiFetch('/trainers/', { method: 'POST', body: JSON.stringify(data) }),
  update:        (id, data)    => apiFetch(`/trainers/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deactivate:    (id)          => apiFetch(`/trainers/${id}/`, { method: 'DELETE' }),
  resetPassword: (id)          => apiFetch(`/trainers/${id}/reset-password/`, { method: 'POST' }),
  me:            ()            => apiFetch('/trainers/me/'),
  classes:       (id)          => apiFetch(`/trainers/${id}/classes/`),
};

// ── Courses ───────────────────────────────────────────────────────
export const courses = {
  list:       (params = {}) => apiFetch('/courses/?' + new URLSearchParams(params)),
  get:        (id)          => apiFetch(`/courses/${id}/`),
  create:     (data)        => apiFetch('/courses/', { method: 'POST', body: JSON.stringify(data) }),
  update:     (id, data)    => apiFetch(`/courses/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  deactivate: (id)          => apiFetch(`/courses/${id}/`, { method: 'DELETE' }),
  classes:    (id)          => apiFetch(`/courses/${id}/classes/`),
};

// ── Classes ───────────────────────────────────────────────────────
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
      body:   JSON.stringify({ student_id: studentId }),
    }),
    drop: (classId, enrollmentId) => apiFetch(
      `/classes/${classId}/enrollments/${enrollmentId}/`, { method: 'DELETE' }
    ),
  },
  myEnrollments: (params = {}) => apiFetch('/classes/my-enrollments/?' + new URLSearchParams(params)),
};

// ── Grades ────────────────────────────────────────────────────────
export const grades = {
  list:         (params = {}) => apiFetch('/grades/?' + new URLSearchParams(params)),
  get:          (id)          => apiFetch(`/grades/${id}/`),
  launch:       (data)        => apiFetch('/grades/', { method: 'POST', body: JSON.stringify(data) }),
  update:       (id, data)    => apiFetch(`/grades/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete:       (id)          => apiFetch(`/grades/${id}/`, { method: 'DELETE' }),
  report:       (classId)     => apiFetch(`/grades/report/?class_id=${classId}`),
  myGrades:     ()            => apiFetch('/grades/my-grades/'),
  byEnrollment: (enrollmentId) => apiFetch(`/grades/enrollment/${enrollmentId}/`),
};

// ── Institutions ──────────────────────────────────────────────────
export const institutions = {
  me:     ()     => apiFetch('/institutions/me/'),
  update: (data) => apiFetch('/institutions/me/', { method: 'PATCH', body: JSON.stringify(data) }),
};
