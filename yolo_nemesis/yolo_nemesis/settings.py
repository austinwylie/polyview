"""
Django settings for yolo_nemesis project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""


# TODO: Let's look into this:
# http://www.webforefront.com/django/configuredjangosettings.html

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r2l6wv@(-q5)p^djq4(41bfq@9@v*%@tc!%ck!-lwb*%f43h09'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = [
    'calpoly.io',  # Allow domain and subdomains
    '.calpoly.io',  # Allow domain and subdomains
    '.calpoly.io.',  # Also allow FQDN and subdomains
    'polyview.io',  # Allow domain and subdomains
    '.polyview.io',  # Allow domain and subdomains
    '.polyview.io.',  # Also allow FQDN and subdomains
    'localhost',  # Also allow FQDN and subdomains
    '127.0.0.1',  # Also allow FQDN and subdomains
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cparse',
    'django_jinja',
    'django_jinja.contrib._humanize',
    'django.contrib.humanize',
    
)

TEMPLATE_LOADERS = (
    'django_jinja.loaders.FileSystemLoader', 'django_jinja.loaders.AppLoader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.messages.context_processors.messages',
    'django.contrib.auth.context_processors.auth',
)

# DEFAULT_JINJA2_TEMPLATE_EXTENSION = '.jinja'
DEFAULT_JINJA2_TEMPLATE_INTERCEPT_RE = r"^.*_jinja\..*$"

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'yolo_nemesis.urls'

WSGI_APPLICATION = 'yolo_nemesis.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    # 'default': {
    # 'ENGINE': 'django.db.backends.mysql',
    #
    #     # Pick one
    #     # 'NAME': 'yolo_nemesis', # Production
    #      'NAME': 'yolo_nemesis_t', # Taylor sandbox
    #
    #     # Pick one
    #     # 'USER': 'yolo_nemesis', # Production
    #      'USER': 'yolo_nemesis_t', # Taylor sandbox
    #
    #     'PASSWORD': 'nemesis_yolo2015',  # Production and sandbox
    #     'OPTIONS': {'charset': 'utf8mb4'},
    #
    #     'HOST': 'yolo-nemesis.cdivb6owmscf.us-west-2.rds.amazonaws.com',
    #     # Azure
    #     # 'HOST': '127.0.0.1', # local
    #
    #     'PORT': '3306',
    # }


    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'yolo_nemesis',
        # 'HOST': '/opt/bitnami/postgresql',
        'HOST': 'calpoly.io',
        'PORT': '5432',
        'USER': 'postgres',
        'PASSWORD': 'Af7YOJgkTMnN'
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

# STATIC_URL = '/static/'

STATIC_URL = '/static/'
