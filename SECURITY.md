# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | Yes       |
| 0.5.x   | Yes       |
| < 0.5   | No        |

## Reporting a vulnerability

Do not open a public GitHub issue to report a security vulnerability.

Send a detailed report to: **[pynerd.mvp@gmail.com](mailto:pynerd.mvp@gmail.com)**

Include:

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested mitigations

You will receive an acknowledgement within 72 hours. We aim to release a fix
within 14 days of a confirmed vulnerability, depending on severity.

## Security considerations for deployment

**Backend:**

- Never set `DEBUG = True` in production.
- Rotate `SECRET_KEY` before the first production deployment.
- Use strong, randomly generated database passwords.
- Restrict `ALLOWED_HOSTS` to your actual domain names.
- Configure `CORS_ALLOWED_ORIGINS` to your frontend origin only.
- The JWT access token lifetime defaults to **15 minutes**. Adjust via
  `JWT_ACCESS_TOKEN_MINUTES` if needed; do not increase beyond 30 minutes.
- Token blacklisting is enabled. The blacklist table (`outstanding_token`,
  `blacklisted_token`) will grow over time. Schedule periodic cleanup using
  the simplejwt management command:
  
  ```bash
  python manage.py flushexpiredtokens
  ```

**Frontend:**

- JWT tokens are stored in `localStorage`. This is accessible to JavaScript
  running on the same origin. If your threat model requires stronger isolation,
  consider migrating to `httpOnly` cookies served by the backend (planned).
- The production Vercel configuration sets `X-Frame-Options: DENY`,
  `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `X-Robots-Tag: noindex`,
  and a `Content-Security-Policy` header on all HTML responses.
- Ensure `API_BASE` in `js/config.js` uses HTTPS in production.
- The admin panel is served at `/mgmt-matrika/` (non-default path).

**Infrastructure:**

- Serve the backend behind Nginx with TLS. The included Docker Compose
  configuration includes an Nginx service; configure your TLS certificates
  in `nginx/certs/`.
- Do not expose PostgreSQL ports publicly.
- Run database backups on a scheduled basis.
