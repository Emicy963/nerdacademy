/**
 * i18n.js — lightweight translation module
 * Primary language: Portuguese (pt)
 * Secondary: English (en)
 *
 * Usage:
 *   import { t, setLocale, getLocale, applyTranslations } from './i18n.js';
 *   applyTranslations();   // on DOMContentLoaded
 *   setLocale('en');       // switch language
 */

const TRANSLATIONS = {
  pt: {
    // ── Navbar ──────────────────────────────────────────
    'nav.features':   'Funcionalidades',
    'nav.how':        'Como funciona',
    'nav.pricing':    'Preços',
    'nav.login':      'Entrar',
    'nav.demo':       'Ver demonstração',

    // ── Hero ────────────────────────────────────────────
    'hero.badge':     'Plataforma académica para Angola',
    'hero.title':     'Gerencie a sua instituição com <em>clareza</em>',
    'hero.subtitle':  'O Acadêmico centraliza alunos, formadores, cursos, turmas e notas numa única plataforma — desenhada para centros de formação técnica angolanos.',
    'hero.cta':       'Começar agora',
    'hero.cta.demo':  'Ver demonstração',
    'hero.trusted':   'Utilizado por centros de formação técnica em Angola',

    // ── Features ────────────────────────────────────────
    'features.badge':     'Funcionalidades',
    'features.title':     'Tudo o que precisa para gerir a sua instituição',
    'features.subtitle':  'Da matrícula à avaliação final, o Acadêmico cobre todo o ciclo académico.',

    'feat.students.title':  'Gestão de Alunos',
    'feat.students.desc':   'Registe e acompanhe todos os seus alunos, gere códigos automáticos, controle presenças e muito mais.',
    'feat.trainers.title':  'Gestão de Formadores',
    'feat.trainers.desc':   'Associe formadores a turmas, gira perfis e acesso ao sistema com total controlo de permissões.',
    'feat.courses.title':   'Cursos e Turmas',
    'feat.courses.desc':    'Crie cursos, abra turmas, faça matrículas e acompanhe o progresso em tempo real.',
    'feat.grades.title':    'Notas e Avaliações',
    'feat.grades.desc':     'Registe exames, testes e trabalhos. Calcule médias automaticamente e gere relatórios de desempenho.',
    'feat.multi.title':     'Multi-instituição',
    'feat.multi.desc':      'Um único utilizador pode pertencer a várias instituições. Mude de contexto com um clique.',
    'feat.secure.title':    'Segurança e Acessos',
    'feat.secure.desc':     'Controlo de acessos por função (admin, formador, aluno) com autenticação JWT e tokens de actualização.',

    // ── How it works ────────────────────────────────────
    'how.badge':       'Como funciona',
    'how.title':       'Operacional em minutos',
    'how.subtitle':    'Sem instalações complexas. Sem configurações intermináveis.',

    'how.step1.num':   '01',
    'how.step1.title': 'Crie a sua instituição',
    'how.step1.desc':  'Registe a sua instituição, defina o prefixo de códigos e configure os dados básicos.',
    'how.step2.num':   '02',
    'how.step2.title': 'Adicione alunos e formadores',
    'how.step2.desc':  'Importe ou crie manualmente. Palavras-passe temporárias são geradas e enviadas por email automaticamente.',
    'how.step3.num':   '03',
    'how.step3.title': 'Comece a gerir',
    'how.step3.desc':  'Abra turmas, realize matrículas, submeta notas e acompanhe o desempenho no dashboard.',

    // ── CTA band ────────────────────────────────────────
    'cta.title':    'Pronto para modernizar a sua gestão académica?',
    'cta.subtitle': 'Comece hoje. Sem cartão de crédito necessário.',
    'cta.btn':      'Criar conta gratuita',

    // ── Footer ──────────────────────────────────────────
    'footer.tagline':    'Gestão académica simples e eficaz para Angola.',
    'footer.product':    'Produto',
    'footer.features':   'Funcionalidades',
    'footer.pricing':    'Preços',
    'footer.changelog':  'Novidades',
    'footer.company':    'Empresa',
    'footer.about':      'Sobre nós',
    'footer.contact':    'Contacto',
    'footer.privacy':    'Privacidade',
    'footer.legal':      'Termos de Uso',
    'footer.copyright':  '© 2026 PyNerd Development. Todos os direitos reservados.',
  },

  en: {
    // ── Navbar ──────────────────────────────────────────
    'nav.features':   'Features',
    'nav.how':        'How it works',
    'nav.pricing':    'Pricing',
    'nav.login':      'Sign in',
    'nav.demo':       'See demo',

    // ── Hero ────────────────────────────────────────────
    'hero.badge':     'Academic platform for Angola',
    'hero.title':     'Manage your institution with <em>clarity</em>',
    'hero.subtitle':  'Acadêmico centralises students, trainers, courses, classes and grades in one platform — designed for Angolan technical training centres.',
    'hero.cta':       'Get started',
    'hero.cta.demo':  'See demo',
    'hero.trusted':   'Used by technical training centres in Angola',

    // ── Features ────────────────────────────────────────
    'features.badge':     'Features',
    'features.title':     'Everything you need to manage your institution',
    'features.subtitle':  'From enrolment to final assessment, Acadêmico covers the full academic cycle.',

    'feat.students.title':  'Student Management',
    'feat.students.desc':   'Register and track all your students, auto-generate codes, manage attendance and more.',
    'feat.trainers.title':  'Trainer Management',
    'feat.trainers.desc':   'Assign trainers to classes, manage profiles and system access with full permission control.',
    'feat.courses.title':   'Courses & Classes',
    'feat.courses.desc':    'Create courses, open classes, enrol students and track progress in real time.',
    'feat.grades.title':    'Grades & Assessments',
    'feat.grades.desc':     'Record exams, tests and assignments. Auto-calculate averages and generate performance reports.',
    'feat.multi.title':     'Multi-institution',
    'feat.multi.desc':      'A single user can belong to multiple institutions. Switch context with one click.',
    'feat.secure.title':    'Security & Access',
    'feat.secure.desc':     'Role-based access control (admin, trainer, student) with JWT authentication and refresh tokens.',

    // ── How it works ────────────────────────────────────
    'how.badge':       'How it works',
    'how.title':       'Up and running in minutes',
    'how.subtitle':    'No complex installations. No endless configuration.',

    'how.step1.num':   '01',
    'how.step1.title': 'Create your institution',
    'how.step1.desc':  'Register your institution, set the code prefix and configure the basic details.',
    'how.step2.num':   '02',
    'how.step2.title': 'Add students and trainers',
    'how.step2.desc':  'Import or create manually. Temporary passwords are auto-generated and emailed instantly.',
    'how.step3.num':   '03',
    'how.step3.title': 'Start managing',
    'how.step3.desc':  'Open classes, enrol students, submit grades and track performance on the dashboard.',

    // ── CTA band ────────────────────────────────────────
    'cta.title':    'Ready to modernise your academic management?',
    'cta.subtitle': 'Start today. No credit card required.',
    'cta.btn':      'Create free account',

    // ── Footer ──────────────────────────────────────────
    'footer.tagline':    'Simple and effective academic management for Angola.',
    'footer.product':    'Product',
    'footer.features':   'Features',
    'footer.pricing':    'Pricing',
    'footer.changelog':  "What's new",
    'footer.company':    'Company',
    'footer.about':      'About us',
    'footer.contact':    'Contact',
    'footer.privacy':    'Privacy',
    'footer.legal':      'Terms of Use',
    'footer.copyright':  '© 2026 PyNerd Development. All rights reserved.',
  },
};

