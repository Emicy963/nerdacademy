# Frontend — Acadêmico

Vanilla HTML/CSS/JavaScript client for the Acadêmico academic management platform.
No build tools, no frameworks, no transpilation. Files are served as-is.

---

## Requirements

- A modern browser (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- A running instance of the Acadêmico backend API, OR the mock layer enabled
- For production: a Vercel account (static deployment)

## Running locally

Because the JavaScript modules use `import/export` (ES modules), the files
must be served over HTTP rather than opened directly as `file://` URLs.
Any static file server works:

```bash
# Option 1: Python (no install required)
cd academico
python -m http.server 3000
# Open http://localhost:3000/frontend/pages/login.html

# Option 2: Node http-server
npx http-server . -p 3000
# Open http://localhost:3000/frontend/pages/login.html
```

The API base URL is configured in `js/api.js`:

```js
const API_BASE = 'http://localhost:8000/api';
```

Change this to point to your backend before serving.

## Running without the backend (mock mode)

The file `js/api.mock.js` is a drop-in replacement for `js/api.js` that
returns realistic fixture data without making any network requests.

To enable mock mode, edit each page's import statement:

```js
// Change this:
import { students, ... } from '../js/api.js';

// To this:
import { students, ... } from '../js/api.mock.js';
```

The mock login accepts any email/password combination. The active role is
controlled by the `MOCK_USER.role` constant at the top of `api.mock.js`.
Change it to `"trainer"` or `"student"` to test the other role views.
All write operations (create, update, delete) mutate the in-memory fixture
state for the duration of the session. A page refresh resets all data.

## Project structure

```
frontend/
├── css/
│   ├── global.css        Design tokens, reset, component styles
│   └── layout.css        App shell: sidebar, topbar, content area
├── js/
│   ├── api.js            API client (production)
│   ├── api.mock.js       Mock API client (development without backend)
│   └── layout.js         Shared layout module
├── components/
│   ├── icons.html        SVG icon sprite
│   └── shell.html        App shell HTML template
├── pages/
│   ├── login.html        Authentication
│   ├── dashboard.html    Role-based dashboard
│   ├── students.html     Student management
│   ├── trainers.html     Trainer management
│   ├── courses.html      Course catalogue
│   ├── classes.html      Class and enrolment management
│   └── grades.html       Grade assessment and reporting
└── index.html            Design system preview / entry point
```

## Deployment to Vercel

The repository includes a `vercel.json` configuration file. To deploy:

```bash
# Install Vercel CLI
npm install -g vercel

# From the repository root
vercel

# Or connect the GitHub repository to Vercel and configure:
# Root directory: frontend
# Framework preset: Other
# Build command: (empty)
# Output directory: .
```

The `vercel.json` file configures:

- All routes to be served as static files
- A rewrite rule that handles the `/frontend/` path prefix
- Cache headers for static assets

Before deploying to production, update `API_BASE` in `js/api.js` to point
to your production backend URL.

## Browser support

The frontend uses ES modules (`type="module"` on script tags) and the Fetch
API natively. No polyfills are included. The minimum supported browser
versions are those that support ES2020 features natively.

## License

MIT — see root `LICENSE`.
