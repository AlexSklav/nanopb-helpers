'''
Provide an API for cross-platform compiling Protocol Buffer definitions for the
following targets:

 - `nanopb` C
 - Google C++
 - Python

__NB__ The compilation is performed using bundled [`nanopb`][1]
[binary distributions][2].

`nanopb` is Copyright (c) 2011 Petteri Aimonen <jpa at nanopb.mail.kapsi.fi>
See [license][3] for more info.

[1]: http://koti.kapsi.fi/~jpa/nanopb
[2]: http://koti.kapsi.fi/~jpa/nanopb/download/
[3]: https://code.google.com/p/nanopb/source/browse/LICENSE.txt
'''
from __future__ import absolute_import
import os
import platform
import sys
import tempfile

from path_helpers import path
from subprocess import check_call
#: .. versionadded:: 0.8
import conda_helpers as ch

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def get_base_path():
    return path(__file__).parent.abspath()


def package_path():
    return path(__file__).parent


def get_lib_directory():
    '''
    Return directory containing the Arduino library headers.
    '''
    return package_path().joinpath('Arduino', 'library')


def get_exe_postfix():
    '''
    Return the file extension for executable files.
    '''
    if platform.system() in ('Linux', 'Darwin'):
        return ''
    elif platform.system() == 'Windows':
        return '.exe'
    raise 'Unsupported platform: %s' % platform.system()


def get_script_postfix():
    '''
    Return the file extension for executable files.
    '''
    if platform.system() in ('Linux', 'Darwin'):
        return ''
    elif platform.system() == 'Windows':
        return '.bat'
    raise 'Unsupported platform: %s' % platform.system()


def get_nanopb_root():
    '''
    .. versionchanged:: 0.8
        Use :func:`conda_helpers.conda_prefix` function.
    '''
    if platform.system() in ('Linux', 'Darwin'):
        return ch.conda_prefix().joinpath('include', 'Arduino', 'nanopb')
    elif platform.system() == 'Windows':
        return ch.conda_prefix().joinpath('Library', 'include', 'Arduino',
                                          'nanopb')
    raise 'Unsupported platform: %s' % platform.system()


def get_sources():
    return get_nanopb_root().files('*.c*')


def get_includes():
    return [get_base_path().joinpath('include')]


def compile_nanopb(proto_path, options_file=None):
    '''
    Compile specified Protocol Buffer file to [`Nanopb`][1] "plain-`C`" code.

    [1]: https://code.google.com/p/nanopb
    '''
    proto_path = path(proto_path)
    tempdir = path(tempfile.mkdtemp(prefix='nanopb'))
    cwd = os.getcwd()
    try:
        os.chdir(tempdir)
        protoc = 'protoc' + get_exe_postfix()
        check_call([protoc, '-I%s' % proto_path.parent, proto_path,
                    '-o%s' % (tempdir.joinpath(proto_path.namebase + '.pb'))])
        nanopb_gen_cmd = [sys.executable, '-m', 'nanopb_generator',
                          tempdir.joinpath(proto_path.namebase + '.pb')]
        if options_file is not None:
            nanopb_gen_cmd += ['-f%s' % options_file]
        check_call(nanopb_gen_cmd)
        header = tempdir.files('*.h')[0].bytes()
        source = tempdir.files('*.c')[0].bytes()
        source = source.replace(proto_path.namebase + '.pb.h',
                                '{{ header_path }}')
    finally:
        os.chdir(cwd)
        tempdir.rmtree()
    return {'header': header, 'source': source}


def compile_pb(proto_path):
    '''
    Compile specified Protocol Buffer file to Google [Protocol Buffers][2]
    `C++` and Python code.

    [2]: https://code.google.com/p/protobuf
    '''
    proto_path = path(proto_path)
    tempdir = path(tempfile.mkdtemp(prefix='nanopb'))
    result = {}
    try:
        protoc = 'protoc' + get_exe_postfix()
        check_call([protoc, '-I%s' % proto_path.parent, proto_path,
                    '--python_out=%s' % tempdir, '--cpp_out=%s' % tempdir])
        result['python'] = tempdir.files('*.py')[0].bytes()
        result['cpp'] = {'header': tempdir.files('*.h*')[0].bytes(),
                         'source': tempdir.files('*.c*')[0].bytes()}
    finally:
        tempdir.rmtree()
    return result
