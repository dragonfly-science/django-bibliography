import sys

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'bibliography.sqlite'
    }
}
MEDIA_ROOT = '.'

INSTALLED_APPS = ['bibliography']
