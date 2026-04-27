import { session, auth, notifications as notifApi } from './api.js';
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

  // Wrap avatar + user-info in a profile link (only once)
  const userEl = nameEl.closest('.sidebar__user');
  if (userEl && !userEl.querySelector('.sidebar__user-link')) {
    const link = document.createElement('a');
    link.href = '/pages/profile.html';
    link.className = 'sidebar__user-link';
    link.title = t('profile.title') || 'Profile';
    const userInfoEl = nameEl.parentElement;
    userEl.insertBefore(link, avatarEl);
    link.appendChild(avatarEl);
    link.appendChild(userInfoEl);
  }
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

// ── Notifications ─────────────────────────────────────────────────
function timeAgo(isoString) {
  const diff = Math.floor((Date.now() - new Date(isoString)) / 1000);
  if (diff < 60)  return t('notif.time.just_now');
  if (diff < 3600) return t('notif.time.minutes').replace('{n}', Math.floor(diff / 60));
  if (diff < 86400) return t('notif.time.hours').replace('{n}', Math.floor(diff / 3600));
  const d = new Date(isoString), now = new Date();
  if (now.toDateString() !== d.toDateString() &&
      new Date(now - 86400000).toDateString() === d.toDateString())
    return t('notif.time.yesterday');
  return d.toLocaleDateString();
}

function renderNotifPanel(data) {
  const { unread_count, results } = data;
  const panel = document.getElementById('notif-panel');
  if (!panel) return;

  if (!results.length) {
    panel.innerHTML = `
      <div class="notif-panel__header">
        <span>${t('ui.notifications')}</span>
      </div>
      <div class="notif-panel__empty">
        <div style="font-size:20px;margin-bottom:4px">🔔</div>
        <div style="font-weight:500;margin-bottom:2px">${t('notif.empty')}</div>
        <div style="font-size:11px;color:var(--text-tertiary)">${t('notif.empty.desc')}</div>
      </div>`;
    return;
  }

  const items = results.map(n => `
    <div class="notif-item ${n.is_read ? '' : 'notif-item--unread'}"
         data-notif-id="${n.id}" role="button" tabindex="0">
      <div class="notif-item__dot"></div>
      <div class="notif-item__body">
        <div class="notif-item__title">${n.title}</div>
        ${n.message ? `<div class="notif-item__msg">${n.message}</div>` : ''}
        <div class="notif-item__time">${timeAgo(n.created_at)}</div>
      </div>
    </div>`).join('');

  panel.innerHTML = `
    <div class="notif-panel__header">
      <span>${t('ui.notifications')}${unread_count > 0 ? ` <span class="notif-count-inline">${unread_count}</span>` : ''}</span>
      ${unread_count > 0 ? `<button class="notif-mark-all">${t('notif.mark_all')}</button>` : ''}
    </div>
    <div class="notif-panel__list">${items}</div>`;

  panel.querySelector('.notif-mark-all')?.addEventListener('click', async () => {
    await notifApi.markAllRead().catch(() => {});
    const fresh = await notifApi.list().catch(() => null);
    if (fresh) { renderNotifPanel(fresh); updateBadge(0); }
  });

  panel.querySelectorAll('.notif-item').forEach(el => {
    el.addEventListener('click', async () => {
      const id = el.dataset.notifId;
      if (!el.classList.contains('notif-item--unread')) return;
      el.classList.remove('notif-item--unread');
      await notifApi.markRead(id).catch(() => {});
      const badge = document.getElementById('notif-badge');
      if (badge) {
        const cur = parseInt(badge.textContent) || 0;
        updateBadge(Math.max(0, cur - 1));
      }
    });
  });
}

function updateBadge(count) {
  const badge = document.getElementById('notif-badge');
  if (!badge) return;
  badge.textContent = count > 99 ? '99+' : count;
  badge.style.display = count > 0 ? 'flex' : 'none';
}

