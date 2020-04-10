# -*- coding: utf-8 -*-
"""
    module_importer.py
    This module implements dynamic module loading and flexible function arguments binding.

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT (see LICENSE for details)
"""

import os
import importlib
import inspect
from collections import Iterable, OrderedDict
from typing import Union, Dict, List

from . import util


def bind_arguments(sig:inspect.Signature, args:dict) -> inspect.BoundArguments:
    """ According to the signature of the function, create a mapping from the passed argument dictionary to the function parameters.
        This implementation is a variant of Signature.bind () in inspect module.

        :param sig:  The signature of the function.
        :param args:  A argument dictionary to be passed to the function.
            - Named arguments are bound to keyword parameters defined by the function - Case Sensitive Matching;
            - All values listed ​​in the empty key (or blank key) are sequentially bound to positional parameters;
            - Any extra arguments will be ignored without error.
        :return:  A BoundArguments object.
        :raise TypeError:  if any required parameter can not be found from the passed arguments
    """
    in_pos_args = []
    in_kw_args = {}
    out_args = OrderedDict()

    if args:
        for name, value in args.items():
            if name and name.strip():
                in_kw_args[name] = value
            else:
                util.extend_or_append(in_pos_args, value)

    for param in sig.parameters.values():
        kw_value = in_kw_args.pop(param.name, param.default)

        if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD):
            out_args[param.name] = in_pos_args.pop(0) if len(in_pos_args) > 0 else kw_value
        elif param.kind == inspect.Parameter.VAR_POSITIONAL:
            if kw_value is not inspect.Parameter.empty:
                util.extend_or_append(in_pos_args, kw_value)
            out_args[param.name] = tuple(in_pos_args)
            #in_pos_args.clear()
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            if kw_value is not inspect.Parameter.empty:
                if isinstance(kw_value, Iterable) and not isinstance(kw_value, str):
                    try:
                        vk = dict(kw_value)
                    except:
                        in_kw_arg.setdefault(param.name, kw_value)
                    else:
                        for k, v in vk.items():
                            if k:
                                before = out_args.get(k)
                                if before is inspect.Parameter.empty:
                                    out_args[k] = v
                                else:
                                    in_kw_arg.setdefault(k, v)
            out_args[param.name] = in_kw_args
            #in_kw_args.clear()
        else:
            out_args[param.name] = kw_value

    missing_args = [repr(k) for k, v in out_args.items() if v is inspect.Parameter.empty]
    missing_count = len(missing_args)
    if missing_count > 0:
        missing_list = ', '.join(missing_args)
        plural = 's' if missing_count > 1 else ''
        error_msg = f"missing {missing_count} required argument{plural}: {missing_list}"
        raise TypeError(error_msg) from None

    return inspect.BoundArguments(sig, out_args)


def __one_call(func, sig:inspect.Signature, args:dict):
    bound_arguments = bind_arguments(sig, args)
    return func(*bound_arguments.args, **bound_arguments.kwargs)


def _bulk_call(func, sig:inspect.Signature, args_list:list):
    i = 0
    for args in args_list:
        if isinstance(args, dict):
            yield __one_call(func, sig, args)
        elif args is None:
            yield None
        else:
            raise TypeError(f"each item in the 'args' list must be a dictionary - receiving args[{i}]={repr(args)} is not acceptable") from None
        i += 1


class ModuleImporter(object):
    """ This class manages the context of a user module to be dynamically imported.

        :param directory:  The directory of being imported user module - the relative path from the configured root directory of all user modules.
        :param module_name:  The module name to be imported.
    """

    def __init__(self, directory:str, module_name:str):
        self.__orig_cwd = os.getcwd()
        self.__scope_cwd = util.full_path(directory)
        self.__cwd_chg = False
        self.__sys_path_chg = False

        if not util.same_path(self.__scope_cwd, self.__orig_cwd):
            try:
                os.chdir(self.__scope_cwd)
            except FileNotFoundError as err:
                raise NotADirectoryError(str(err).replace(' the file ', ' the directory '))
            else:
                self.__cwd_chg = True

        if util.insert_sys_path(self.__scope_cwd):
            self.__sys_path_chg = True

        self.module = importlib.import_module(module_name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.__cwd_chg and util.same_path(os.getcwd(), self.__scope_cwd):
            os.chdir(self.__orig_cwd)

        if self.__sys_path_chg:
            util.remove_sys_path(self.__scope_cwd)


    def invoke(self, func_name:str, args:Union[Dict, List[Dict]]={}):
        """ Invoke a module level function in current context.

            :param func_name:  The module level function name.
            :param args:  A argument dictionary or a list of argument dictionary to be passed to the invoking function.
                * If the args is a dictionary:
                    - Named arguments are bound to keyword parameters defined by the function - Case Sensitive Matching;
                    - All values listed ​​in the empty key (or blank key) are sequentially bound to positional parameters;
                    - Any extra arguments will be ignored without error.
                * If the args is a list of dictionaries:
                    - This function will be called in loop by using each argument dictionary in the list.
            :return:  The result object of the module level function returned
                * If the args is a dictionary, the result of the function execution is returned;
                * If the args is a list of dictionaries, all results of multiple executions of the function will be wrapped into a list and returned together.
                    If any exception is thrown during the call loop, subsequent calls will be stopped
        """
        try:
            module_level_function = getattr(self.module, func_name)
            if not callable(module_level_function) or inspect.isclass(module_level_function):
                raise TypeError(f'{repr(func_name)} is not a function')
        except AttributeError as err:
            raise NotImplementedError(str(err).replace(' no attribute ', ' no function '))
        else:
            sig = inspect.signature(module_level_function)

            if isinstance(args, dict):
                return __one_call(module_level_function, sig, args)
            elif isinstance(args, list):
                if args:
                    return list(_bulk_call(module_level_function, sig, args))
                else:
                    return []
            else:
                raise TypeError("'args' parameter only accepts a dictionary or a list of dictionaries")
