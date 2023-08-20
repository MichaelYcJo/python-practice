from .base import *
from decouple import config

TEST = config("TEST", default="False") == "True"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

SECRET_KEY = config('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ['*']


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

if TEST:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "db.sqlite3",
            "TEST": {
                "NAME": "db.sqlite3",
            },
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": config("ENV_DATABASE_NAME"),
            "USER": config("ENV_DATABASE_USER"),
            "PASSWORD": config("ENV_DATABASE_PASSWORD"),
            "HOST": config("ENV_DATABASE_HOST"),
            "PORT": config("ENV_DATABASE_PORT"),
        }
    }
