# -*- coding: utf-8 -*-
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'd9!y*=h!g&l4nj_rk$zvt_g!7&1wmzvwrj-=jxj1q$d#d6gad('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SITE_ID = 1

ADMIN_SITE_HEADER = 'Администрирование Garlnd'

ALLOWED_HOSTS = ['*']

AUTH_USER_MODEL = 'custom_auth.CustomUser'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DEFAULT_MAX_MAPS_COUNT = 3 #Количество карт по умолчанию
DEFAULT_MAX_LOCATIONS_COUNT = 50 #Количество адресов по умолчанию
DEFAULT_MAX_DEVICES_COUNT = 3 #Количество трэкеров по умолчанию
DEFAULT_MAX_LOCATIONS_TYPES_FACTOR = 0.1 #Максимальное количество типов количество адресов * коэффицент
DEFAULT_MAX_STATUSES_PER_LOCATION = 10
DEFAULT_MAX_RULES_COUNT = 4
DEFAULT_MAX_TRACKS_COUNT = 50
DEFAULT_MAX_SCHEDULE_EVENTS_COUNT = 10
DEFAULT_MAX_GRATICULES_COUNT = 3
DEFAULT_GRATICULE_CELL_SIZE = 0.1

DEFAULT_MAP_LONGITUDE = 30.313497 #широта
DEFAULT_MAP_LATITUDE = 59.938531 #дологота
DEFAULT_MAP_ZOOM = 11

SITE_NAME = 'GΛRLND α'
SEND_EMAILS = True #make it True and edit settings bellow if you want to receive emails
EMAIL_ADDRESS_FROM = 'noreply@garlnd.ru'
DEFAULT_FROM_EMAIL = EMAIL_ADDRESS_FROM
EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_HOST_USER = 'noreply@garlnd.ru'
EMAIL_HOST_PASSWORD = 'nbXxvD00Ra'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_PORT = 645

# Application definition

INSTALLED_APPS = (
    'channels',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'bootstrap_toolkit',
    'django_bootstrap5',
    # 'password_required',
    'registration',
    'brake',
    'captcha',
    'apps.account',
    # 'graticules', #Сетки для карт
    'apps.devices',  #Трэкеры
    'apps.maps',  #Карты
    'apps.positions',  #Запись позиций трэкеров
    'apps.tracks', #Формирование трэков из позиций
    'apps.rules', #Правила наблюдения за позицией
    'apps.custom_auth',
    'apps.custom_registration',
    'apps.notifications'
)

MIDDLEWARE = (
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware'
)

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#         'LOCATION': '/var/tmp/garlnd_cache',
#         'TIMEOUT': 60,
#         'OPTIONS': {
#             'MAX_ENTRIES': 1000
#         }
#     }
# }


TEMPLATES = [{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'utils.context_processors.site_constants',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG
        },
    },
]

ROOT_URLCONF = 'garlnd.urls'

WSGI_APPLICATION = 'garlnd.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

ADMINS = (
    ('a.sinyavskiy', 'sinyawskiy@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'garlnd',
        'USER': 'garlnd',
        'PASSWORD': 'garlnd',
        'HOST': 'garlnd_db', # 'localhost'
        'PORT': 5432,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

USE_L10N = True
USE_TZ = True
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
LANGUAGE_CODE = 'ru-R'

YANDEX_MAPS_API_KEY = 'AKEPlU8BAAAAfqPFEQQAIHdWxfzumRVqMKh2LnjH_-yrasgAAAAAAAAAAADQIGjovXF1CSqdRWrK9YTABFtR0A=='

TORNADING_KEY = 'hyCrbCGII4WDKAa4Wucr'
TORNADING_PORT = 8000
WEB_SOCKET_PORT = 8001 # Todo remove
WEB_SOCKET_HOST = '127.0.0.1'
WEB_SOCKET_BROWSER_HOST = '127.0.0.1'


ASGI_APPLICATION = "garlnd.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
    # "default": {
    #     "BACKEND": "channels_redis.core.RedisChannelLayer",
    #     "CONFIG": {
    #         "hosts": [("localhost", 6379)],
    #     },
    # },
}



MAX_ABS_ACCELERATION = 10
TIME_DELTA_BETWEEN_TRACKS = 15*60 #sec

# from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
# TEMPLATE_CONTEXT_PROCESSORS = list(TEMPLATE_CONTEXT_PROCESSORS)
# TEMPLATE_CONTEXT_PROCESSORS.append('annoying.context_processors.site_constants')

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/'
AUTH_PROFILE_MODULE = 'apps.custom_registration.CustomRegistrationProfile'

# django-registration
ACCOUNT_ACTIVATION_DAYS = 2
AUTH_USER_EMAIL_UNIQUE = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_URL = '/static/'
# DEBUG = False
STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    STATIC_DIR
]

if not DEBUG:
    STATIC_ROOT = os.path.join(BASE_DIR, 'public')  # used in collectstatic

#
# GRAPPELLI_ADMIN_TITLE = 'Администрирование %s' % SITE_NAME
# GRAPPELLI_INDEX_DASHBOARD = 'custom_grappelli.dashboard.CustomIndexDashboard'

CAPTCHA_LENGTH = 3
CAPTCHA_FONT_PATH = os.path.join(STATIC_DIR, 'captcha', 'fonts', 'Vera.ttf')
CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.random_char_challenge'
CAPTCHA_NOISE_FUNCTIONS = ('captcha.helpers.noise_dots',)
CAPTCHA_LETTER_ROTATION = (-10, 10)
# CAPTCHA_OUTPUT_FORMAT = '%(hidden_field)s %(text_field)s %(image)s'

MAX_ATTACH_FEEDBACK_FILE_SIZE = 5*1024*1024
FEEDBACK_MAIL_TO = 'feedback@garlnd.r'

SMS_URL = 'http://sms.ru/sms/send?api_id=857f60cc-3086-0f34-353f-00fa76eac6f9&to=%(to)s&text=%(text)s&test=1'

LOGGING = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
            },
        # 'file': {
        #     'level': 'DEBUG',
        #     'class': 'logging.FileHandler',
        #     'filename': '/path/to/your/file.log',
        #     'formatter': 'simple'
        #     },
        },
    'loggers': {
        'mysql': {
            'handlers': ['console'], #file
            'level': 'DEBUG',
            'propagate': True,
            },
        },
    }