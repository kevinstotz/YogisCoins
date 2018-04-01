COIN_IP_ADDRESS = "172.31.2.86"
COIN_HOSTNAME = 'coin.yogishouse.com'
COIN_PORT = 10007

WEBSITE_IP_ADDRESS = "172.31.2.86"
WEBSITE_HOSTNAME = 'www.yogishouse.com'
WEBSITE_PORT = 10004

DASHBOARD_IP_ADDRESS = "172.31.2.86"
DASHBOARD_HOSTNAME = 'dashboard.yogishouse.com'
DASHBOARD_PORT = 10005

LOCAL_HOST = 'localhost'
LOCAL_HOST_PORT = 10004

ENGINE_IP_ADDRESS = "172.31.2.86"
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
        'HOST': 'dev.cdt994n5tnkz.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {
            'read_default_file': join('/', 'etc', 'mysql', 'conf.d', 'mysql.YogisCoin.cnf'),
        },
    },
    'DimeAPI': {
        'NAME': 'DimeAPI',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'dev.cdt994n5tnkz.us-west-2.rds.amazonaws.com',
        'PORT': '3306',
        'OPTIONS': {
            'read_default_file': join('/', 'etc', 'mysql', 'conf.d', 'mysql.YogisAPI.cnf'),
         },
    }
}


try:
    from .local import *
except ImportError:
    local = None
    raise ImportError('local settings import not found')
