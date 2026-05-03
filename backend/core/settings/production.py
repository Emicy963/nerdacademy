import dj_database_url
from corsheaders.defaults import default_headers

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "").split(",")
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",")

CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOW_HEADERS = list(default_headers) + ["X-Institution-Id"]

# Railway terminates TLS at the proxy layer — use the forwarded header instead
# of redirecting to HTTPS (which would cause an infinite loop).
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# WhiteNoise — must sit right after SecurityMiddleware (index 1)
MIDDLEWARE.insert(2, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Railway supplies a single DATABASE_URL; fall back to individual vars from base
_db_url = os.environ.get("DATABASE_URL")
if _db_url:
    DATABASES["default"] = dj_database_url.config(
        default=_db_url,
        conn_max_age=600,
        ssl_require=True,
    )

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

REFRESH_TOKEN_COOKIE = {**REFRESH_TOKEN_COOKIE, "secure": True}
