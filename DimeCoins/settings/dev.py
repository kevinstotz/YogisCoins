
WEBSITE_IP_ADDRESS = "127.0.0.1"
WEBSITE_HOSTNAME = 'www.dime.yogishouse.com'
WEBSITE_PORT = 10004

DASHBOARD_IP_ADDRESS = "127.0.0.1"
DASHBOARD_HOSTNAME = 'dashboard.dime.yogishouse.com'
DASHBOARD_PORT = 10004

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
        'HOST': 'dev.cdt994n5tnkz.us-west-2.rds.amazonaws.com',
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
