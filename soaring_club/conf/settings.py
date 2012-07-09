# Import global settings to make it easier to extend settings. 
from django.conf.global_settings import *

#==============================================================================
# Generic Django project settings
#==============================================================================

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Rome'
USE_I18N = True
LANGUAGE_CODE = 'it-it'
DEFAULT_COUNTRY_ISO = 'IT'
SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = '+4fljb@0b!zw&v1_iq^=d13v&fbzly=k)r7x963!0*hr1a8=l1'

#==============================================================================
# Calculation of directories relative to the module location
#==============================================================================
import os
import os.path
import sys
#import soaring_club

# Work out the project module name and root directory, assuming that this file
# is located at [project]/conf/settings.py
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
)

PYTHON_BIN = os.path.dirname(sys.executable)

if os.path.exists(os.path.join(PYTHON_BIN, 'activate_this.py')):
    # Assume that the presence of 'activate_this.py' in the python bin/
    # directory means that we're running in a virtual environment. Set the
    # variable root to $VIRTUALENV/var.
    VAR_ROOT = os.path.join(os.path.dirname(PYTHON_BIN), 'var')
    if not os.path.exists(VAR_ROOT):
        os.mkdir(VAR_ROOT)
else:
    # Set the variable root to the local configuration location (which is
    # ignored by the repository).
    VAR_ROOT = os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'conf', 'local')


#==============================================================================
# Project URLS and media settings
#==============================================================================

ROOT_URLCONF = 'soaring_club.conf.urls'

#LOGIN_URL = '/accounts/login/'
#LOGOUT_URL = '/accounts/logout/'
#LOGIN_REDIRECT_URL = '/'

MEDIA_URL = '/uploads/'
MEDIA_ROOT = os.path.join(VAR_ROOT, 'uploads')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(VAR_ROOT, 'static')

STATICFILES_DIRS = (
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'static'),
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'apps/aircraftlogger/static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

LOCALE_PATHS = (
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'apps/aircraftlogger/locale'),
)

#==============================================================================
# Templates
#==============================================================================

TEMPLATE_DIRS = (
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, 'templates'),
    os.path.join(PROJECT_DIR, PROJECT_MODULE_NAME, "aircraftlogger/templates"),
)

TEMPLATE_CONTEXT_PROCESSORS += (
    # 'Custom context processors here',
    'django.core.context_processors.request',

)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',

)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.humanize',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'django.contrib.databrowse',
    'django_extensions',
    'aircraftlogger',
    'south',
    'gunicorn',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s  %(module)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}
    
AUTH_PROFILE_MODULE = 'aircraftlogger.Member'    
SESSION_COOKIE_AGE = 3600 # Default: 1209600 (2 weeks, in seconds)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

AJAX_LOOKUP_CHANNELS = {
    'contact' : ('crm.lookups', 'ContactLookup'),
    'quick_search' : ('crm.lookups', 'QuickLookup'),
}
#try:
#    from email import *
#except:
#    print "email settings import failed"

try:
    from aircraftlogger.settings import *
except ImportError:
    print "aircraftlogger.settings import error" 
