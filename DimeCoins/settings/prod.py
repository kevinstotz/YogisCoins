
WEBSITE_IP_ADDRESS = "127.0.0.1"
WEBSITE_HOSTNAME = 'www.yogishouse.com'
WEBSITE_PORT = 10004

DASHBOARD_IP_ADDRESS = "127.0.0.1"
DASHBOARD_HOSTNAME = 'dashboard.yogishouse.com'
DASHBOARD_PORT = 10004

LOCAL_HOST = 'localhost'
LOCAL_HOST_PORT = 10004

ENGINE_IP_ADDRESS = "127.0.0.1"
ENGINE_DOMAIN = 'yogishouse.com'
ENGINE_HOSTNAME = 'api' + "." + ENGINE_DOMAIN
ENGINE_PORT = 10006



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
