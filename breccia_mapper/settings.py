"""
Django settings for breccia_mapper project.

Generated by 'django-admin startproject' using Django 2.2.9.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/

Before production deployment, see
https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/
"""

import collections
import logging
import logging.config
import pathlib

from django.urls import reverse_lazy

from decouple import config, Csv
import dj_database_url


# Settings exported to templates
# https://github.com/jakubroztocil/django-settings-export

SETTINGS_EXPORT = [
    'DEBUG',
    'PROJECT_LONG_NAME',
    'PROJECT_SHORT_NAME',
]


PROJECT_LONG_NAME = config('PROJECT_LONG_NAME', default='Project Long Name')
PROJECT_SHORT_NAME = config('PROJECT_SHORT_NAME', default='shortname')


# Build paths inside the project like this: BASE_DIR.joinpath(...)
BASE_DIR = pathlib.Path(__file__).parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='*' if DEBUG else '127.0.0.1,localhost,localhost.localdomain',
    cast=Csv()
)


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'bootstrap4',
    'constance',
    'constance.backends.database',
    'dbbackup',
    'django_countries',
    'django_select2',
    'rest_framework',
]

FIRST_PARTY_APPS = [
    'people',
    'activities',
    'export',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + FIRST_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'breccia_mapper.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.joinpath('breccia_mapper', 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django_settings_export.settings_export',
                'constance.context_processors.config',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'breccia_mapper.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': config(
        'DATABASE_URL',
        default='sqlite:///' + str(BASE_DIR.joinpath('db.sqlite3')),
        cast=dj_database_url.parse
    )
}

# Django DBBackup
# https://django-dbbackup.readthedocs.io/en/stable/index.html

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {
    'location': config('DBBACKUP_STORAGE_LOCATION', default=BASE_DIR.joinpath('.dbbackup')),
}


# Django REST Framework
# https://www.django-rest-framework.org/

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework_csv.renderers.CSVRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Custom user model
# https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project

AUTH_USER_MODEL = 'people.User'

# Login flow

LOGIN_URL = reverse_lazy('login')

LOGIN_REDIRECT_URL = reverse_lazy('index')


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR.joinpath('static')

STATICFILES_DIRS = [
    BASE_DIR.joinpath('breccia_mapper', 'static')
]


# Logging - NB the logger name is empty to capture all output

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': config('LOG_LEVEL', default='INFO'),
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': config('LOG_FILENAME', default='debug.log'),
            'when': 'midnight',
            'backupCount': config('LOG_DAYS', default=14, cast=int),
            'formatter': 'timestamped',
        },
        'console': {
            'level': config('LOG_LEVEL', default='INFO'),
            'class': 'logging.StreamHandler',
            'formatter': 'timestamped',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': config('LOG_LEVEL', default='INFO'),
            'propagate': True,
        },
    },
    'formatters': {
        'timestamped': {
            'format': '[{asctime} {levelname} {module} {funcName}] {message}',
            'style': '{',
        }
    }
}

# Initialise logger now so we can use it in this file

LOGGING_CONFIG = None
logging.config.dictConfig(LOGGING)
logger = logging.getLogger(__name__)


# Admin panel variables

CONSTANCE_CONFIG = collections.OrderedDict([
    ('NOTICE_TEXT', ('', 'Text to be displayed in a notice banner at the top of every page.')),
    ('NOTICE_CLASS', ('alert-warning', 'CSS class to use for background of notice banner.')),
])

CONSTANCE_CONFIG_FIELDSETS = {
    'Notice Banner': ('NOTICE_TEXT', 'NOTICE_CLASS'),
}

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'


# Bootstrap settings
# See https://django-bootstrap4.readthedocs.io/en/latest/settings.html

BOOTSTRAP4 = {
    'include_jquery': 'full',
}


# Import customisation app settings if present

TEMPLATE_NAME_INDEX = 'index.html'

try:
    from custom.settings import (
        CUSTOMISATION_NAME,
        TEMPLATE_NAME_INDEX
    )
    logger.info("Loaded customisation app: %s", CUSTOMISATION_NAME)

    INSTALLED_APPS.append('custom')

except ImportError as e:
    logger.info("No customisation app loaded: %s", e)
