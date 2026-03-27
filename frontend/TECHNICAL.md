# Frontend — Technical Reference

This document explains the internal architecture, design decisions and code
conventions of the Acadêmico frontend. It is intended for developers who
need to understand, extend or debug the codebase.

---

## Architectural decisions

### No framework, no build step

The frontend is intentionally built without a JavaScript framework (React,
Vue, Svelte) and without a build tool (Vite, Webpack, esbuild). This
decision has consequences that every developer working on this project should
understand:

- Files are served as-is. There is no compilation, transpilation or bundling.
- ES modules (`import`/`export`) are used natively. The browser resolves
  module imports directly. This requires serving files over HTTP (not `file://`).
- Each page is a standalone HTML file. There is no client-side router.
  Navigation between pages is standard `<a href>` link traversal.
- State is not shared between pages. Each page initialises from `localStorage`
  tokens and API calls on load.

### CSS architecture

The CSS is split into two files with distinct responsibilities:

`global.css` contains the design system: CSS custom properties (tokens),
a reset layer, typography scale, and all reusable component classes
(buttons, forms, badges, cards, tables, modals, toasts, skeleton loaders).
This file is imported by every page.

`layout.css` contains structural styles for the app shell: the sidebar,
topbar, and main content area. It is also imported by every page that uses
the dashboard shell. Pages that use a different layout (login) do not import
it.

No class name convention (BEM, SMACSS, utility-first) is strictly enforced.
The classes loosely follow a component prefix pattern (`sidebar__brand`,
`card-header`, `btn-primary`) and are designed to be readable without a
preprocessor.

### JavaScript module structure

Three shared modules are used across all pages:

**`js/api.js`** — the API client. Exports named resource objects (`students`,
`trainers`, `courses`, `classes`, `grades`, `institutions`, `auth`) and the
`token` helper. All network communication goes through this file.

**`js/api.mock.js`** — a drop-in replacement for `api.js` during development.
Exports the same interface with identical function signatures. No changes to
page code are needed beyond the import path.

**`js/layout.js`** — the shared layout module. Exports functions for nav
rendering, breadcrumb management, auth guard, and mobile sidebar. Called once
per page via `initLayout(activeNavId)`.

---

## API client — `js/api.js`

### Request flow

```
apiFetch(path, options)
    │
    ├── attach Authorization header from localStorage
    │
    ├── fetch(API_BASE + path, options)
    │
    ├── if 401 and not already retrying:
    │       silentRefresh()           ← POST /auth/refresh/
    │       retry apiFetch once
    │       if refresh fails → clear tokens → redirect to login
    │
    ├── if !res.ok → parseError(res) → throw Error with .status and .detail
    │
    └── if 204 → return null
        else   → return res.json()
```

### Silent token refresh

The `silentRefresh` function uses a single in-flight promise (`_refreshing`)
to deduplicate concurrent refresh calls. If three requests fire simultaneously
and all receive 401, only one refresh request is sent; the other two await
the same promise.

```js
let _refreshing = null;

async function silentRefresh() {
  if (_refreshing) return _refreshing;   // deduplicate
  _refreshing = (async () => { ... })().finally(() => { _refreshing = null; });
  return _refreshing;
}
```

### Error normalisation

The backend returns errors in the envelope `{error, status_code, detail}`.
`parseError` reads the response body and extracts the most useful message:

1. If `body.detail` is a string, use it directly.
2. If `body.detail` is an object, stringify it.
3. If `body.non_field_errors` is present, use the first message.
4. Otherwise, take the first value from the body object (field-level error).

The resulting `Error` object has `.status` (HTTP status code) and `.detail`
(human-readable message) properties in addition to the standard `.message`.

### Pagination parameters

All list methods accept a `params` object that maps to query string
parameters. The backend envelope is `{count, pages, page, next, previous, results}`.
Pages call `list(params)` and access `data.results` and `data.count`.

---

## Layout module — `js/layout.js`

### Initialisation

Every dashboard page calls `initLayout(activeNavId)` as its first statement.
This function:

1. Calls `requireAuth()` — reads the JWT from `localStorage`; redirects to
   login if absent or unparseable.
2. Calls `renderNav(activeNavId, user.role)` — builds the sidebar nav from
   the `NAV_ITEMS` configuration, filtering by the user's role and marking
   the active item.
3. Calls `renderUser(user)` — fills the sidebar footer with the user's name,
   role and initials.
4. Calls `initMobileToggle()` — wires the hamburger button to the sidebar
   open/close state.
5. Calls `initLogout()` — wires the logout button to clear tokens and redirect.

The function returns the `user` object so pages can read `user.role` without
a separate call.

### Nav configuration

The `NAV_ITEMS` array defines which nav entries appear for which roles:

```js
const NAV_ITEMS = [
  {
    section: 'Overview',
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: 'dashboard',
        href: '/pages/dashboard.html', roles: ['admin', 'trainer', 'student'] },
    ]
  },
  ...
];
```

Adding a new page to the navigation requires only a new entry in this array.

---

## Page architecture

### Common pattern

Every page follows the same initialisation sequence:

```js
// 1. Bootstrap layout and get user
const user = initLayout('page-id');
if (!user) throw new Error('unauthenticated');

// 2. Set breadcrumb
setBreadcrumb([{ label: 'Page Title', current: true }]);

// 3. Load icon sprite asynchronously
fetch('../components/icons.html')
  .then(r => r.text())
  .then(h => { document.getElementById('icon-sprite').innerHTML = h; });

// 4. Role-based UI setup
const isAdmin = user.role === 'admin';
if (isAdmin) { /* show admin controls */ }

// 5. Load data
loadData();
```

