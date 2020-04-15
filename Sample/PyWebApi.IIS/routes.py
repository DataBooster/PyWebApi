# -*- coding: utf-8 -*-
"""
    Routes for the sample PyWebApi Service.
"""

import os
from bottle import route, request, response, abort
from pywebapi import RequestArguments, execute, cors


_user_script_root = os.getenv("USER_SCRIPT_ROOT")
if not os.path.isabs(_user_script_root):
    _user_script_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), _user_script_root)
_user_script_root = os.path.normpath(_user_script_root)

_server_debug = os.getenv("SERVER_DEBUG")


def _get_user() -> str:
    return request.auth[0] if request.auth else None


def authorize(func):
    def wrapped(*args, **kwargs):
        if not _get_user() and _server_debug != 'VisualStudio':
            abort(401, "The requested resource requires user authentication.")
        return func(*args, **kwargs)
    return wrapped


def enable_cors(func):
    def wrapped(*args, **kwargs):
        if cors.enable_cors(request, response):
            return None
        return func(*args, **kwargs)
    return wrapped



@route(path='/whoami', method=['GET', 'POST', 'OPTIONS'])
@authorize
@enable_cors
def who_am_i():
    return _get_user()


def check_permission(app_id:str, user_id:str, module_func:str) -> bool:
    #TODO: add your implementation of permission checks
    return True


@route(path='/pys/<app_id>/<func_path:path>', method=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@authorize
@enable_cors
def execute_module_level_function(app_id:str, func_path:str):
    user_name = _get_user()

    if check_permission(app_id, user_name, func_path):
        ra = RequestArguments(request)
        ra.override_value('actual_username', user_name)

        return execute(_user_script_root, func_path, ra.arguments)
    else:
        abort(401, f"Current user ({repr(user_name)}) does not have permission to execute the requested {repr(funcpath)}.")
