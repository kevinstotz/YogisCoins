from os.path import join, abspath, dirname, relpath, realpath
from os import environ

WEBSITE_IP_ADDRESS = ""
WEBSITE_HOSTNAME = ""
WEBSITE_PORT = ""
WEBSITE_HOSTNAME_AND_PORT = ""
WEBSITE_HOSTNAME_URL = ""

DASHBOARD_IP_ADDRESS = ""
DASHBOARD_HOSTNAME = ""
DASHBOARD_PORT = ""
DASHBOARD_HOSTNAME_AND_PORT = ""

LOCAL_HOST = ""
LOCAL_HOST_PORT = ""
LOCAL_HOST_AND_PORT = ""

ENGINE_IP_ADDRESS = ""
ENGINE_DOMAIN = ""
ENGINE_HOSTNAME = ""
ENGINE_PORT = ""
ENGINE_HOSTNAME_AND_PORT = ""

COIN_HOSTNAME_AND_PORT = ""
COIN_IP_ADDRESS = ""
COIN_HOSTNAME = ""
COIN_PORT = ""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = abspath(dirname(__name__))  # .../DimeCoins
PROJECT_DIR = dirname(dirname(abspath(__file__)))  # .../DimeCoins/DimeCons
SETTINGS_DIR = dirname(realpath(__file__))  # .../DimeCoins/DimeCoins/settings
PROJECT_NAME = relpath(PROJECT_DIR)  # DimeCoins


SECURE = 'https://'
UNSECURE = 'http://'
if 'dev' in environ['DJANGO_SERVER_TYPE'].lower():
    DEBUG = True
    DJANGO_LOG_LEVEL = DEBUG

    WEBSITE_IP_ADDRESS = "127.0.0.1"
    WEBSITE_HOSTNAME = 'www.dime.yogishouse.com'
    WEBSITE_PORT = 10004

    DASHBOARD_IP_ADDRESS = "127.0.0.1"
    DASHBOARD_HOSTNAME = 'dashboard.dime.yogishouse.com'
    DASHBOARD_PORT = 10005

    ENGINE_IP_ADDRESS = "127.0.0.1"
    ENGINE_DOMAIN = 'yogishouse.com'
    ENGINE_HOSTNAME = 'api.dime' + "." + ENGINE_DOMAIN
    ENGINE_PORT = 10006

    COIN_IP_ADDRESS = "127.0.0.1"
    COIN_HOSTNAME = 'coin.dime.yogishouse.com'
    COIN_PORT = 10007

    WEBSITE_HOSTNAME_AND_PORT = WEBSITE_HOSTNAME + ":" + str(WEBSITE_PORT)
    WEBSITE_HOSTNAME_URL = UNSECURE + WEBSITE_HOSTNAME + ":" + str(WEBSITE_PORT)

    DASHBOARD_HOSTNAME_AND_PORT = DASHBOARD_HOSTNAME + ":" + str(DASHBOARD_PORT)
    DASHBOARD_HOSTNAME_URL = UNSECURE + DASHBOARD_HOSTNAME + ":" + str(DASHBOARD_PORT)

    LOCAL_HOST = 'localhost'
    LOCAL_HOST_PORT = 10004
    LOCAL_HOST_AND_PORT = LOCAL_HOST + str(LOCAL_HOST_PORT)

    ENGINE_HOSTNAME_NO_PORT = UNSECURE + ENGINE_HOSTNAME
    ENGINE_HOSTNAME_AND_PORT = ENGINE_HOSTNAME + ":" + str(ENGINE_PORT)
    ENGINE_HOSTNAME_URL = UNSECURE + ENGINE_HOSTNAME + ":" + str(ENGINE_PORT)

    COIN_HOSTNAME_AND_PORT = COIN_HOSTNAME + ":" + str(COIN_PORT)
    COIN_HOSTNAME_URL = UNSECURE + COIN_HOSTNAME + ":" + str(COIN_PORT)

