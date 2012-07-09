#!/usr/bin/env python
import os
import sys
from django import get_version
from django.core.management import execute_from_command_line, LaxOptionParser
from django.core.management.base import BaseCommand
from colors import *

# Work out the project module name and root directory, assuming that this file
# is located at [project]/bin/manage.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR, PROJECT_MODULE_NAME = os.path.split(os.path.dirname(BASE_DIR))
APPS_DIR = os.path.abspath(os.path.join(BASE_DIR, '../apps'))
sys.path.append(APPS_DIR)

# Check that the project module can be imported.
try:
    __import__(PROJECT_MODULE_NAME)
except ImportError:
    # Couldn't import the project, place it on the Python path and try again.
    sys.path.append(PROJECT_DIR)
    try:
        __import__(PROJECT_MODULE_NAME)
    except ImportError:
        sys.stderr.write("Error: Can't import the \"%s\" project module." %
                         PROJECT_MODULE_NAME)
        sys.exit(1)

def has_settings_option():
    parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
                             version=get_version(),
                             option_list=BaseCommand.option_list)
    try:
        options = parser.parse_args(sys.argv[:])[0]
        if options.settings:
            print "=" * 20
            print "%s has_settings_option '%s%s%s'%s" % (BYELLOW,BRED,options.settings,BYELLOW,NORMAL)
            print "=" * 20
    except:
        return False # Ignore any option errors at this point.
    return bool(options.settings)

if not has_settings_option() and not 'DJANGO_SETTINGS_MODULE' in os.environ:
    settings_module = '%s.conf.local.settings' % PROJECT_MODULE_NAME
    os.environ['DJANGO_SETTINGS_MODULE'] = settings_module

print "=" * 20
print "%s settings module is '%s%s%s'%s" % (BYELLOW,BRED,os.environ['DJANGO_SETTINGS_MODULE'],BYELLOW,NORMAL)
print "=" * 20
execute_from_command_line()
