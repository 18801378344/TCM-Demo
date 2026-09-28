"""Render-only configuration layered over the submitted settings."""
from .settings import *
import dj_database_url
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
ALLOWED_HOSTS = [os.environ["RENDER_EXTERNAL_HOSTNAME"]]
CSRF_TRUSTED_ORIGINS = ["https://" + ALLOWED_HOSTS[0]]
DATABASES = {"default": dj_database_url.parse(os.environ["DATABASE_URL"], conn_max_age=60)}
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SESSION_COOKIE_AGE = 3600
