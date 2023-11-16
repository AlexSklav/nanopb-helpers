# coding: utf-8
"""
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
"""
import os
import platform
import sys
import tempfile
from typing import List, Optional, Dict

import conda_helpers as ch

from path_helpers import path
from subprocess import check_call

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions


def get_base_path() -> path:
    return path(__file__).parent.abspath()


def package_path() -> path:
    return path(__file__).parent


def get_lib_directory() -> path:
    """
    Return directory containing the Arduino library headers.
    """
    return package_path().joinpath('Arduino', 'library')


def get_exe_postfix() -> str:
    """
    Return the file extension for executable files.
    """
    if platform.system() in ('Linux', 'Darwin'):
        return ''
    elif platform.system() == 'Windows':
        return '.exe'
    raise f'Unsupported platform: {platform.system()}'


def get_script_postfix() -> str:
    """
    Return the file extension for executable files.
    """
    if platform.system() in ('Linux', 'Darwin'):
        return ''
    elif platform.system() == 'Windows':
        return '.bat'
    raise f'Unsupported platform: {platform.system()}'


def get_nanopb_root() -> path:
    """
    .. versionchanged:: 0.8
        Use :func:`conda_helpers.conda_prefix` function.
    """
    if platform.system() in ('Linux', 'Darwin'):
        return ch.conda_prefix().joinpath('include', 'Arduino', 'nanopb')
    elif platform.system() == 'Windows':
        return ch.conda_prefix().joinpath('Library', 'include', 'Arduino', 'nanopb')
    raise f'Unsupported platform: {platform.system()}'


def get_sources() -> List[path]:
    return get_nanopb_root().files('*.c*')


def get_includes() -> List[path]:
    return [get_base_path().joinpath('include')]


def compile_nanopb(proto_path: path, options_file: Optional[str] = None) -> Dict:
    """
    Compile specified Protocol Buffer file to `Nanopb
    <https://code.google.com/p/nanopb>`_ "plain-``C``" code.


    .. versionchanged:: 0.9.2
        Fix Python 3 unicode support.  Use :meth:`path_helpers.path.text`
        method instead of :meth:`path_helpers.path.bytes` method.
    """
    proto_path = path(proto_path)
    tempdir = path(tempfile.mkdtemp(prefix='nanopb'))
    cwd = os.getcwd()
    try:
        os.chdir(tempdir)
        protoc = f'protoc{get_exe_postfix()}'
        proto_pb_path = str(tempdir.joinpath(proto_path.namebase + ".pb"))
        check_call([protoc, f'-I{str(proto_path.parent)}', str(proto_path), f'-o{proto_pb_path}'])
        nanopb_gen_cmd = [sys.executable, '-m', 'nanopb_generator', proto_pb_path]
        if options_file is not None:
            nanopb_gen_cmd += [f'-f{options_file}']
        check_call(nanopb_gen_cmd)
        header = tempdir.files('*.h')[0].text()
        source = tempdir.files('*.c')[0].text()
        source = source.replace(f'{proto_path.namebase}.pb.h', '{{ header_path }}')
    finally:
        os.chdir(cwd)
        tempdir.rmtree()
    return {'header': header, 'source': source}


def compile_pb(proto_path: path) -> Dict:
    """
    Compile specified Protocol Buffer file to Google `Protocol Buffers
    <https://code.google.com/p/protobuf>`_ `C++` and Python code.


    .. versionchanged:: 0.9.2
        Fix Python 3 unicode support.  Use :meth:`path_helpers.path.text`
        method instead of :meth:`path_helpers.path.bytes` method.
    """
    proto_path = path(proto_path)
    tempdir = path(tempfile.mkdtemp(prefix='nanopb'))
    result = {}
    try:
        protoc = f'protoc{get_exe_postfix()}'
        check_call([protoc, f'-I{proto_path.parent}', proto_path,
                    f'--python_out={tempdir}', f'--cpp_out={tempdir}'])
        result['python'] = tempdir.files('*.py')[0].text()
        result['cpp'] = {'header': tempdir.files('*.h*')[0].text(),
                         'source': tempdir.files('*.c*')[0].text()}
    finally:
        tempdir.rmtree()
    return result
