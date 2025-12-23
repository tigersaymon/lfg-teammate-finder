from .base import *

DEBUG = False

RENDER_DOMAIN = os.environ["RENDER_DOMAIN"]

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', RENDER_DOMAIN]

# Database

DATABASES = {
 'default': {
   'ENGINE': 'django.db.backends.postgresql',
   'NAME': os.getenv('POSTGRES_DB'),
   'USER': os.getenv('POSTGRES_USER'),
   'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
   'HOST': os.getenv('POSTGRES_HOST'),
   'PORT': os.getenv('POSTGRES_DB_PORT', 5432),
   'OPTIONS': {
     'sslmode': 'require',
   },
 }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
