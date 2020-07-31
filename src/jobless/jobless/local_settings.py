import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DB_DEFAULT_CONFIG = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'jobless_2',
    'USER' : 'admin',
    'PASSWORD' : 'sargsyan123',
    'HOST' : '127.0.0.1',
    'PORT' : '5432',
}

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

MEDIA_URL = '/media/'
MEDIA_ROOT = STATIC_ROOT + "media/"