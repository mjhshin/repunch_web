# Django settings for repunch project.
from django.conf.global_settings import EMAIL_HOST_USER, EMAIL_PORT,\
    EMAIL_USE_TLS, EMAIL_HOST_PASSWORD
import os

# SERVER SIDE SHOULD ALWAYS HAVE DEBUG FALSE!
DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Used in notification templates
MAIN_TRANSPORT_PROTOCOL = "https"

if DEBUG:
    FS_SITE_DIR = os.getcwd()
else:
    FS_SITE_DIR = "/home/ubuntu/Repunch/repunch_web"

ADMINS = (
    ('Vandolf Estrellado', 'vandolf@repunch.com'),
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

# this 1 is for django
AUTH_USER_MODEL = 'accounts.Account'

# configuration for SMTP
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'support@repunch.com'
EMAIL_HOST_PASSWORD = 'REPunch7575'
EMAIL_USE_TLS = True
# for order_placed event
if DEBUG:
    ORDER_PLACED_EMAILS = ['vandolf@repunch.com']
else:
    ORDER_PLACED_EMAILS = ['vandolf@repunch.com', 'matt@repunch.com',
        'mike@repunch.com']
# for template rendering
if DEBUG:
    ABSOLUTE_HOST = 'localhost:8000'
    ABSOLUTE_HOST_ALIAS = ABSOLUTE_HOST
else:
    ABSOLUTE_HOST = 'ec2-23-20-15-30.compute-1.amazonaws.com'
    ABSOLUTE_HOST_ALIAS = "repunch.com"

# PARSE 
PARSE_VERSION = '1'
PARSE_APPLICATION_ID = "m0EdwpRYlJwttZLZ5PUk7y13TWCnvSScdn8tfVoh"
PARSE_MASTER_KEY = 'K78G9D3mBk3vmSRh90D7T2cv1v41JXrJg0vv2kUB'
REST_API_KEY = "LVlPD43KJK4oGsP5f8ItFCA7RD4fwahTKQYRudod"
PARSE_IMAGE_DIMENSIONS = (300, 300)
SUPPORTED_IMAGE_FORMATS = ("png", "jpg", "jpeg")
REST_CONNECTION_META = {
       "X-Parse-Application-Id": PARSE_APPLICATION_ID,
       "X-Parse-REST-API-Key":REST_API_KEY
}

USER_CLASS = "Account"


if DEBUG:
    # PAYPAL SANDBOX credentials need to use LIVE for the real thing
    # endpoint = api.sandbox.paypal.com
    PAYPAL_CLIENT_ID = "AaRn0BC74DY7UloGyRv8DBt8VmfK2QpDuTqQF_LYVTpejKftwlUCueD3jM7R"
    PAYPAL_CLIENT_SECRET = "ELBn1BAQJOfiELEr04BA5NQieEpUe6MjT_dbSt0Vu0lA-8iuvefJfH8tUJPX"
    PAYPAL_ENDPOINT = "api.sandbox.paypal.com"
else:
    # PAYPAL LIVE credentials
    # endpoint = api.paypal.com
    PAYPAL_CLIENT_ID = "AfVmThAEY5V081CmZwFMRiCE642CT5lYeV9Yb3E2SNXC1Ru1L_I0IuZqewwZ"
    PAYPAL_CLIENT_SECRET = "ECNDuRAEYaO8YPFu2pGkoetFEN1tZ0qL1ACuZfKzsECTYV1RxTbB14l9WCdR"
    PAYPAL_ENDPOINT = "api.paypal.com"


# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['ec2-23-20-15-30.compute-1.amazonaws.com', 'localhost', 
'repunch.com', 'www.repunch.com', 'vandolf.repunch.com', '23.20.15.30']
# note that the first ec2 host is repunch dev.
# The second 1 is the real repunch.

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
if DEBUG:
    MEDIA_ROOT = os.getcwd() + '/media'
else:
    MEDIA_ROOT = FS_SITE_DIR+'/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
# Actually, this has been setup so that collectstatic does not have to 
# be run. All static files are in /static for production and deployment.
if DEBUG:
    STATIC_ROOT = '/static'
else:
    STATIC_ROOT = FS_SITE_DIR+'/static'
    
# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

"""
# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    FS_SITE_DIR+"/static",
    # os.getcwd() + '/static',
    # getcwd at aws ec2 returns '/' (the document root?)
)
"""

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
    # https://docs.djangoproject.com/en/1.5/ref/clickjacking/
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'repunch.urls'
LOGIN_URL = '/manage/'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'repunch.wsgi.application'

"""
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    FS_SITE_DIR+'/templates',
    # os.getcwd() + '/templates', 
)
"""

if DEBUG:
    TEMPLATE_DIRS = (os.getcwd() + '/templates', )
    STATICFILES_DIRS = (os.getcwd() + '/static', )
else:
    TEMPLATE_DIRS = (FS_SITE_DIR + '/templates', )
    STATICFILES_DIRS = (FS_SITE_DIR + '/static', )
    
# order placed on smartphones
PHONE_COST_UNIT_COST = 149
# paginator
PAGINATION_THRESHOLD = 20
# days given before account is disabled when passed user limit
USER_LIMIT_PASSED_DISABLE_DAYS = 14

# SESSION POLICIES
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# COMET APPROACH
if DEBUG:
    COMET_REQUEST_RECEIVE =\
        "http://localhost:8000/manage/comet/receive/"
else:
    COMET_REQUEST_RECEIVE = MAIN_TRANSPORT_PROTOCOL +\
        '://www.repunch.com/manage/comet/receive/'

# force responding to requests and getting a new request from the
# client every 4 minutes
# client timeout is 5 mins just in case.
REQUEST_TIMEOUT = 240 # in seconds 
# check for new stuff in the cache every 4 seconds
COMET_REFRESH_RATE = 4

# Note about clearing the session store. We do not need to manually
# clear the session because "caches automatically delete stale data"
# https://docs.djangoproject.com/en/dev/topics/http/sessions/
# #clearing-the-session-store

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
    'apps.db_static',
    'apps.workbench',
    'apps.comet',
    'apps.scripts',
    'libs.repunch',

    'django_extensions',
)

# Also see Cache arguments for extra options
# https://docs.djangoproject.com/en/1.5/topics/cache/#cache-arguments
# Dont forget to install memcached service and run it.
# Also need the python-memcached module installed.
CACHES = {
    'default': {
        'BACKEND':\
            'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211', # can be a list!
        'TIMEOUT': 900, # 15 mins
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

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
