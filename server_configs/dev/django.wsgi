import os, sys
import site

site.addsitedir('/home/mauro/Develop/soaring_club/lib/python2.7/site-packages')

sys.stdout = sys.stderr

os.environ['DJANGO_SETTINGS_MODULE'] = 'soaring_club.conf.local.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
