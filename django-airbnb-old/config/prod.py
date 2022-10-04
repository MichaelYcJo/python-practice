from google.oauth2 import service_account
from .base import *

DEBUG = os.environ['DEBUG'] == 'True'
SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = [
    '127.0.0.1',  # for local testing
    os.environ.get('CURRENT_HOST', 'localhost')
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD']
    }
}

GOOGLE_APPLICATION_CREDENTIALS = os.path.join(BASE_DIR, 'service-account.json')
DEFAULT_FILE_STORAGE = 'config.storage_backends.GoogleCloudMediaStorage'
STATICFILES_STORAGE = 'config.storage_backends.GoogleCloudStaticStorage'
GS_PROJECT_ID = 'weinteract-develop'
GS_MEDIA_BUCKET_NAME = 'weinteract-develop-media'
GS_STATIC_BUCKET_NAME = 'weinteract-develop-static'
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    GOOGLE_APPLICATION_CREDENTIALS
)

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'https://storage.googleapis.com/{}/'.format(GS_STATIC_BUCKET_NAME)
# collect static directory (located OUTSIDE the base directory)
# TODO: configure the name and path to your static bucket directory (where collectstatic will copy to)
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'static')
STATICFILES_DIRS = [
    # TODO: configure the name and path to your development static directory
    os.path.join(BASE_DIR, 'static'),  # static directory (in the top level directory) for local testing
]

MEDIA_URL = 'https://storage.googleapis.com/{}/'.format(GS_MEDIA_BUCKET_NAME)

CORS_ORIGIN_WHITELIST = [
    FRONT_HOST,
    'http://localhost:3000'
]