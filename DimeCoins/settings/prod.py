from .base import *
from os.path import join
from os import environ

DEBUG = False

SECRET_KEY = environ['SECRET_KEY']

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'NAME' : 'DimeCoins',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {
            'read_default_file': join('C:/', 'ProgramData/', 'MySQL', 'MySQL Server 5.7/', 'my.ini'),
        },
    }
}


try:
    from .local import *
except ImportError:
    local = None
    raise ImportError('local settings import not found')