### Loading states

All data loading follows a three-state pattern:

1. **Skeleton** — placeholder elements rendered immediately in HTML before
   the JS runs. Uses the `.skel` class which applies an animated shimmer.
2. **Loaded** — real data replaces the skeleton via `innerHTML` assignment.
3. **Error** — an empty state with an error message and a "Try again" button
   that calls the load function again.

### Role-based rendering

A single page serves all roles. Role checks are applied at multiple levels:

- **Nav filtering** — `layout.js` renders only the nav items applicable to
  the user's role.
- **UI controls** — pages check `user.role` and conditionally render write
  controls (create buttons, edit buttons, action menus).
- **Data filtering** — some pages show different content by role (e.g.
  `dashboard.html` renders three entirely different layouts; `classes.html`
  shows a table for admin/trainer and an enrolment card grid for students).
- **Redirect guard** — pages restricted to a single role (e.g. `trainers.html`
  is admin-only) redirect immediately if the role does not match.

---

## Design system

### Tokens

All values are defined as CSS custom properties on `:root` in `global.css`.
The categories are:

- **Surface colours** — `--bg-canvas`, `--bg-surface`, `--bg-raised`
- **Sidebar colours** — `--sidebar-bg`, `--sidebar-hover`, `--sidebar-active`, `--sidebar-accent`
- **Text colours** — `--text-primary`, `--text-secondary`, `--text-tertiary`, `--text-inverse`
- **Border colours** — `--border-default`, `--border-strong`, `--border-focus`
- **State colours** — `--color-amber`, `--color-green`, `--color-red`, `--color-blue` (and `-bg` variants)
- **Spacing** — `--sp-1` through `--sp-16` (4px base unit)
- **Typography** — `--font-ui` (DM Sans), `--font-mono` (DM Mono)
- **Radius** — `--radius-sm` (4px), `--radius-md` (6px), `--radius-lg` (10px), `--radius-xl` (14px)
- **Shadows** — `--shadow-sm`, `--shadow-md`, `--shadow-lg`
- **Layout** — `--sidebar-width` (224px), `--topbar-height` (56px)

### Typography classes

| Class            | Size   | Weight | Usage                                  |
|------------------|--------|--------|----------------------------------------|
| `.t-display`     | 24px   | 600    | Page titles                            |
| `.t-heading`     | 18px   | 600    | Section and panel headings             |
| `.t-subheading`  | 13px   | 500    | Uppercase category labels              |
| `.t-body`        | 14px   | 400    | Standard body text                     |
| `.t-body-sm`     | 13px   | 400    | Secondary body text                    |
| `.t-mono`        | 12px   | 400    | Codes, IDs, dates, numeric values      |
| `.t-label`       | 12px   | 500    | Form labels and tags                   |

### Skeleton loader

The `.skel` class applies an animated shimmer to any element. It is used
inline (via `style` attributes) to create placeholder shapes that match the
expected content layout:

```html
<div class="skel" style="height:14px;width:60%;border-radius:4px"></div>
```

The shimmer uses a `linear-gradient` background animated with `background-position`.
It does not use `opacity` or `transform` to avoid repaints.

---

## Icon system

All icons are SVG symbols defined in `components/icons.html`. The sprite is
loaded asynchronously on every page:

```js
fetch('../components/icons.html')
  .then(r => r.text())
  .then(h => { document.getElementById('icon-sprite').innerHTML = h; });
```

Icons are referenced via `<use>`:

```html
<svg width="16" height="16">
  <use href="#icon-students"/>
</svg>
```

All symbols use `stroke="currentColor"`, which means icon colour is
controlled by the `color` CSS property of the parent element.

---

## Mock API — `js/api.mock.js`

### Design principles

The mock exports the same named objects as `api.js` with identical function
signatures. Every function is `async` and awaits a `delay()` call to simulate
network latency (default 400ms). This ensures that loading state transitions
are visible and tested during development.

All fixture data is defined as mutable `let` arrays at the top of the file.
Write operations mutate these arrays in place (e.g. `STUDENTS.push(student)`),
so the UI reflects changes within the session. Data is reset on page refresh.

### Pagination

The `paginate(results, params)` helper slices the fixture array and returns
the standard envelope `{count, pages, page, next, previous, results}`.
Pages work correctly with the mock because the envelope is identical to the
real API.

### Simulated errors

The mock validates business rules and throws errors with a `.status` property
to match the real API. Examples:

- Enrolling a student in a non-open class → `400`
- Enrolling an already-enrolled student → `400`
- Dropping a completed enrolment → `400`
- Getting a non-existent record → `404`

---

## Vercel deployment

The `vercel.json` configuration file specifies:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/frontend/$1" }],
  "headers": [
    {
      "source": "/frontend/js/(.*)",
      "headers": [{ "key": "Cache-Control", "value": "public, max-age=31536000, immutable" }]
    }
  ]
}
```

The rewrite rule maps the root of the Vercel deployment to the `frontend/`
directory, so `https://yourdomain.vercel.app/pages/login.html` resolves to
`frontend/pages/login.html`.

Before deploying, set `API_BASE` in `js/api.js` to the production backend
URL. The CORS configuration on the backend must list the Vercel deployment
URL in `CORS_ALLOWED_ORIGINS`.
