#!/usr/bin/env python
from django.core.management import execute_manager
import imp
import os.path
import sys
import traceback
from os.path import abspath, dirname, join

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'external_apps'))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'imported_apps'))

GREEN='\033[0;32m'
BGREEN='\033[1;32m'
RED='\033[0;31m'
BRED='\033[1;31m'
BLUE='\033[0;34m'
BBLUE='\033[1;34m'
YELLOW='\033[0;33m'
BYELLOW='\033[1;33m'
NORMAL='\033[00m'

try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    print BYELLOW
    print "Error: Can't find the module '%s%s%s' in the directory containing %s%r%s. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % (BGREEN,'settings',BYELLOW,BGREEN,__file__,BYELLOW)
    print NORMAL
    print "=" * 20
    print "original traceback:"
    print "=" * 20
    print
    traceback.print_exc(e)
    sys.exit(1)

import settings

try:
    print "=" * 20
    print "%sYour settings is for '%s%s%s'%s" % (BYELLOW,BRED,settings.ENV,BYELLOW,NORMAL)
    print "=" * 20
except AttributeError:
    print BYELLOW
    print "Error: you have to define your '%sENV%s' in your settings module.\nYou'll have to check your '%ssettings/__init__.py%s' and relative settings enviroment.\n" % (BGREEN,BYELLOW,BGREEN,BYELLOW)
    print NORMAL
    print "=" * 20
    print "original traceback:"
    print "=" * 20
    print
    traceback.print_exc(e)
    sys.exit(1)

if __name__ == "__main__":
    execute_manager(settings)
