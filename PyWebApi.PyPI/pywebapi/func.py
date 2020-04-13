# -*- coding: utf-8 -*-
"""
    func.py
    This module implements the main APIs.

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT (see LICENSE for details)
"""
import os
import inspect
import importlib
from collections import Iterable, OrderedDict
from typing import Union, Dict, List

from bottle import Request, FormsDict
from . import util


####################################################################################################
# This region implements flexible function arguments binding.
#region

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

#endregion
####################################################################################################


####################################################################################################
# This class implements dynamic module loading.
#region

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

#endregion
####################################################################################################


####################################################################################################
# This region implements the main entrance: execute(...).
#region

def execute(root:str, routed_path:str, args_dict:Union[Dict, List[Dict]]={}):
    public_root = util.full_path(root)
    if not os.path.isdir(public_root):
        raise NotADirectoryError(f'the root {repr(root)} of user modules is not configured as a valid file system directory')

    module_func = util.extract_path_info(request.path)
    work_dir = os.path.normpath(os.path.join(public_root, module_func.directory))
    if not os.path.isdir(work_dir):
        raise NotADirectoryError(f'the directory {repr(module_func.directory)} specified in the request URL path cannot be found in the file system')

    with ModuleImporter(work_dir, module_func.module) as starter:
        return_object = starter.invoke(module_func.function, args_dict)

    return return_object

#endregion
####################################################################################################


####################################################################################################
# This region implements the merging of all arguments for function calls received from HTTP request.
#region

def _fill_dict_multi_value(arg_dict:dict, name:str, values):
    key = name.strip() if name else ''
    value = values[0] if isinstance(values, list) and len(values) == 1 else values

    if key:
        try:
            existing = arg_dict[key]
        except KeyError:
            arg_dict[key] = value
        else:
            if isinstance(existing, list):
                util.extend_or_append(existing, value)
            elif value and not existing:
                arg_dict[key] = value
            elif existing is None and value is not None:
                arg_dict[key] = value
            #else ignore
    else:
        pos_args = arg_dict.setdefault('', [])
        util.extend_or_append(pos_args, value)


def _fill_dict(arg_dict:dict, forms_dict:FormsDict):
    for name, values in forms_dict.items():
        _fill_dict_multi_value(arg_dict, name, values)


def _init_dict_list(json_obj) -> List[Dict]:
    if json_obj is None:
        return [{}]
    if isinstance(json_obj, dict):
        return [dict(json_obj)]
    elif isinstance(json_obj, list):
        if all(isinstance(item, dict) for item in json_obj):
            return [dict(item) for item in json_obj]
        else:
            return [{'': list(json_obj)}]
    else:
        return [{'': json_obj}]


class RequestArguments(object):
    """ This class is used to gather all arguments information from the request body (if JSON) and the URL query string,
        then merge them into a dictionary or a list of dictionary.

        :param request:  The request object passed from bottle.

        .. note::
            Arguments from the request body (if it is JSON) are dominant, and arguments from the query string are supplementary.
            Only arguments in the body (if it is JSON) can determine whether the request is a single function call or a loop of calls on the same function.
            - If the body JSON is a dictionary, this request will be treated as a single call to the function.
              Arguments are primarily picked from the JSON dictionary (those values listed ​​in empty key or blank key are treated as positional arguments, 
              and values of empty key from query string will be extended together), then named arguments can be picked from query string only if they 
              do not exist in the JSON body.
            - If the body JSON is a list of dictionaries, this request will be treated as calling the same function in a loop for each argument dictionary.
              Other arguments in the query string are added to current argument dictionary for each function call (same way as above)。
    """
    def __init__(self, request:Request):
        self.request = request
        self.arg_dict_list = _init_dict_list(request.json)

        for arg_dict in self.arg_dict_list:
            _fill_dict(arg_dict, request.params)

    @property
    def arguments(self) -> Union[Dict, List[Dict]]:
        return self.arg_dict_list if len(self.arg_dict_list) > 1 else self.arg_dict_list[0]

    def override(override_dict:dict) -> Union[Dict, List[Dict]]:
        if override_dict and isinstance(override_dict, dict):
            for name, value in override_dict:
                key = name.strip() if name else ''
                if key:
                    for arg_dict in self.arg_dict_list:
                        arg_dict[key] = value

        return self.arguments

    def override_value(key:str, value) -> Union[Dict, List[Dict]]:
        for arg_dict in self.arg_dict_list:
            arg_dict[key] = value

        return self.arguments

#endregion
####################################################################################################
