from paver.easy import task, needs
from paver.setuputils import setup
from finddata import find_package_data

import version


setup(name='nanopb_helpers',
      version=version.getVersion(),
      description='Cross-platform Python API for `nanopb`',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='http://github.com/wheeler-microfluidics/nanopb_helpers.git',
      license='GPLv2',
      install_requires=['path_helpers'],
      packages=['nanopb_helpers', 'nanopb_helpers.bin'],
      package_data=find_package_data())


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
