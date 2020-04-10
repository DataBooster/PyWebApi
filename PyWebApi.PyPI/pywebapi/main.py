# -*- coding: utf-8 -*-
"""
    main.py
    This module implements the main entrance: execute(...).

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT (see LICENSE for details)
"""
from os import path
from bottle import Request

from .module_importer import ModuleImporter
from .request_arguments import RequestArguments
from . import util


def execute(root:str, request:Request, override_args:dict=None):
    public_root = util.full_path(root)
    if not path.isdir(public_root):
        raise NotADirectoryError(f'the root {repr(root)} of user modules is not configured as a valid file system directory')

    module_func = util.extract_path_info(request.path)
    work_dir = path.normpath(path.join(public_root, module_func.directory))
    if not path.isdir(work_dir):
        raise NotADirectoryError(f'the directory {repr(module_func.directory)} specified in the request URL path cannot be found in the file system')

    request_arguments = RequestArguments(request)
    request_arguments.override(override_args)

    with ModuleImporter(work_dir, module_func.module) as starter:
        return_object = starter.invoke(module_func.function, request_arguments.arguments)

    return return_object
