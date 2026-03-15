/**
 * layout.js
 * Manages the app shell: sidebar nav state, mobile toggle,
 * breadcrumb updates, and user info rendering.
 * Import this on every page that uses the dashboard shell.
 */

// ── Nav items config ──────────────────────────────────────
const NAV_ITEMS = [
  {
    section: 'Overview',
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: 'dashboard', href: '/pages/dashboard.html', roles: ['admin', 'trainer', 'student'] },
    ]
  },
  {
    section: 'Management',
    items: [
      { id: 'students',  label: 'Students',  icon: 'students',  href: '/pages/students.html',  roles: ['admin', 'trainer'] },
      { id: 'trainers',  label: 'Trainers',  icon: 'trainers',  href: '/pages/trainers.html',  roles: ['admin'] },
      { id: 'courses',   label: 'Courses',   icon: 'courses',   href: '/pages/courses.html',   roles: ['admin', 'trainer', 'student'] },
      { id: 'classes',   label: 'Classes',   icon: 'classes',   href: '/pages/classes.html',   roles: ['admin', 'trainer', 'student'] },
    ]
  },
  {
    section: 'Academic',
    items: [
      { id: 'grades',    label: 'Grades',    icon: 'grades',    href: '/pages/grades.html',    roles: ['admin', 'trainer', 'student'] },
    ]
  },
];

// ── Render sidebar nav ────────────────────────────────────
export function renderNav(activeId, userRole = 'admin') {
  const navEl = document.getElementById('sidebar-nav');
  if (!navEl) return;

  const currentPath = window.location.pathname;

  navEl.innerHTML = NAV_ITEMS.map(section => {
    const visibleItems = section.items.filter(item =>
      item.roles.includes(userRole)
    );
    if (!visibleItems.length) return '';

    const itemsHTML = visibleItems.map(item => {
      const isActive = activeId
        ? item.id === activeId
        : currentPath.includes(item.id);

      return `
        <a href="${item.href}"
           class="nav-item ${isActive ? 'active' : ''}"
           data-nav-id="${item.id}">
          <svg class="nav-item__icon" aria-hidden="true">
            <use href="#icon-${item.icon}"/>
          </svg>
          ${item.label}
        </a>
      `;
    }).join('');

    return `
      <div class="sidebar__section">
        <div class="sidebar__section-label">${section.section}</div>
        ${itemsHTML}
      </div>
    `;
  }).join('');
}

// ── Render user info in sidebar footer ───────────────────
export function renderUser(user) {
  const nameEl  = document.getElementById('sidebar-user-name');
  const roleEl  = document.getElementById('sidebar-user-role');
  const avatarEl = document.getElementById('sidebar-avatar');
  if (!nameEl) return;

  const displayName = user?.email
    ? user.email.split('@')[0].replace(/[._]/g, ' ')
    : 'User';
  const initials = displayName.split(' ')
    .map(w => w[0]?.toUpperCase() ?? '')
    .slice(0, 2)
    .join('');

  nameEl.textContent  = displayName;
  roleEl.textContent  = user?.role ?? '';
  if (avatarEl) avatarEl.textContent = initials;
}

// ── Breadcrumb ────────────────────────────────────────────
export function setBreadcrumb(items) {
  // items: [{ label: 'Students' }, { label: 'Ana Silva', current: true }]
  const el = document.getElementById('topbar-breadcrumb');
  if (!el) return;

  el.innerHTML = items.map((item, i) => {
    const isLast = i === items.length - 1;
    const sep = i > 0
      ? `<span class="topbar__breadcrumb-sep">
           <svg width="6" height="10" viewBox="0 0 6 10" fill="none">
             <path d="M1 1l4 4-4 4" stroke="currentColor" stroke-width="1.5"
                   stroke-linecap="round" stroke-linejoin="round"/>
           </svg>
         </span>`
      : '';
    return `${sep}<span class="topbar__breadcrumb-item ${isLast ? 'current' : ''}">${item.label}</span>`;
  }).join('');
}

// ── Mobile sidebar toggle ────────────────────────────────
export function initMobileToggle() {
  const sidebar    = document.getElementById('sidebar');
  const menuBtn    = document.getElementById('menu-toggle');
  const backdrop   = document.getElementById('sidebar-backdrop');

  if (!menuBtn || !sidebar) return;

  const open  = () => { sidebar.classList.add('open'); backdrop?.classList.add('visible'); };
  const close = () => { sidebar.classList.remove('open'); backdrop?.classList.remove('visible'); };

  menuBtn.addEventListener('click', open);
  backdrop?.addEventListener('click', close);
}

// ── Logout ───────────────────────────────────────────────
export function initLogout() {
  const btn = document.getElementById('logout-btn');
  if (!btn) return;

  btn.addEventListener('click', () => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user');
    window.location.href = '/pages/login.html';
  });
}

// ── Guard: redirect to login if not authenticated ────────
export function requireAuth() {
  const token = localStorage.getItem('access');
  if (!token) {
    window.location.href = '/pages/login.html';
    return null;
  }
  try {
    const user = JSON.parse(localStorage.getItem('user') ?? '{}');
    return user;
  } catch {
    window.location.href = '/pages/login.html';
    return null;
  }
}

// ── Init everything ───────────────────────────────────────
export function initLayout(activeNavId) {
  const user = requireAuth();
  if (!user) return;

  renderNav(activeNavId, user.role);
  renderUser(user);
  initMobileToggle();
  initLogout();

  return user;
}
