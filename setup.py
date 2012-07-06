#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='soarign_club',
      version='0.1',
      packages=find_packages(),
      package_data={'soarign_club': ['bin/*.*', 'static/*.*', 'templates/*.*']},
      exclude_package_data={'soarign_club': ['bin/*.pyc']},
      scripts=['soarign_club/bin/manage.py'])