if 'prod' in environ['DJANGO_SERVER_TYPE'].lower():
    DEBUG = True
    DJANGO_LOG_LEVEL = DEBUG

    WEBSITE_IP_ADDRESS = "127.0.0.1"
    WEBSITE_HOSTNAME = 'www.yogishouse.com'
    WEBSITE_PORT = 10004

    DASHBOARD_IP_ADDRESS = "127.0.0.1"
    DASHBOARD_HOSTNAME = 'dashboard.yogishouse.com'
    DASHBOARD_PORT = 10005

    ENGINE_IP_ADDRESS = "127.0.0.1"
    ENGINE_DOMAIN = 'yogishouse.com'
    ENGINE_HOSTNAME = 'api' + "." + ENGINE_DOMAIN
    ENGINE_PORT = 10006

    COIN_IP_ADDRESS = "127.0.0.1"
    COIN_HOSTNAME = 'coin.yogishouse.com'
    COIN_PORT = 10007

    WEBSITE_HOSTNAME_AND_PORT = WEBSITE_HOSTNAME + ":" + str(WEBSITE_PORT)
    WEBSITE_HOSTNAME_URL = UNSECURE + WEBSITE_HOSTNAME + ":" + str(WEBSITE_PORT)

    DASHBOARD_HOSTNAME_AND_PORT = DASHBOARD_HOSTNAME + ":" + str(DASHBOARD_PORT)
    DASHBOARD_HOSTNAME_URL = UNSECURE + DASHBOARD_HOSTNAME + ":" + str(DASHBOARD_PORT)

    LOCAL_HOST = 'localhost'
    LOCAL_HOST_PORT = 10004
    LOCAL_HOST_AND_PORT = LOCAL_HOST + str(LOCAL_HOST_PORT)

    ENGINE_HOSTNAME_NO_PORT = SECURE + ENGINE_HOSTNAME
    ENGINE_HOSTNAME_AND_PORT = ENGINE_HOSTNAME + ":" + str(ENGINE_PORT)
    ENGINE_HOSTNAME_URL = SECURE + ENGINE_HOSTNAME + ":" + str(ENGINE_PORT)

    COIN_HOSTNAME_AND_PORT = COIN_HOSTNAME + ":" + str(COIN_PORT)
    COIN_HOSTNAME_URL = SECURE + COIN_HOSTNAME + ":" + str(COIN_PORT)

ALLOWED_HOSTS = [ENGINE_HOSTNAME, COIN_HOSTNAME]

# Application definition
AUTH_USER_MODEL = 'DimeAPI.CustomUser'

INSTALLED_APPS = [
    'DimeCoins',
    'DimeAPI',
    'corsheaders',
    'rest_framework',
    'django_user_agents',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]


SECURE_HSTS_INCLUDE_SUBDOMAINS = 'True'


USER_AGENTS_CACHE = 'default'
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = True
CSRF_COOKIE_DOMAIN = '.' + ENGINE_DOMAIN
CSRF_TRUSTED_ORIGINS = (
    ENGINE_HOSTNAME,
    COIN_HOSTNAME,
    WEBSITE_HOSTNAME,
    DASHBOARD_HOSTNAME
)

ROOT_URLCONF = PROJECT_NAME + '.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

INTERNAL_IPS = [
    ENGINE_IP_ADDRESS,
    WEBSITE_IP_ADDRESS,
    COIN_IP_ADDRESS,
    DASHBOARD_IP_ADDRESS
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s:%(asctime)s:%(module)s:%(name)s:%(process)d:%(thread)d:%(message)s'
        },
        'simple': {
            'format': '%(levelname)s:%(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': join(PROJECT_DIR, 'log', 'debug.log'),
            'formatter': 'verbose',
        },
        'request_handler': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': join(PROJECT_DIR, 'log', 'debug-request.log'),
            'formatter': 'verbose',
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG'
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

