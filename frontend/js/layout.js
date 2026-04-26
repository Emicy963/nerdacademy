import { session, auth } from './api.js';
import { t, applyTranslations, getLocale, setLocale } from './i18n.js';

// ── Nav items ─────────────────────────────────────────────────────
const NAV_ITEMS = [
  {
    sectionKey: 'nav.section.overview',
    items: [
      { id: 'dashboard', labelKey: 'nav.item.dashboard', icon: 'dashboard',
        href: '/pages/dashboard.html', roles: ['admin', 'trainer', 'student'] },
    ]
  },
  {
    sectionKey: 'nav.section.management',
    items: [
      { id: 'students', labelKey: 'nav.item.students', icon: 'students',
        href: '/pages/students.html',  roles: ['admin', 'trainer'] },
      { id: 'trainers', labelKey: 'nav.item.trainers', icon: 'trainers',
        href: '/pages/trainers.html',  roles: ['admin'] },
      { id: 'courses',  labelKey: 'nav.item.courses',  icon: 'courses',
        href: '/pages/courses.html',   roles: ['admin', 'trainer', 'student'] },
      { id: 'classes',  labelKey: 'nav.item.classes',  icon: 'classes',
        href: '/pages/classes.html',   roles: ['admin', 'trainer', 'student'] },
    ]
  },
  {
    sectionKey: 'nav.section.academic',
    items: [
      { id: 'grades', labelKey: 'nav.item.grades', icon: 'grades',
        href: '/pages/grades.html', roles: ['admin', 'trainer', 'student'] },
    ]
  },
];

// ── Render sidebar nav ────────────────────────────────────────────
export function renderNav(activeId, userRole = 'admin') {
  const navEl = document.getElementById('sidebar-nav');
  if (!navEl) return;

  navEl.innerHTML = NAV_ITEMS.map(section => {
    const visible = section.items.filter(item => item.roles.includes(userRole));
    if (!visible.length) return '';

    return `
      <div class="sidebar__section">
        <div class="sidebar__section-label">${t(section.sectionKey)}</div>
        ${visible.map(item => `
          <a href="${item.href}"
             class="nav-item ${item.id === activeId ? 'active' : ''}"
             data-nav-id="${item.id}">
            <svg class="nav-item__icon" aria-hidden="true">
              <use href="#icon-${item.icon}"/>
            </svg>
            ${t(item.labelKey)}
          </a>`).join('')}
      </div>`;
  }).join('');
}

// ── Inject language switcher into topbar ─────────────────────────
function injectLangSwitcher() {
  const actions = document.querySelector('.topbar__actions');
  if (!actions || actions.querySelector('.topbar-lang-switcher')) return;

  const locale = getLocale();
  const switcher = document.createElement('div');
  switcher.className = 'topbar-lang-switcher';
  switcher.setAttribute('role', 'group');
  switcher.setAttribute('aria-label', 'Idioma / Language');
  switcher.style.cssText = [
    'display:flex', 'align-items:center',
    'background:var(--bg-raised)', 'border:1px solid var(--border-default)',
    'border-radius:5px', 'overflow:hidden', 'margin-right:4px',
  ].join(';');

  ['pt', 'en'].forEach(lang => {
    const btn = document.createElement('button');
    btn.dataset.langBtn = lang;
    btn.textContent = lang.toUpperCase();
    btn.style.cssText = [
      'background:none', 'border:none', 'cursor:pointer',
      `padding:4px 8px`, 'font-family:var(--font-ui)', 'font-size:11px', 'font-weight:600',
      `color:${locale === lang ? 'var(--text-primary)' : 'var(--text-tertiary)'}`,
      `background:${locale === lang ? 'var(--bg-canvas)' : 'transparent'}`,
      'transition:all 120ms ease', 'letter-spacing:0.03em',
    ].join(';');

    btn.addEventListener('click', () => {
      setLocale(lang);
      const activeNavId = document.querySelector('.nav-item.active')?.dataset?.navId ?? '';
      const user = session.getUserWithRole();
      if (user) renderNav(activeNavId, user.role);
    });

    switcher.appendChild(btn);
  });

  window.addEventListener('localechange', ({ detail }) => {
    switcher.querySelectorAll('button').forEach(b => {
      const active = b.dataset.langBtn === detail.lang;
      b.style.color      = active ? 'var(--text-primary)' : 'var(--text-tertiary)';
      b.style.background = active ? 'var(--bg-canvas)'    : 'transparent';
    });
  });

  actions.insertBefore(switcher, actions.firstChild);
}

// ── Render user info in sidebar footer ────────────────────────────
export function renderUser(user) {
  const nameEl   = document.getElementById('sidebar-user-name');
  const roleEl   = document.getElementById('sidebar-user-role');
  const avatarEl = document.getElementById('sidebar-avatar');
  if (!nameEl) return;

  const displayName = user?.full_name?.trim()
    || (user?.email ? user.email.split('@')[0].replace(/[._]/g, ' ') : 'User');

  const initials = displayName.split(' ')
    .map(w => w[0]?.toUpperCase() ?? '')
    .slice(0, 2)
    .join('');

  const roleLabel = {
    admin:   t('ui.role.admin')   || 'Administrator',
    trainer: t('ui.role.trainer') || 'Trainer',
    student: t('ui.role.student') || 'Student',
  }[user?.role] ?? user?.role ?? '';

  nameEl.textContent  = displayName;
  roleEl.textContent  = roleLabel;
  if (avatarEl) avatarEl.textContent = initials;
}

