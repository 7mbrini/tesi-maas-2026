# (C) 2025-2026 Francesco Settembrini

"""
Django settings for RentalBikes project.
"""

import os

from pathlib import Path
from logs import log_clear


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '7bN9wK3mRz2pXq8vYt5cX4mJ9wK2pRt5vYq8cX3mN2pWz7vRt5c')

# Il nostro "interruttore": True se il file .env esiste, False sul VPS
DEBUG = os.environ.get('DJANGO_DEBUG') == 'True'

# --- MODIFICA 1: Sicurezza e Proxy ---
# Necessario quando Django è dietro un Proxy (Plesk/Nginx) per gestire HTTPS correttamente
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# setup per OSGEO, richiesto da GeoDjango e PostGIS
if os.name == 'nt':
    VENV_BASE = os.environ.get('VIRTUAL_ENV', '') # Evita KeyError se non attiva
    if VENV_BASE:
        os.environ['PATH'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\osgeo') + ';' + os.environ['PATH']
        os.environ['PROJ_LIB'] = os.path.join(VENV_BASE, 'Lib\\site-packages\\osgeo\\data\\proj') + ';' + os.environ['PATH']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'whitenoise.runserver_nostatic', # --- MODIFICA 3: Aiuta WhiteNoise a prendere il controllo ---
    'django.contrib.staticfiles',

    'django.contrib.gis',
    'rest_framework',
    'rest_framework_gis',

    'main',
    'cars',
    'rentals',
    'accounts',
    'payments',
    'tools',
    'api',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # --- MODIFICA 4: Posizione fissa per evitare errori ---
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'rentalbikes.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'rentalbikes.wsgi.application'

# Configurazione Database Dinamica per Docker
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('DB_NAME', 'rentalbikes'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'postgres'),
        'HOST': os.environ.get('DB_HOST', 'db'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/' # Aggiunto slash iniziale per sicurezza

# Cartella dove collectstatic copierà i file
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Cartella sorgente dei tuoi file statici
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

WHITENOISE_USE_FINDERS = True

LOGIN_REDIRECT_URL = '/rentals/'

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- STORAGE STATICI ---
# MODIFICA 5: Cambiato ManifestStaticFilesStorage in CompressedStaticFilesStorage
# Questo evita l'Errore 500 se un file manca nel manifest, rendendo il sistema più stabile.
if not DEBUG:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        # Logger specifico per la tua app (cambia 'api' con il nome della tua app)
        'api': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

# --- SICUREZZA CSRF ---
# Legge la stringa dal file .env (separata da virgole). Se manca, usa i valori di default locali.
CSRF_TRUSTED_ORIGINS = os.environ.get(
    'DJANGO_CSRF_TRUSTED_ORIGINS',
    'http://localhost:8520,http://127.0.0.1:8520,http://localhost:8000'
).split(',')

# settings.py
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1", # Puntiamo al nome del servizio 'redis'
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


# --- ATTIVAZIONE AUTOMATICA ---
# Il controllo RUN_MAIN evita che la barra ocra appaia due volte a ogni riavvio
if os.environ.get('RUN_MAIN') == 'true':
    log_clear()