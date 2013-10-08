DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'bibliography.sqlite'
    }
}
MEDIA_ROOT = '.'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.markup',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',

    'south',
    'taggit',
    'django_nose',

    'bibliography',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
NOSE_ARGS = [
    '--with-xunit', '--with-doctest'
    ]


SECRET_KEY = 'secret_key'
SITE_ID = 1