// ── Breadcrumb ────────────────────────────────────────────────────
export function setBreadcrumb(items) {
  const el = document.getElementById('topbar-breadcrumb');
  if (!el) return;

  el.innerHTML = items.map((item, i) => {
    const sep = i > 0
      ? `<span class="topbar__breadcrumb-sep">
           <svg width="6" height="10" viewBox="0 0 6 10" fill="none">
             <path d="M1 1l4 4-4 4" stroke="currentColor" stroke-width="1.5"
                   stroke-linecap="round" stroke-linejoin="round"/>
           </svg>
         </span>`
      : '';
    const cls = i === items.length - 1 ? 'current' : '';
    return `${sep}<span class="topbar__breadcrumb-item ${cls}">${item.label}</span>`;
  }).join('');
}

// ── Mobile sidebar toggle ─────────────────────────────────────────
export function initMobileToggle() {
  const sidebar  = document.getElementById('sidebar');
  const menuBtn  = document.getElementById('menu-toggle');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (!menuBtn || !sidebar) return;

  const open  = () => { sidebar.classList.add('open');    backdrop?.classList.add('visible');    };
  const close = () => { sidebar.classList.remove('open'); backdrop?.classList.remove('visible'); };

  menuBtn.addEventListener('click', open);
  backdrop?.addEventListener('click', close);
}

// ── Logout ────────────────────────────────────────────────────────
export function initLogout() {
  const btn = document.getElementById('logout-btn');
  if (!btn) return;
  btn.title = t('nav.signout');
  btn.setAttribute('aria-label', t('nav.signout'));
  btn.addEventListener('click', () => auth.logout());
}

// ── Auth guard ────────────────────────────────────────────────────
export function requireAuth() {
  if (!session.isLoggedIn()) {
    window.location.href = '/pages/login.html';
    return null;
  }
  const user = session.getUserWithRole();
  if (!user) {
    window.location.href = '/pages/login.html';
    return null;
  }
  if (!user.role) {
    session.clear();
    window.location.href = '/pages/login.html';
    return null;
  }
  if (user.must_change_password && !window.location.pathname.includes('change-password')) {
    window.location.href = '/pages/change-password.html';
    return null;
  }
  return user;
}

// ── Institution switcher (for multi-membership users) ────────────
export function renderInstitutionSwitcher(containerId) {
  const container  = document.getElementById(containerId);
  if (!container) return;

  const memberships = session.getMemberships();
  if (memberships.length <= 1) { container.style.display = 'none'; return; }

  const active = session.getActiveMembership();
  container.innerHTML = `
    <div style="padding:var(--sp-3) var(--sp-4);border-bottom:1px solid rgba(255,255,255,0.06)">
      <div style="font-size:10px;font-weight:600;letter-spacing:0.07em;
                  text-transform:uppercase;color:#4A4842;margin-bottom:var(--sp-2)">
        Institution
      </div>
      ${memberships.map(m => `
        <button onclick="switchMembership('${m.id}')"
          style="width:100%;text-align:left;padding:6px 8px;border:none;
                 border-radius:4px;cursor:pointer;font-size:12px;
                 background:${m.id === active?.id ? 'rgba(255,255,255,0.08)' : 'transparent'};
                 color:${m.id === active?.id ? '#F5F3EE' : '#8C8A83'};
                 margin-bottom:2px;display:flex;align-items:center;gap:6px">
          <span style="width:6px;height:6px;border-radius:50%;flex-shrink:0;
                       background:${m.id === active?.id ? 'var(--color-amber)' : 'transparent'};
                       border:1px solid ${m.id === active?.id ? 'var(--color-amber)' : '#4A4842'}">
          </span>
          <div>
            <div>${m.institution_name}</div>
            <div style="font-size:10px;opacity:0.6">${m.role}</div>
          </div>
        </button>`).join('')}
    </div>`;

  window.switchMembership = (membershipId) => {
    const m = memberships.find(m => m.id === membershipId);
    if (!m) return;
    session.setActiveMembership(m);
    window.location.reload();
  };
}

// ── Init everything ───────────────────────────────────────────────
export function initLayout(activeNavId) {
  const user = requireAuth();
  if (!user) return null;

  renderNav(activeNavId, user.role);
  renderUser(user);
  renderInstitutionSwitcher('sidebar-institution-switcher');
  initMobileToggle();
  initLogout();
  injectLangSwitcher();
  applyTranslations();

  // Re-render nav + apply translations on language change
  window.addEventListener('localechange', () => {
    renderNav(activeNavId, user.role);
    applyTranslations();
  });

  return user;
}
