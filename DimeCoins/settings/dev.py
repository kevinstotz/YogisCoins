COIN_IP_ADDRESS = "127.0.0.1"
COIN_HOSTNAME = 'coin.dime.yogishouse.com'
COIN_PORT = 10007

WEBSITE_IP_ADDRESS = "127.0.0.1"
WEBSITE_HOSTNAME = 'www.dime.yogishouse.com'
WEBSITE_PORT = 10004

DASHBOARD_IP_ADDRESS = "127.0.0.1"
DASHBOARD_HOSTNAME = 'dashboard.dime.yogishouse.com'
DASHBOARD_PORT = 10005

LOCAL_HOST = 'localhost'
LOCAL_HOST_PORT = 10004

ENGINE_IP_ADDRESS = "127.0.0.1"
ENGINE_DOMAIN = 'yogishouse.com'
ENGINE_HOSTNAME = 'api.dime' + "." + ENGINE_DOMAIN
ENGINE_PORT = 10006


from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'NAME' : "dimecoins-dev",
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'read_default_file': join('C:/', 'ProgramData/', 'MySQL', 'MySQL Server 5.7/', 'my.ini'),
        },
    },
    'dimeAPI': {
        'NAME': "dimeapi-dev",
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
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
