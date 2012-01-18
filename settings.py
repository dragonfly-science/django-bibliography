import sys

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'cuckoo.sqlite'
    }
}
MEDIA_ROOT = '.'

INSTALLED_APPS = ['bibliography']
