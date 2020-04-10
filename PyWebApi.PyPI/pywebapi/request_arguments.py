# -*- coding: utf-8 -*-
"""
    request_arguments.py
    This module implements the merging of all arguments for function calls received from HTTP request.

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT (see LICENSE for details)
"""

from typing import Union, Dict, List
from bottle import Request, FormsDict

from . import util


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
