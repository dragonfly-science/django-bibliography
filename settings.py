DEBUG = True
BIBLIOGRAPHY_DEV_MODE = True

import os
PROJECT_DIR = os.path.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'bibliography.sqlite'
    }
}
MEDIA_ROOT = '.'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',

    'taggit',
    'django_nose',

    'bibliography',
)

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, "static"),
)
STATIC_ROOT = os.path.join(PROJECT_DIR, '../static/')
STATIC_URL = '/static/'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)


TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-xunit', '--with-doctest'
    ]

ROOT_URLCONF = 'bibliography.urls'


SECRET_KEY = 'secret_key'
SITE_ID = 1
