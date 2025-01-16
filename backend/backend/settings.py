import os
from datetime import timedelta
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")

#####################
#   General Settings
#####################
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG") == "True"

allowed_hosts_string = os.environ.get("ALLOWED_HOSTS")
ALLOWED_HOSTS = allowed_hosts_string.split(",") if allowed_hosts_string else []

#####################
#   Application Definition
#####################
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "api",
    "stocks",
    "rest_framework",
    "corsheaders",
]

MIDDLEWARE = [
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"
ASGI_APPLICATION = "backend.asgi.application"

#####################
#   Database Settings
#####################
if os.environ.get("USE_DEVELOPMENT_DB") == "True":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME"),
            "USER": os.environ.get("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": dj_database_url.config(
            default="postgres://user:pass@host:port/dbname"
        )
    }

#####################
#   Password Validation
#####################
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

#####################
#   Internationalization
#####################
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Berlin"

USE_I18N = True

USE_TZ = True

#####################
#   Static Files
#####################
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

#####################
#   Default primary key field type
#####################
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

#####################
#   REST Framework & JWT Settings
#####################
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

#####################
#   CORS & CSRF Settings
#####################
FRONTEND_URL = os.environ.get("FRONTEND_URL")
CORS_ALLOWED_ORIGINS = [FRONTEND_URL] if FRONTEND_URL else []
CSRF_TRUSTED_ORIGINS = [FRONTEND_URL] if FRONTEND_URL else []
CORS_ALLOWS_CREDENTIALS = True


#####################
#   Security Settings (for production with HTTPS)
#####################
def get_bool_env(name, default=False):
    """Helper function to get boolean values from environment variables."""
    value = os.environ.get(name)
    return value == "True" if value is not None else default


def get_int_env(name, default=None):
    """Helper function to get integer values from environment variables."""
    value = os.environ.get(name)
    return int(value) if value is not None else default


def get_str_env(name, default=None):
    """Helper function to get string values from environment variables."""
    return os.environ.get(name, default)


if not DEBUG:
    SECURE_SSL_REDIRECT = get_bool_env("SECURE_SSL_REDIRECT")
    SECURE_HSTS_SECONDS = get_int_env("SECURE_HSTS_SECONDS", 31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = get_bool_env("SECURE_HSTS_INCLUDE_SUBDOMAINS")
    SECURE_HSTS_PRELOAD = get_bool_env("SECURE_HSTS_PRELOAD")
    SESSION_COOKIE_SECURE = get_bool_env("SESSION_COOKIE_SECURE")
    CSRF_COOKIE_SECURE = get_bool_env("CSRF_COOKIE_SECURE")
    SECURE_REFERRER_POLICY = get_str_env("SECURE_REFERRER_POLICY", "same-origin")
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

#####################
#   Debug Toolbar (nur für Entwicklung)
#####################
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

#####################
#  Email settings
#####################
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = get_str_env("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = get_int_env("EMAIL_PORT", 587)
EMAIL_USE_TLS = get_bool_env("EMAIL_USE_TLS")
EMAIL_HOST_USER = os.environ.get("EMAIL_USER")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_PASS")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

#####################
#   Stock Updates
#####################
UPDATE_STOCKS = get_bool_env("UPDATE_STOCKS", True)
UPDATE_STOCKS_INTERVAL = get_int_env("UPDATE_STOCKS_INTERVAL", 3600)