CORS_ORIGIN_WHITELIST = (
    LOCAL_HOST_AND_PORT,
    COIN_HOSTNAME_AND_PORT,
    WEBSITE_HOSTNAME_AND_PORT,
    DASHBOARD_HOSTNAME_AND_PORT,
    ENGINE_HOSTNAME_AND_PORT
)

CORS_ORIGIN_ALLOW_ALL = False

CORS_ALLOW_HEADERS = (
    'x-requested-with',
    'content-type',
    'Access-Control-Allow-Origin',
    'accept',
    'origin',
    'accept-encoding',
    'csrftoken',
    'Redirect',
    'authorization',
    'X-CSRFToken',
    'X-CSRF-TOKEN'
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    'GET',
    'POST',
    'PUT',
    'PATCH',
    'DELETE',
    'OPTIONS'
)
# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'NAME': 'YogisCoins',
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'dev.cdt994n5tnkz.us-west-2.rds.amazonaws.com',
        'PORT': 3306,
        'OPTIONS': {
            'read_default_file': join('C:/', 'ProgramData/', 'MySQL', 'MySQL Server 5.7/', 'my.ini'),
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],

    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'PAGINATE_BY': 20,
    'PAGINATE_BY_PARAM': 'page_size',
    'MAX_PAGINATE_BY': 100
}

# 'DEFAULT_FILTER_BACKENDS':  ('rest_framework.filters.DjangoFilterBackend',),

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
STATIC_URL = '/static/'
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False

SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
SESSION_COOKIE_HTTPONLY = False

EMAIL_SERVER = {
    'HOST': 'smtp.mailtrap.io',
    'USER': 'c8bed2fa6aecd1',
    'PASSWORD': '4eaf0f51577f20',
    'PORT': 2525
}
PASSWORD_LENGTH = 20
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailtrap.io'
EMAIL_PORT = 2525
EMAIL_HOST_USER = 'c8bed2fa6aecd1'
EMAIL_HOST_PASSWORD = '4eaf0f51577f20'
EMAIL_TIMEOUT = 10
EMAIL_LENGTH = 100

EMAIL_TEMPLATE_DIR = join(PROJECT_NAME, 'EmailTemplates')
EMAIL_FROM_DOMAIN = 'yogishouse.com'
EMAIL_LOGIN_URL = WEBSITE_HOSTNAME_URL + '/auth/login'
EMAIL_VERIFY_ACCOUNT_URL = WEBSITE_HOSTNAME_URL + '/register/verify/'
EMAIL_VERIFY_TRACK_URL = WEBSITE_HOSTNAME_URL + '/api/statistics/track.png?auth='
FORGOT_PASSWORD_URL = WEBSITE_HOSTNAME_URL + '/account/forgotPassword/'
PASSWORD_RESET_URL = WEBSITE_HOSTNAME_URL + '/account/resetPassword/'
AUTHORIZATION_CODE_VALID_TIME_IN_SECONDS = 60 * 60 * 24  # 1 day
#  User Status

XCHANGE = {
    'CRYPTO_COMPARE': 1,
    'GDAX': 2,
    'COINBASE': 3,
    'COINDESK': 4,
    'COIN_MARKET_CAP': 5,
    'COIN_API': 6,
    'BITTREX': 7,
    'KRAKEN': 8,
    'CRYPTOINDEX': 9,
    'BITSTAMP': 10,
    'POLONIEX': 13
}

ADDRESS_LENGTH = 42
URL_LENGTH = 100
CURRENCY_NAME_LENGTH = 50
CURRENCY_SYMBOL_LENGTH = 10
CURRENCY_FULL_NAME_LENGTH = 100
ICON_NAME_LENGTH = 30

FUND_PERIOD = {
    'DAY': 1,
    'WEEK': 2,
    'MONTH': 3,
    'QUARTER': 4,
    'YEAR': 5
}
