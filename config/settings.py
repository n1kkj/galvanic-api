import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(".env")

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG", default=False)

HOST = env("HOST", default="127.0.0.1:8000")
BASE_URL = env("BASE_URL", default="http://127.0.0.1:8000")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS").split(" ")


# Application definition

INSTALLED_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_yasg",
    "corsheaders",
    "django_filters",
    "apps.core.apps.CoreConfig",
    "apps.unfold_admin",
    "apps.api",
    "channels",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": env("DB_NAME", default="galvanica_db"),
        "USER": env("DB_USER", default="postgres"),
        "PASSWORD": env("DB_PASS", default="postgres"),
        "HOST": env("DB_HOST", default="127.0.0.1"),
        "PORT": env("DB_PORT", default="5432"),
    }
}

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

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

LANGUAGES = [("ru", _("russian"))]
LANGUAGE_CODE = "ru"
LOCALE_PATHS = [
    BASE_DIR / "locale",
]

SIMPLE_JWT = {
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS").split(" ")

TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


STATIC_URL = "static/"

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

REDIS_URL = env("REDIS_URL", default="redis://127.0.0.1:6379/0")
SENSOR_DATA_MODE = env("SENSOR_DATA_MODE", default="factory_api")

UNFOLD = {
    "SIDEBAR": {
        "show_search": False,
        "navigation": [
            {
                "title": "Мониторинг",
                "separator": False,
                "items": [
                    {
                        "title": "Станки",
                        "icon": "precision_manufacturing",
                        "link": "/admin/core/machine/",
                    },
                    {
                        "title": "Датчики",
                        "icon": "sensors",
                        "link": "/admin/core/sensor/",
                    },
                ],
            },
        ],
    },
}

FACTORY_STATUS_URL = env("FACTORY_STATUS_URL", default="https://pr4ibk-37-230-157-12.ru.tuna.am/api/factory-status")
