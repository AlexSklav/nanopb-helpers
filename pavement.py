import os
import shutil
import sys
import re
from paver.easy import task, needs, error, cmdopts, path
from paver.setuputils import setup

sys.path.insert(0, '.')
import version


setup(name='nanopb_helpers',
      version=version.getVersion(),
      description='Cross-platform Python API for `nanopb`',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='http://github.com/wheeler-microfluidics/nanopb_helpers.git',
      license='GPLv2',
      install_requires=['path_helpers'],
      packages=['nanopb_helpers'],
      include_package_data=True)


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass


@task
@needs('generate_setup', 'minilib', 'setuptools.command.bdist_wheel')
def bdist_wheel():
    """Overrides bdist_wheel to make sure that our setup.py is generated."""
    pass
