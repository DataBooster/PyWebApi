# -*- coding: utf-8 -*-
"""
    util.py
    This module implements some utility functions commonly used in this library.

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT (See LICENSE file in the repository root for details)
"""

import os
import sys
from collections import Iterable, namedtuple


RequestModuleFunction = namedtuple('RequestModuleFunction', ['directory', 'module', 'function'])

def extract_path_info(path_info:str) -> RequestModuleFunction:
    directory, _, module_function = path_info.strip('/').rpartition('/')
    module, _, function = module_function.rstrip('.').rpartition('.')
    if not module and directory:
        directory, _, module = directory.rpartition('/')

    if not function:
        raise NameError(f'the function name cannot be found from the request URL path {repr(path_info)}')
    if not module:
        raise ModuleNotFoundError(f'the module name cannot be found from the request URL path {repr(path_info)}')
    if not directory:
        raise NotADirectoryError(f'the directory of module cannot be found from the request URL path {repr(path_info)}')

    return RequestModuleFunction(directory=directory, module=module, function=function)


def full_path(path:str) -> str:
    if path:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        return os.path.normpath(path)
    else:
        return os.getcwd()


def same_path(path1:str, path2:str) -> bool:
    if not path1 and not path2:
        return True
    elif not path1 or not path2:
        return False
    else:
        try:
            return os.path.samefile(path1, path2)
        except FileNotFoundError:
            return False


def __can_add_into_sys_path(path:str) -> bool:
    if path and os.path.exists(path):
        return not any(same_path(p, path) for p in sys.path)
    else:
        return False


def append_sys_path(path:str) -> bool:
    if __can_add_into_sys_path(path):
        sys.path.append(path)
        return True
    else:
        return False


def insert_sys_path(path:str, index:int=1) -> bool:
    if __can_add_into_sys_path(path) and index > 0:
        sys.path.insert(index, path)
        return True
    else:
        return False


def remove_sys_path(path:str) -> bool:
    if path:
        i = len(sys.path) - 1
        while i > 0:
            if same_path(sys.path[i], path):
                sys.path.pop(i)
                return True
            i -= 1

    return False



def extend_or_append(iterable:list, item):
    if isinstance(item, Iterable) and not isinstance(item, str):
        iterable.extend(item)
    else:
        iterable.append(item)
