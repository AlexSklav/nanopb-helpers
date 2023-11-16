# coding: utf-8
import argparse

import platformio_helpers as pioh

from path_helpers import path


def transfer(**kwargs) -> None:
    # Copy Arduino library to Conda include directory
    source_dir = kwargs.get('source_dir')
    lib_name = kwargs.get('lib_name')
    # source_dir = path(source_dir).joinpath(module_name, 'Arduino', 'library', lib_name) # Use this for Arduino libs
    source_dir = path(source_dir).joinpath('lib', lib_name)
    install_dir = pioh.conda_arduino_include_path().joinpath(lib_name)
    for file in source_dir.walkfiles():
        dest = install_dir.joinpath(file.relpathto(source_dir))
        file.copy2(dest)
        print(f"Copied '{file.name}' to '{dest}'")


def cli_parser():
    parser = argparse.ArgumentParser(description='Transfer header files to include directory.')
    parser.add_argument('source_dir')
    parser.add_argument('prefix')
    parser.add_argument('package_name')
    parser.add_argument('module_name')
    parser.add_argument('lib_name')

    args = parser.parse_args()
    execute(**vars(args))


def execute(**kwargs):

    top = '>' * 180
    print(top)

    transfer(**kwargs)

    print('<' * len(top))


if __name__ == '__main__':
    cli_parser()
