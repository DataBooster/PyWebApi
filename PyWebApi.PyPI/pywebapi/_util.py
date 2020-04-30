# -*- coding: utf-8 -*-
"""
    _util.py
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
    else:
        path = os.getcwd()

    return os.path.normpath(path)


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


def get_sys_path_as_set(sys_path:list=None) -> set:
    if not sys_path:
        sys_path = sys.path

    path_set = set()
    for p in sys_path:
        try:
            if p and p != '.' and os.path.exists(p):
                path_set.add(full_path(p))
        except TypeError:
            continue

    return path_set


def insert_sys_path(path:str, known_paths:set) -> bool:
    """ Insert the new path into sys.path right after '' or '.', otherwise in the first position. """
    if not path or path == '.':
        return False

    i = cnt = len(sys.path)

    if known_paths:
        if path in known_paths:
            return False

        i = 0
        while i < cnt:
            p = sys.path[i]
            if not p or p == '.':
                break
            i += 1
    else:
        r = cnt - 1
        while r >= 0:
            p = sys.path[r]
            if p and p != '.':
                if path == full_path(p):
                    return False
            else:
                i = r
            r -= 1

    if i < cnt:
        i += 1
    else:
        i = 0

    sys.path.insert(i, path)
    return True


def remove_sys_path_set(path_set:set) -> set:
    removed = set()

    if path_set:
        i = len(sys.path) - 1
        while i > 0:
            p = sys.path[i]
            if p and p != '.' and full_path(p) in path_set:
                removed.add(sys.path.pop(i))
            i -= 1

    return removed


def extend_or_append(iterable:list, item):
    if isinstance(item, Iterable) and not isinstance(item, str):
        iterable.extend(item)
    else:
        iterable.append(item)
