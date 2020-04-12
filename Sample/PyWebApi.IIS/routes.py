"""
    Routes for the sample PyWebApi Service.
"""

import os
from bottle import route, request, abort
from pywebapi import execute, cors


_user_script_root = os.getenv("USER_SCRIPT_ROOT")
if not os.path.isabs(_user_script_root):
    _user_script_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), _user_script_root)
_user_script_root = os.path.normpath(_user_script_root)


def _get_user() -> str:
    return request.auth[0] if request.auth else None


def authorize(func):

    def wrapped(*args, **kwargs):
        if not _get_user():
            abort(401, "The requested resource requires user authentication.")
        return func(*args, **kwargs)

    return wrapped


@route(path='/whoami', method=['GET', 'POST'])
@authorize
def who_am_i():
    return _get_user()


def check_permission(app:str, user:str, module_func:str) -> bool:
    #TODO: add your implementation of permission checks
    return True


@route(path='/pyscripts/<app>/<funcpath:path>', method=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
@authorize
def execute_module_level_function(app:str, funcpath:str):
    user_name = _get_user()

    if check_permission(app, user_name, funcpath):
        return execute(_user_script_root, request, {'actual_username': user_name})
    else:
        abort(401, f"Current user ({repr(user_name)}) does not have permission to execute the requested {repr(funcpath)}.")
