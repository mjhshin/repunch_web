# Django settings for repunch project.
from django.conf.global_settings import EMAIL_HOST_USER, EMAIL_PORT,\
    EMAIL_USE_TLS, EMAIL_HOST_PASSWORD
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

FS_SITE_DIR = "/opt/bitnami/apps/repunch.com"

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'repunch',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'repunch_admin',
        'PASSWORD': 'r3puNch2013!',
        'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                      # Set to empty string for default.
    }
}

# configuration for SMTP
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'testuser@cambiolabs.com'
EMAIL_HOST_PASSWORD = 'T3st1T2013!'
EMAIL_USE_TLS = True

# PARSE 
PARSE_VERSION = '1'
PARSE_APPLICATION_ID = "m0EdwpRYlJwttZLZ5PUk7y13TWCnvSScdn8tfVoh"
PARSE_MASTER_KEY = 'K78G9D3mBk3vmSRh90D7T2cv1v41JXrJg0vv2kUB'
REST_API_KEY = "LVlPD43KJK4oGsP5f8ItFCA7RD4fwahTKQYRudod"

REST_CONNECTION_META_JSON = {
       "X-Parse-Application-Id": PARSE_APPLICATION_ID,
       "X-Parse-REST-API-Key":REST_API_KEY,
       "Content-Type": "application/json"
}
REST_CONNECTION_META_PNG = {
       "X-Parse-Application-Id": PARSE_APPLICATION_ID,
       "X-Parse-REST-API-Key":REST_API_KEY,
       "Content-Type": "image/png"
}
USER_CLASS = "Account"

# PAYPAL
PAYPAL_CLIENT_ID = "EBWKjlELKMYqRNQ6sYvFo64FtaRLRR5BdHEESmha49TM"
PAYPAL_CLIENT_SECRET = "EO422dn3gQLgDbuwqTjzrFgFtaRLRR5BdHEESmha49TM"
PAYPAL_MODE = "sandbox"

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['stage.repunch.com', 'repunch.com', 'www.repunch.com']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "America/New_York"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.djhtml
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = FS_SITE_DIR+'/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = FS_SITE_DIR+'/static'

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #FS_SITE_DIR+"/static",
    os.getcwd() + '/static',
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
#    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0frrve^tq7+zj%f$#u46iquw)u(&d&kn1#=1cp7ca3fipwd)i2'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.static',
    'django.core.context_processors.media',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'repunch.urls'
LOGIN_URL = '/manage/'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'repunch.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    FS_SITE_DIR+'/templates',
    os.getcwd() + '/templates', 
)

AUTH_USER_MODEL = 'accounts.Account'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    #'django.contrib.admindocs',
    #'django_extensions',
    'apps.public',
	'apps.stores',
    'apps.patrons',
    'apps.accounts',
    'apps.employees',
	'apps.rewards',
	'apps.messages',
    'apps.analysis',
    'libs.repunch',

    'django_extensions',
)


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
