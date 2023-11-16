#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import setup

import versioneer


setup(name='nanopb_helpers',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='Cross-platform Python API for `nanopb`',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='http://github.com/sci-bots/nanopb_helpers.git',
      license='GPLv2',
      install_requires=['nanopb'],
      packages=['nanopb_helpers'],
      include_package_data=True)
