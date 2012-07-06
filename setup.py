#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='soaring_club',
      version='0.1',
      packages=find_packages(),
      package_data={'soaring_club': ['bin/*.*', 'static/*.*', 'templates/*.*']},
      exclude_package_data={'soaring_club': ['bin/*.pyc']},
      scripts=['soaring_club/bin/manage.py', 'soaring_club/bin/colors.py'])
