/**
 * api.mock.js
 *
 * Drop-in replacement for api.js that returns realistic fixture data
 * without making any network requests. Used to develop and test the
 * frontend UI independently of the Django backend.
 *
 * USAGE
 * -----
 * In every page that imports from api.js, temporarily change:
 *
 *   import { students, ... } from '../js/api.js';
 *   to:
 *   import { students, ... } from '../js/api.mock.js';
 *
 * The login page accepts any email/password combination.
 * The mock user defaults to role "admin". Change MOCK_USER.role to
 * "trainer" or "student" to test the other role views.
 *
 * All write operations (create, update, delete) resolve successfully
 * and return the mutated fixture so the UI re-renders correctly.
 * Nothing is persisted — a page refresh resets all state.
 */

// ── Active mock user — change role here to test different views ────
const MOCK_USER = {
  id:               'a1b2c3d4-0000-0000-0000-000000000001',
  email:            'admin@cinfotec.ao',
  role:             'admin',           // 'admin' | 'trainer' | 'student'
  institution_id:   'inst-0000-0000-0000-000000000001',
  institution_name: 'CINFOTEC Huambo',
  created_at:       '2024-01-15T08:00:00Z',
};

// ── Token helpers (same interface as api.js) ───────────────────────
export const token = {
  getAccess:  () => localStorage.getItem('access') ?? 'mock-access-token',
  getRefresh: () => localStorage.getItem('refresh') ?? 'mock-refresh-token',
  getUser:    () => {
    try { return JSON.parse(localStorage.getItem('user') ?? 'null') ?? MOCK_USER; }
    catch { return MOCK_USER; }
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
  isLoggedIn: () => true,  // always logged in during mock mode
};

// ── Simulated network delay (ms) ───────────────────────────────────
const DELAY = 400;
const delay = (ms = DELAY) => new Promise(r => setTimeout(r, ms));

// ── UUID generator (simple) ────────────────────────────────────────
let _seq = 100;
const uuid = () => `mock-${++_seq}-${Date.now()}`;

// ── Paginated response envelope ────────────────────────────────────
function paginate(results, params = {}) {
  const page      = parseInt(params.page ?? 1);
  const page_size = parseInt(params.page_size ?? 20);
  const start     = (page - 1) * page_size;
  const slice     = results.slice(start, start + page_size);
  return {
    count:    results.length,
    pages:    Math.ceil(results.length / page_size),
    page,
    next:     start + page_size < results.length ? `?page=${page + 1}` : null,
    previous: page > 1 ? `?page=${page - 1}` : null,
    results:  slice,
  };
}

// ══════════════════════════════════════════════════════════════════
//  FIXTURE DATA
// ══════════════════════════════════════════════════════════════════

const INSTITUTION = {
  id:         'inst-0000-0000-0000-000000000001',
  name:       'CINFOTEC Huambo',
  slug:       'cinfotec-huambo',
  email:      'geral@cinfotec.ao',
  phone:      '+244 241 000 001',
  address:    'Rua da Independência, 42, Huambo, Angola',
  is_active:  true,
  created_at: '2024-01-10T10:00:00Z',
  updated_at: '2024-06-01T09:00:00Z',
};

let STUDENTS = [
  { id: 'stu-001', institution: INSTITUTION.id, full_name: 'Ana Luísa Ferreira', student_code: 'EST-2024-001', birth_date: '2002-03-14', phone: '+244 923 111 001', address: 'Bairro Académico, Huambo', is_active: true,  enrolled_at: '2024-02-01T08:00:00Z', updated_at: '2024-02-01T08:00:00Z' },
  { id: 'stu-002', institution: INSTITUTION.id, full_name: 'Carlos Manuel Silva',  student_code: 'EST-2024-002', birth_date: '2001-07-22', phone: '+244 923 111 002', address: 'Centralidade do Huambo',   is_active: true,  enrolled_at: '2024-02-01T08:00:00Z', updated_at: '2024-02-01T08:00:00Z' },
  { id: 'stu-003', institution: INSTITUTION.id, full_name: 'Beatriz Neto Costa',   student_code: 'EST-2024-003', birth_date: '2003-11-05', phone: '+244 923 111 003', address: 'Bairro da Paz, Huambo',    is_active: true,  enrolled_at: '2024-02-15T08:00:00Z', updated_at: '2024-02-15T08:00:00Z' },
  { id: 'stu-004', institution: INSTITUTION.id, full_name: 'David António Lopes',  student_code: 'EST-2024-004', birth_date: '2002-05-18', phone: '',                  address: '',                        is_active: true,  enrolled_at: '2024-03-01T08:00:00Z', updated_at: '2024-03-01T08:00:00Z' },
  { id: 'stu-005', institution: INSTITUTION.id, full_name: 'Esperança João Pedro', student_code: 'EST-2024-005', birth_date: '2001-09-30', phone: '+244 923 111 005', address: 'Quarteirão 7, Huambo',     is_active: false, enrolled_at: '2024-01-20T08:00:00Z', updated_at: '2024-05-10T08:00:00Z' },
  { id: 'stu-006', institution: INSTITUTION.id, full_name: 'Francisco Bento Lima',  student_code: 'EST-2024-006', birth_date: '2003-02-11', phone: '+244 923 111 006', address: 'Bairro do Belas, Huambo',  is_active: true,  enrolled_at: '2024-03-10T08:00:00Z', updated_at: '2024-03-10T08:00:00Z' },
  { id: 'stu-007', institution: INSTITUTION.id, full_name: 'Graça Simão Teixeira',  student_code: 'EST-2024-007', birth_date: '2002-08-25', phone: '+244 923 111 007', address: 'Rua da Missão, Huambo',    is_active: true,  enrolled_at: '2024-03-15T08:00:00Z', updated_at: '2024-03-15T08:00:00Z' },
];

let TRAINERS = [
  { id: 'trn-001', institution: INSTITUTION.id, full_name: 'Prof. José Cardoso',    specialization: 'Web Development',    phone: '+244 912 200 001', bio: 'Engenheiro de software com 8 anos de experiência em desenvolvimento web full-stack.', is_active: true,  hired_at: '2023-09-01T08:00:00Z', updated_at: '2023-09-01T08:00:00Z' },
  { id: 'trn-002', institution: INSTITUTION.id, full_name: 'Dra. Maria Conceição', specialization: 'Database Systems',    phone: '+244 912 200 002', bio: 'Doutorada em Ciências da Computação, especialista em bases de dados relacionais e NoSQL.', is_active: true,  hired_at: '2023-09-01T08:00:00Z', updated_at: '2023-09-01T08:00:00Z' },
  { id: 'trn-003', institution: INSTITUTION.id, full_name: 'Eng. Paulo Rodrigues', specialization: 'Networking',          phone: '+244 912 200 003', bio: 'Certificado CCNA e CCNP, 10 anos de experiência em infraestrutura de redes corporativas.', is_active: true,  hired_at: '2024-01-15T08:00:00Z', updated_at: '2024-01-15T08:00:00Z' },
  { id: 'trn-004', institution: INSTITUTION.id, full_name: 'Dr. António Mbala',    specialization: 'Cybersecurity',       phone: '',                 bio: '', is_active: false, hired_at: '2023-06-01T08:00:00Z', updated_at: '2024-04-01T08:00:00Z' },
];

let COURSES = [
  { id: 'crs-001', institution: INSTITUTION.id, institution_name: INSTITUTION.name, name: 'Web Development',      code: 'WD-2024',  description: 'Desenvolvimento web completo com HTML, CSS, JavaScript, React e Node.js. Abrange frontend e backend.',        total_hours: 240, is_active: true,  created_at: '2024-01-15T08:00:00Z', updated_at: '2024-01-15T08:00:00Z' },
  { id: 'crs-002', institution: INSTITUTION.id, institution_name: INSTITUTION.name, name: 'Database Design',      code: 'DB-2024',  description: 'Modelagem de dados, SQL avançado, PostgreSQL, MySQL e introdução a bancos NoSQL como MongoDB.',              total_hours: 160, is_active: true,  created_at: '2024-01-15T08:00:00Z', updated_at: '2024-01-15T08:00:00Z' },
  { id: 'crs-003', institution: INSTITUTION.id, institution_name: INSTITUTION.name, name: 'Computer Networking',  code: 'NET-2024', description: 'Fundamentos de redes, protocolos TCP/IP, roteamento, switching e segurança de redes.',                       total_hours: 200, is_active: true,  created_at: '2024-01-20T08:00:00Z', updated_at: '2024-01-20T08:00:00Z' },
  { id: 'crs-004', institution: INSTITUTION.id, institution_name: INSTITUTION.name, name: 'Python Programming',   code: 'PY-2024',  description: 'Programação em Python desde fundamentos até aplicações práticas com bibliotecas populares de data science.',   total_hours: 180, is_active: true,  created_at: '2024-02-01T08:00:00Z', updated_at: '2024-02-01T08:00:00Z' },
  { id: 'crs-005', institution: INSTITUTION.id, institution_name: INSTITUTION.name, name: 'Cloud Computing',      code: 'CLD-2024', description: 'Fundamentos de computação em nuvem, AWS, Azure e Google Cloud. IaaS, PaaS e SaaS.',                           total_hours: 120, is_active: true,  created_at: '2024-03-01T08:00:00Z', updated_at: '2024-03-01T08:00:00Z' },
  { id: 'crs-006', institution: INSTITUTION.id, institution_name: INSTITUTION.name, name: 'Digital Marketing',    code: 'MKT-2023', description: 'Marketing digital, SEO, SEM, redes sociais e análise de métricas.',                                           total_hours: 80,  is_active: false, created_at: '2023-09-01T08:00:00Z', updated_at: '2024-01-10T08:00:00Z' },
];

const COURSE_SUMMARY = (id) => {
  const c = COURSES.find(x => x.id === id);
  return c ? { id: c.id, name: c.name, code: c.code, total_hours: c.total_hours } : null;
};
const TRAINER_SUMMARY = (id) => {
  const t = TRAINERS.find(x => x.id === id);
  return t ? { id: t.id, full_name: t.full_name, specialization: t.specialization } : null;
};

let CLASSES = [
  { id: 'cls-001', institution: INSTITUTION.id, institution_name: INSTITUTION.name, course: COURSE_SUMMARY('crs-001'), trainer: TRAINER_SUMMARY('trn-001'), name: 'Web Development — Turma A',     status: 'in_progress', start_date: '2024-03-01', end_date: '2024-08-30', enrollment_count: 4, created_at: '2024-02-15T08:00:00Z', updated_at: '2024-03-01T08:00:00Z' },
  { id: 'cls-002', institution: INSTITUTION.id, institution_name: INSTITUTION.name, course: COURSE_SUMMARY('crs-002'), trainer: TRAINER_SUMMARY('trn-002'), name: 'Database Design — Turma A',   status: 'open',        start_date: '2024-05-01', end_date: '2024-09-30', enrollment_count: 3, created_at: '2024-04-01T08:00:00Z', updated_at: '2024-04-01T08:00:00Z' },
  { id: 'cls-003', institution: INSTITUTION.id, institution_name: INSTITUTION.name, course: COURSE_SUMMARY('crs-003'), trainer: TRAINER_SUMMARY('trn-003'), name: 'Networking — Turma A',         status: 'open',        start_date: '2024-06-01', end_date: '2024-11-30', enrollment_count: 2, created_at: '2024-05-01T08:00:00Z', updated_at: '2024-05-01T08:00:00Z' },
  { id: 'cls-004', institution: INSTITUTION.id, institution_name: INSTITUTION.name, course: COURSE_SUMMARY('crs-004'), trainer: TRAINER_SUMMARY('trn-001'), name: 'Python Basics — Turma A',      status: 'closed',      start_date: '2024-01-15', end_date: '2024-04-30', enrollment_count: 5, created_at: '2024-01-10T08:00:00Z', updated_at: '2024-05-01T08:00:00Z' },
  { id: 'cls-005', institution: INSTITUTION.id, institution_name: INSTITUTION.name, course: COURSE_SUMMARY('crs-001'), trainer: TRAINER_SUMMARY('trn-001'), name: 'Web Development — Turma B',     status: 'open',        start_date: '2024-07-01', end_date: '2024-12-31', enrollment_count: 0, created_at: '2024-06-01T08:00:00Z', updated_at: '2024-06-01T08:00:00Z' },
];

let ENROLLMENTS = [
  { id: 'enr-001', class_instance: 'cls-001', student: { id: 'stu-001', full_name: 'Ana Luísa Ferreira', student_code: 'EST-2024-001' }, status: 'active',    enrolled_at: '2024-03-01T08:00:00Z', updated_at: '2024-03-01T08:00:00Z', class_name: 'Web Development — Turma A', course_name: 'Web Development', trainer_name: 'Prof. José Cardoso' },
  { id: 'enr-002', class_instance: 'cls-001', student: { id: 'stu-002', full_name: 'Carlos Manuel Silva',  student_code: 'EST-2024-002' }, status: 'active',    enrolled_at: '2024-03-01T08:00:00Z', updated_at: '2024-03-01T08:00:00Z', class_name: 'Web Development — Turma A', course_name: 'Web Development', trainer_name: 'Prof. José Cardoso' },
  { id: 'enr-003', class_instance: 'cls-001', student: { id: 'stu-003', full_name: 'Beatriz Neto Costa',   student_code: 'EST-2024-003' }, status: 'active',    enrolled_at: '2024-03-05T08:00:00Z', updated_at: '2024-03-05T08:00:00Z', class_name: 'Web Development — Turma A', course_name: 'Web Development', trainer_name: 'Prof. José Cardoso' },
  { id: 'enr-004', class_instance: 'cls-001', student: { id: 'stu-004', full_name: 'David António Lopes',  student_code: 'EST-2024-004' }, status: 'dropped',   enrolled_at: '2024-03-01T08:00:00Z', updated_at: '2024-04-10T08:00:00Z', class_name: 'Web Development — Turma A', course_name: 'Web Development', trainer_name: 'Prof. José Cardoso' },
  { id: 'enr-005', class_instance: 'cls-002', student: { id: 'stu-001', full_name: 'Ana Luísa Ferreira',  student_code: 'EST-2024-001' }, status: 'active',    enrolled_at: '2024-05-01T08:00:00Z', updated_at: '2024-05-01T08:00:00Z', class_name: 'Database Design — Turma A', course_name: 'Database Design', trainer_name: 'Dra. Maria Conceição' },
  { id: 'enr-006', class_instance: 'cls-002', student: { id: 'stu-002', full_name: 'Carlos Manuel Silva', student_code: 'EST-2024-002' }, status: 'active',    enrolled_at: '2024-05-01T08:00:00Z', updated_at: '2024-05-01T08:00:00Z', class_name: 'Database Design — Turma A', course_name: 'Database Design', trainer_name: 'Dra. Maria Conceição' },
  { id: 'enr-007', class_instance: 'cls-004', student: { id: 'stu-001', full_name: 'Ana Luísa Ferreira',  student_code: 'EST-2024-001' }, status: 'completed', enrolled_at: '2024-01-15T08:00:00Z', updated_at: '2024-05-01T08:00:00Z', class_name: 'Python Basics — Turma A',      course_name: 'Python Programming', trainer_name: 'Prof. José Cardoso' },
];

let GRADES = [
  { id: 'grd-001', institution: INSTITUTION.id, enrollment: 'enr-001', student_name: 'Ana Luísa Ferreira', student_code: 'EST-2024-001', class_name: 'Web Development — Turma A', course_name: 'Web Development', assessment_type: 'continuous', value: '15.00', max_value: '20.00', assessed_at: '2024-04-15', notes: 'Excelente participação.',        created_at: '2024-04-15T10:00:00Z', updated_at: '2024-04-15T10:00:00Z' },
  { id: 'grd-002', institution: INSTITUTION.id, enrollment: 'enr-001', student_name: 'Ana Luísa Ferreira', student_code: 'EST-2024-001', class_name: 'Web Development — Turma A', course_name: 'Web Development', assessment_type: 'exam',       value: '17.50', max_value: '20.00', assessed_at: '2024-05-20', notes: '',                             created_at: '2024-05-20T10:00:00Z', updated_at: '2024-05-20T10:00:00Z' },
  { id: 'grd-003', institution: INSTITUTION.id, enrollment: 'enr-002', student_name: 'Carlos Manuel Silva', student_code: 'EST-2024-002', class_name: 'Web Development — Turma A', course_name: 'Web Development', assessment_type: 'continuous', value: '12.00', max_value: '20.00', assessed_at: '2024-04-15', notes: '',                             created_at: '2024-04-15T10:00:00Z', updated_at: '2024-04-15T10:00:00Z' },
  { id: 'grd-004', institution: INSTITUTION.id, enrollment: 'enr-002', student_name: 'Carlos Manuel Silva', student_code: 'EST-2024-002', class_name: 'Web Development — Turma A', course_name: 'Web Development', assessment_type: 'exam',       value: '13.00', max_value: '20.00', assessed_at: '2024-05-20', notes: 'Melhorou bastante.',          created_at: '2024-05-20T10:00:00Z', updated_at: '2024-05-20T10:00:00Z' },
  { id: 'grd-005', institution: INSTITUTION.id, enrollment: 'enr-003', student_name: 'Beatriz Neto Costa',  student_code: 'EST-2024-003', class_name: 'Web Development — Turma A', course_name: 'Web Development', assessment_type: 'continuous', value: '18.00', max_value: '20.00', assessed_at: '2024-04-15', notes: 'Trabalho exemplar.',         created_at: '2024-04-15T10:00:00Z', updated_at: '2024-04-15T10:00:00Z' },
  { id: 'grd-006', institution: INSTITUTION.id, enrollment: 'enr-007', student_name: 'Ana Luísa Ferreira', student_code: 'EST-2024-001', class_name: 'Python Basics — Turma A',      course_name: 'Python Programming', assessment_type: 'exam',       value: '16.00', max_value: '20.00', assessed_at: '2024-04-20', notes: '',                             created_at: '2024-04-20T10:00:00Z', updated_at: '2024-04-20T10:00:00Z' },
  { id: 'grd-007', institution: INSTITUTION.id, enrollment: 'enr-007', student_name: 'Ana Luísa Ferreira', student_code: 'EST-2024-001', class_name: 'Python Basics — Turma A',      course_name: 'Python Programming', assessment_type: 'project',    value: '19.00', max_value: '20.00', assessed_at: '2024-04-28', notes: 'Projecto excelente.',       created_at: '2024-04-28T10:00:00Z', updated_at: '2024-04-28T10:00:00Z' },
];

// ── Report builder ─────────────────────────────────────────────────
function buildReport(classId) {
  const classEnrollments = ENROLLMENTS.filter(e => e.class_instance === classId);
  return classEnrollments.map(enr => {
    const gradeList = GRADES.filter(g => g.enrollment === enr.id);
    const sum = gradeList.reduce((acc, g) => {
      const val = parseFloat(g.value);
      const max = parseFloat(g.max_value);
      return acc + (val / max) * 20;
    }, 0);
    const avg = gradeList.length ? (sum / gradeList.length).toFixed(2) : '0.00';
    return {
      enrollment_id:     enr.id,
      enrollment_status: enr.status,
      student:           enr.student,
      grades:            gradeList.map(g => ({
        id:              g.id,
        assessment_type: g.assessment_type,
        value:           g.value,
        max_value:       g.max_value,
        assessed_at:     g.assessed_at,
        notes:           g.notes,
      })),
      average: avg,
    };
  });
}

// ══════════════════════════════════════════════════════════════════
//  MOCK API MODULES
// ══════════════════════════════════════════════════════════════════

export const auth = {
  async login(email, _password) {
    await delay();
    const mockUser = { ...MOCK_USER, email };
    token.set('mock-access-token', 'mock-refresh-token', mockUser);
    return { access: 'mock-access-token', refresh: 'mock-refresh-token', user: mockUser };
  },
  async logout() {
    token.clear();
    window.location.href = '../pages/login.html';
  },
  async me() {
    await delay(200);
    return token.getUser();
  },
  async changePassword(_old, _new) {
    await delay(300);
    return { detail: 'Password updated successfully.' };
  },
};

export const institutions = {
  async me() {
    await delay(200);
    return { ...INSTITUTION };
  },
  async update(data) {
    await delay(300);
    Object.assign(INSTITUTION, data);
    return { ...INSTITUTION };
  },
};

export const students = {
  async list(params = {}) {
    await delay();
    let results = [...STUDENTS];
    if (params.search) {
      const q = params.search.toLowerCase();
      results = results.filter(s =>
        s.full_name.toLowerCase().includes(q) ||
        s.student_code.toLowerCase().includes(q)
      );
    }
    if (params.is_active !== undefined && params.is_active !== '') {
      const active = params.is_active === 'true' || params.is_active === true;
      results = results.filter(s => s.is_active === active);
    }
    return paginate(results, params);
  },
  async get(id) {
    await delay(200);
    const s = STUDENTS.find(s => s.id === id);
    if (!s) throw Object.assign(new Error('Student not found.'), { status: 404 });
    return { ...s };
  },
  async create(data) {
    await delay(350);
    const student = {
      id:          uuid(),
      institution: INSTITUTION.id,
      is_active:   true,
      enrolled_at: new Date().toISOString(),
      updated_at:  new Date().toISOString(),
      phone:       '',
      address:     '',
      birth_date:  null,
      ...data,
    };
    STUDENTS.push(student);
    return { ...student };
  },
  async update(id, data) {
    await delay(300);
    const idx = STUDENTS.findIndex(s => s.id === id);
    if (idx === -1) throw Object.assign(new Error('Student not found.'), { status: 404 });
    STUDENTS[idx] = { ...STUDENTS[idx], ...data, updated_at: new Date().toISOString() };
    return { ...STUDENTS[idx] };
  },
  async deactivate(id) {
    await delay(300);
    const idx = STUDENTS.findIndex(s => s.id === id);
    if (idx !== -1) STUDENTS[idx].is_active = false;
    return null;
  },
  async me() {
    await delay(200);
    return { ...STUDENTS[0], institution_name: INSTITUTION.name };
  },
};

export const trainers = {
  async list(params = {}) {
    await delay();
    let results = [...TRAINERS];
    if (params.search) {
      const q = params.search.toLowerCase();
      results = results.filter(t =>
        t.full_name.toLowerCase().includes(q) ||
        t.specialization.toLowerCase().includes(q)
      );
    }
    if (params.is_active !== undefined && params.is_active !== '') {
      const active = params.is_active === 'true' || params.is_active === true;
      results = results.filter(t => t.is_active === active);
    }
    return paginate(results, params);
  },
  async get(id) {
    await delay(200);
    const t = TRAINERS.find(t => t.id === id);
    if (!t) throw Object.assign(new Error('Trainer not found.'), { status: 404 });
    return { ...t };
  },
  async create(data) {
    await delay(350);
    const trainer = {
      id:          uuid(),
      institution: INSTITUTION.id,
      is_active:   true,
      hired_at:    new Date().toISOString(),
      updated_at:  new Date().toISOString(),
      phone:       '',
      bio:         '',
      specialization: '',
      ...data,
    };
    TRAINERS.push(trainer);
    return { ...trainer };
  },
  async update(id, data) {
    await delay(300);
    const idx = TRAINERS.findIndex(t => t.id === id);
    if (idx === -1) throw Object.assign(new Error('Trainer not found.'), { status: 404 });
    if (data.is_active !== undefined) data.is_active = data.is_active === true || data.is_active === 'true';
    TRAINERS[idx] = { ...TRAINERS[idx], ...data, updated_at: new Date().toISOString() };
    return { ...TRAINERS[idx] };
  },
  async deactivate(id) {
    await delay(300);
    const idx = TRAINERS.findIndex(t => t.id === id);
    if (idx !== -1) TRAINERS[idx].is_active = false;
    return null;
  },
  async me() {
    await delay(200);
    return { ...TRAINERS[0], institution_name: INSTITUTION.name };
  },
  async classes(id) {
    await delay(300);
    const trainerClasses = CLASSES.filter(c => c.trainer?.id === id);
    return paginate(trainerClasses);
  },
};

export const courses = {
  async list(params = {}) {
    await delay();
    let results = [...COURSES];
    if (params.search) {
      const q = params.search.toLowerCase();
      results = results.filter(c =>
        c.name.toLowerCase().includes(q) ||
        c.code.toLowerCase().includes(q)
      );
    }
    if (params.is_active !== undefined && params.is_active !== '') {
      const active = params.is_active === 'true' || params.is_active === true;
      results = results.filter(c => c.is_active === active);
    }
    return paginate(results, params);
  },
  async get(id) {
    await delay(200);
    const c = COURSES.find(c => c.id === id);
    if (!c) throw Object.assign(new Error('Course not found.'), { status: 404 });
    return { ...c };
  },
  async create(data) {
    await delay(350);
    const course = {
      id:              uuid(),
      institution:     INSTITUTION.id,
      institution_name: INSTITUTION.name,
      is_active:       true,
      created_at:      new Date().toISOString(),
      updated_at:      new Date().toISOString(),
      description:     '',
      total_hours:     0,
      ...data,
      code: (data.code ?? '').toUpperCase(),
    };
    COURSES.push(course);
    return { ...course };
  },
  async update(id, data) {
    await delay(300);
    const idx = COURSES.findIndex(c => c.id === id);
    if (idx === -1) throw Object.assign(new Error('Course not found.'), { status: 404 });
    if (data.is_active !== undefined) data.is_active = data.is_active === true || data.is_active === 'true';
    COURSES[idx] = { ...COURSES[idx], ...data, updated_at: new Date().toISOString() };
    return { ...COURSES[idx] };
  },
  async deactivate(id) {
    await delay(300);
    const idx = COURSES.findIndex(c => c.id === id);
    if (idx !== -1) COURSES[idx].is_active = false;
    return null;
  },
  async classes(id) {
    await delay(300);
    return paginate(CLASSES.filter(c => c.course?.id === id));
  },
};

export const classes = {
  async list(params = {}) {
    await delay();
    let results = [...CLASSES];
    if (params.search) {
      const q = params.search.toLowerCase();
      results = results.filter(c => c.name.toLowerCase().includes(q));
    }
    if (params.status) results = results.filter(c => c.status === params.status);
    if (params.course_id)  results = results.filter(c => c.course?.id  === params.course_id);
    if (params.trainer_id) results = results.filter(c => c.trainer?.id === params.trainer_id);
    return paginate(results, params);
  },
  async get(id) {
    await delay(200);
    const c = CLASSES.find(c => c.id === id);
    if (!c) throw Object.assign(new Error('Class not found.'), { status: 404 });
    const enrollments = ENROLLMENTS.filter(e => e.class_instance === id && e.status === 'active');
    return {
      ...c,
      enrollments: enrollments.map(e => ({
        id: e.id, student: e.student, status: e.status, enrolled_at: e.enrolled_at, updated_at: e.updated_at,
      })),
    };
  },
  async create(data) {
    await delay(400);
    const course  = COURSES.find(c => c.id === data.course_id);
    const trainer = TRAINERS.find(t => t.id === data.trainer_id);
    const cls = {
      id:               uuid(),
      institution:      INSTITUTION.id,
      institution_name: INSTITUTION.name,
      course:           course ? COURSE_SUMMARY(course.id) : null,
      trainer:          trainer ? TRAINER_SUMMARY(trainer.id) : null,
      status:           'open',
      enrollment_count: 0,
      created_at:       new Date().toISOString(),
      updated_at:       new Date().toISOString(),
      name:             data.name,
      start_date:       data.start_date,
      end_date:         data.end_date,
    };
    CLASSES.push(cls);
    return { ...cls };
  },
  async update(id, data) {
    await delay(300);
    const idx = CLASSES.findIndex(c => c.id === id);
    if (idx === -1) throw Object.assign(new Error('Class not found.'), { status: 404 });
    if (data.trainer_id) {
      const trainer = TRAINERS.find(t => t.id === data.trainer_id);
      if (trainer) { CLASSES[idx].trainer = TRAINER_SUMMARY(trainer.id); }
      delete data.trainer_id;
    }
    CLASSES[idx] = { ...CLASSES[idx], ...data, updated_at: new Date().toISOString() };
    return { ...CLASSES[idx] };
  },
  async delete(id) {
    await delay(300);
    const cls = CLASSES.find(c => c.id === id);
    if (cls?.enrollment_count > 0)
      throw Object.assign(new Error('Cannot delete a class with enrolled students. Close it instead.'), { status: 400 });
    CLASSES = CLASSES.filter(c => c.id !== id);
    return null;
  },
  async close(id) {
    await delay(400);
    const idx = CLASSES.findIndex(c => c.id === id);
    if (idx === -1) throw Object.assign(new Error('Class not found.'), { status: 404 });
    if (CLASSES[idx].status === 'closed')
      throw Object.assign(new Error('Class is already closed.'), { status: 400 });
    CLASSES[idx].status = 'closed';
    ENROLLMENTS.filter(e => e.class_instance === id && e.status === 'active')
      .forEach(e => { e.status = 'completed'; });
    return { ...CLASSES[idx] };
  },
  enrollments: {
    async list(classId, params = {}) {
      await delay(300);
      let results = ENROLLMENTS.filter(e => e.class_instance === classId);
      if (params.status) results = results.filter(e => e.status === params.status);
      return paginate(results, params);
    },
    async enroll(classId, studentId) {
      await delay(350);
      const cls = CLASSES.find(c => c.id === classId);
      if (!cls || cls.status !== 'open')
        throw Object.assign(new Error('Cannot enroll in a class that is not open.'), { status: 400 });
      const already = ENROLLMENTS.find(e => e.class_instance === classId && e.student.id === studentId);
      if (already)
        throw Object.assign(new Error('This student is already enrolled in this class.'), { status: 400 });
      const student = STUDENTS.find(s => s.id === studentId);
      const enrollment = {
        id:             uuid(),
        class_instance: classId,
        student:        { id: student.id, full_name: student.full_name, student_code: student.student_code },
        status:         'active',
        enrolled_at:    new Date().toISOString(),
        updated_at:     new Date().toISOString(),
        class_name:     cls.name,
        course_name:    cls.course?.name ?? '',
        trainer_name:   cls.trainer?.full_name ?? '',
      };
      ENROLLMENTS.push(enrollment);
      const clsIdx = CLASSES.findIndex(c => c.id === classId);
      if (clsIdx !== -1) CLASSES[clsIdx].enrollment_count++;
      return { ...enrollment };
    },
    async drop(classId, enrollmentId) {
      await delay(300);
      const idx = ENROLLMENTS.findIndex(e => e.id === enrollmentId);
      if (idx === -1) throw Object.assign(new Error('Enrollment not found.'), { status: 404 });
      if (ENROLLMENTS[idx].status === 'completed')
        throw Object.assign(new Error('Cannot drop a completed enrollment.'), { status: 400 });
      ENROLLMENTS[idx].status = 'dropped';
      const clsIdx = CLASSES.findIndex(c => c.id === classId);
      if (clsIdx !== -1 && CLASSES[clsIdx].enrollment_count > 0) CLASSES[clsIdx].enrollment_count--;
      return null;
    },
  },
  async myEnrollments(params = {}) {
    await delay(300);
    let results = ENROLLMENTS.filter(e => e.student.id === 'stu-001');
    if (params.status) results = results.filter(e => e.status === params.status);
    return paginate(results, params);
  },
};

export const grades = {
  async list(params = {}) {
    await delay();
    let results = [...GRADES];
    if (params.enrollment_id)   results = results.filter(g => g.enrollment === params.enrollment_id);
    if (params.class_id)        results = results.filter(g => ENROLLMENTS.find(e => e.id === g.enrollment)?.class_instance === params.class_id);
    if (params.student_id)      results = results.filter(g => ENROLLMENTS.find(e => e.id === g.enrollment)?.student?.id === params.student_id);
    if (params.assessment_type) results = results.filter(g => g.assessment_type === params.assessment_type);
    return paginate(results, params);
  },
  async get(id) {
    await delay(200);
    const g = GRADES.find(g => g.id === id);
    if (!g) throw Object.assign(new Error('Grade not found.'), { status: 404 });
    return { ...g };
  },
  async launch(data) {
    await delay(400);
    const existing = GRADES.find(g => g.enrollment === data.enrollment_id && g.assessment_type === data.assessment_type);
    if (existing)
      throw Object.assign(new Error(`A grade of type "${data.assessment_type}" already exists for this enrollment.`), { status: 400 });
    const enr = ENROLLMENTS.find(e => e.id === data.enrollment_id);
    const grade = {
      id:              uuid(),
      institution:     INSTITUTION.id,
      enrollment:      data.enrollment_id,
      student_name:    enr?.student?.full_name  ?? '',
      student_code:    enr?.student?.student_code ?? '',
      class_name:      enr?.class_name  ?? '',
      course_name:     enr?.course_name ?? '',
      assessment_type: data.assessment_type,
      value:           String(data.value),
      max_value:       String(data.max_value),
      assessed_at:     data.assessed_at,
      notes:           data.notes ?? '',
      created_at:      new Date().toISOString(),
      updated_at:      new Date().toISOString(),
    };
    GRADES.push(grade);
    return { ...grade };
  },
  async update(id, data) {
    await delay(300);
    const idx = GRADES.findIndex(g => g.id === id);
    if (idx === -1) throw Object.assign(new Error('Grade not found.'), { status: 404 });
    GRADES[idx] = { ...GRADES[idx], ...data, updated_at: new Date().toISOString() };
    return { ...GRADES[idx] };
  },
  async delete(id) {
    await delay(300);
    GRADES = GRADES.filter(g => g.id !== id);
    return null;
  },
  async report(classId) {
    await delay(500);
    return buildReport(classId);
  },
  async myGrades() {
    await delay(400);
    const myEnrollments = ENROLLMENTS.filter(e => e.student.id === 'stu-001');
    const grouped = {};
    myEnrollments.forEach(enr => {
      const gradeList = GRADES.filter(g => g.enrollment === enr.id);
      const sum = gradeList.reduce((acc, g) => acc + (parseFloat(g.value) / parseFloat(g.max_value)) * 20, 0);
      const avg = gradeList.length ? (sum / gradeList.length).toFixed(2) : null;
      grouped[enr.class_instance] = {
        class_id:     enr.class_instance,
        class_name:   enr.class_name,
        course_name:  enr.course_name,
        trainer_name: enr.trainer_name,
        grades:       gradeList.map(g => ({
          id: g.id, assessment_type: g.assessment_type,
          value: g.value, max_value: g.max_value,
          assessed_at: g.assessed_at,
          class_name: g.class_name, course_name: g.course_name, trainer_name: enr.trainer_name,
        })),
        average: avg,
      };
    });
    return Object.values(grouped);
  },
  async byEnrollment(enrollmentId) {
    await delay(300);
    return paginate(GRADES.filter(g => g.enrollment === enrollmentId));
  },
};

export function apiFetch() {
  throw new Error('apiFetch is not available in mock mode. Use the specific resource modules.');
}
