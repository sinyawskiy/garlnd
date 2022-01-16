from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'garlnd',
        'USER': 'garlnd',
        'PASSWORD': 'garlnd',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}