export function initNotifications() {
  const btn = document.querySelector('.topbar__icon-btn[aria-label="Notifications"]');
  if (!btn || !session.isLoggedIn()) return;

  // Inject badge
  btn.style.position = 'relative';
  const badge = document.createElement('span');
  badge.id = 'notif-badge';
  badge.style.cssText = [
    'display:none', 'position:absolute', 'top:-4px', 'right:-4px',
    'min-width:16px', 'height:16px', 'padding:0 4px',
    'background:var(--color-red)', 'color:#fff',
    'font-size:10px', 'font-weight:700', 'line-height:16px',
    'border-radius:99px', 'text-align:center', 'pointer-events:none',
  ].join(';');
  btn.appendChild(badge);

  // Inject panel
  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'position:relative';
  btn.parentNode.insertBefore(wrapper, btn);
  wrapper.appendChild(btn);

  const panel = document.createElement('div');
  panel.id = 'notif-panel';
  panel.className = 'notif-panel';
  panel.style.display = 'none';
  wrapper.appendChild(panel);

  // Inject styles once
  if (!document.getElementById('notif-styles')) {
    const style = document.createElement('style');
    style.id = 'notif-styles';
    style.textContent = `
      .notif-panel {
        position:absolute; top:calc(100% + 8px); right:0;
        width:320px; max-height:420px;
        background:var(--bg-surface); border:1px solid var(--border-default);
        border-radius:var(--radius-lg,8px); box-shadow:0 8px 24px rgba(0,0,0,0.12);
        z-index:500; overflow:hidden; display:flex; flex-direction:column;
      }
      .notif-panel__header {
        display:flex; align-items:center; justify-content:space-between;
        padding:12px 16px 10px; border-bottom:1px solid var(--border-default);
        font-size:13px; font-weight:600; color:var(--text-primary);
        flex-shrink:0;
      }
      .notif-count-inline {
        display:inline-flex; align-items:center; justify-content:center;
        background:var(--color-red); color:#fff;
        font-size:10px; font-weight:700; height:16px; min-width:16px;
        padding:0 4px; border-radius:99px; margin-left:4px;
      }
      .notif-mark-all {
        font-size:11px; color:var(--text-secondary); background:none;
        border:none; cursor:pointer; padding:0; font-family:var(--font-ui);
      }
      .notif-mark-all:hover { color:var(--text-primary); }
      .notif-panel__list { overflow-y:auto; flex:1; }
      .notif-panel__empty {
        padding:32px 16px; text-align:center;
        font-size:13px; color:var(--text-secondary);
      }
      .notif-item {
        display:flex; align-items:flex-start; gap:10px;
        padding:12px 16px; cursor:pointer;
        border-bottom:1px solid var(--border-default);
        transition:background 120ms ease;
      }
      .notif-item:last-child { border-bottom:none; }
      .notif-item:hover { background:var(--bg-raised); }
      .notif-item--unread { background:var(--color-blue-bg,#EAF4FB); }
      .notif-item--unread:hover { background:#dbeef7; }
      .notif-item__dot {
        width:8px; height:8px; border-radius:50%; flex-shrink:0; margin-top:4px;
        background:transparent;
      }
      .notif-item--unread .notif-item__dot { background:var(--color-blue,#2980B9); }
      .notif-item__body { flex:1; min-width:0; }
      .notif-item__title { font-size:13px; font-weight:500; color:var(--text-primary); line-height:1.4; }
      .notif-item__msg { font-size:12px; color:var(--text-secondary); margin-top:2px; }
      .notif-item__time { font-size:11px; color:var(--text-tertiary); margin-top:4px; }
    `;
    document.head.appendChild(style);
  }

  // Toggle panel
  btn.addEventListener('click', async (e) => {
    e.stopPropagation();
    const isOpen = panel.style.display !== 'none';
    if (isOpen) { panel.style.display = 'none'; return; }
    panel.style.display = 'flex';
    try {
      const data = await notifApi.list();
      renderNotifPanel(data);
      updateBadge(data.unread_count);
    } catch { /* silent */ }
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!wrapper.contains(e.target)) panel.style.display = 'none';
  });

  // Poll unread count every 60 seconds
  async function pollUnread() {
    try {
      const data = await notifApi.list();
      updateBadge(data.unread_count);
    } catch { /* silent */ }
  }
  pollUnread();
  setInterval(pollUnread, 60_000);
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
  initNotifications();
  applyTranslations();

  // Re-render nav + apply translations on language change
  window.addEventListener('localechange', () => {
    renderNav(activeNavId, user.role);
    applyTranslations();
  });

  return user;
}