const STORAGE_KEY = 'academico_locale';
const SUPPORTED   = ['pt', 'en'];
const DEFAULT     = 'pt';

export function getLocale() {
  const stored = localStorage.getItem(STORAGE_KEY);
  return SUPPORTED.includes(stored) ? stored : DEFAULT;
}

export function setLocale(lang) {
  if (!SUPPORTED.includes(lang)) return;
  localStorage.setItem(STORAGE_KEY, lang);
  document.documentElement.lang = lang;
  applyTranslations();
  dispatchLocaleChange(lang);
}

export function t(key) {
  const locale = getLocale();
  return TRANSLATIONS[locale]?.[key] ?? TRANSLATIONS[DEFAULT]?.[key] ?? key;
}

export function applyTranslations() {
  const locale = getLocale();
  document.documentElement.lang = locale;

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    const val = TRANSLATIONS[locale]?.[key] ?? TRANSLATIONS[DEFAULT]?.[key];
    if (val !== undefined) el.innerHTML = val;
  });

  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const key = el.dataset.i18nPlaceholder;
    const val = TRANSLATIONS[locale]?.[key] ?? TRANSLATIONS[DEFAULT]?.[key];
    if (val !== undefined) el.placeholder = val;
  });

  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const key = el.dataset.i18nTitle;
    const val = TRANSLATIONS[locale]?.[key] ?? TRANSLATIONS[DEFAULT]?.[key];
    if (val !== undefined) el.title = val;
  });

  // Mark active language on switcher buttons
  document.querySelectorAll('[data-lang-btn]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.langBtn === locale);
  });
}

function dispatchLocaleChange(lang) {
  window.dispatchEvent(new CustomEvent('localechange', { detail: { lang } }));
}
