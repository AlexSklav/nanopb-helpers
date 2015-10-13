import os
import shutil
import sys
import re
from paver.easy import task, needs, error, cmdopts, path
from paver.setuputils import setup

import version
sys.path.insert(0, '.')


LIB_GENERATE_TASKS = ['generate_arduino_library_properties',
                      'copy_lib_contents']
LIB_CMDOPTS = [('lib_out_dir=', 'o', 'Output directory for Arduino library.')]

setup(name='nanopb_helpers',
      version=version.getVersion(),
      description='Cross-platform Python API for `nanopb`',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='http://github.com/wheeler-microfluidics/nanopb_helpers.git',
      license='GPLv2',
      install_requires=['path_helpers'],
      packages=['nanopb_helpers', 'nanopb_helpers.bin'],
      include_package_data=True)


def recursive_overwrite(src, dest, ignore=None):
    '''
    http://stackoverflow.com/questions/12683834/how-to-copy-directory-recursively-in-python-and-overwrite-all#15824216
    '''
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f),
                                    os.path.join(dest, f),
                                    ignore)
    else:
        shutil.copyfile(src, dest)


def verify_library_directory(options):
    '''
    Must be called from task function accepting `LIB_CMDOPTS` as `cmdopts`.
    '''
    import inspect
    import nanopb_helpers as npb

    print '[verify_library_directory]', inspect.currentframe().f_back.f_code.co_name
    cmd_opts = getattr(options, inspect.currentframe().f_back.f_code.co_name)
    output_dir = path(getattr(cmd_opts, 'lib_out_dir',
                              npb.get_lib_directory()))
    library_dir = output_dir.joinpath('nanopb')
    library_dir.makedirs_p()
    return library_dir


@task
@cmdopts(LIB_CMDOPTS, share_with=LIB_GENERATE_TASKS)
def generate_arduino_library_properties(options):
    import nanopb_helpers as npb

    match = re.search(r'nanopb-(?P<version>\d+\.\d+\.\d+)-',
                      npb.get_nanopb_root().name)
    library_dir = verify_library_directory(options)
    library_properties = library_dir.joinpath('library.properties')

    with library_properties.open('wb') as output:
        print >> output, '''
name=nanopb
version=%s
author=Petteri Aimonen <jpa at nanopb.mail.kapsi.fi>
maintainer=Christian Fobel <christian@fobel.net>
sentence=Nanopb is a plain-C implementation of Google's Protocol Buffers data format.
paragraph=It is targeted at 32 bit microcontrollers, but is also fit for other embedded systems with tight (2-10 kB ROM, <1 kB RAM) memory
category=Communication
url=http://koti.kapsi.fi/jpa/nanopb/
architectures=avr'''.strip() % match.group('version')


@task
@cmdopts(LIB_CMDOPTS, share_with=LIB_GENERATE_TASKS)
def copy_lib_contents(options):
    import nanopb_helpers as npb

    source_dir = npb.get_nanopb_root()
    lib_dir = npb.get_lib_directory().joinpath('nanopb')
    target_dir = lib_dir.joinpath('src')
    if not target_dir.isdir():
        target_dir.makedirs_p()
    for f in source_dir.files():
        f.copy(target_dir.joinpath(f.name))
    with target_dir.joinpath('nanopb.h').open('wb') as output:
        print >> output, '#include "pb.h"'
    target_dir = verify_library_directory(options)
    if lib_dir.realpath() != target_dir.realpath():
        recursive_overwrite(lib_dir, target_dir)


@task
@needs('copy_lib_contents', 'generate_arduino_library_properties')
def build_arduino_library(options):
    import zipfile

    library_dir = verify_library_directory(options)
    zf = zipfile.ZipFile(library_dir + '.zip', mode='w')

    for f in library_dir.walkfiles():
        zf.write(f, arcname=library_dir.relpathto(f))
    zf.close()


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
