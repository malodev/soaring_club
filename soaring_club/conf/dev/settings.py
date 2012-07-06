# Django dev settings for soaring_club project.
from soaring_club.conf.settings import *
ENV='develop'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ROOT_URLCONF = 'soaring_club.conf.dev.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(VAR_ROOT, 'dev.db'),
    }
}

INSTALLED_APPS += (
    'django.contrib.admindocs',
)

SECRET_KEY = '0y%!euc@!d^2x#1i$&+)n4b$n0ypc7xzxd@x9@ifs8egfti#(f'
