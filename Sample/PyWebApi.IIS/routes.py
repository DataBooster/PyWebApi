"""
    Routes for the sample PyWebApi Service.
"""

from bottle import route, request, abort
from pywebapi import execute, cors


def authorize(func):

    def wrapped(*args, **kwargs):
        if not request.auth or not request.auth[0]:
            abort(401, "The requested resource requires user authentication.")
        return func(*args, **kwargs)

    return wrapped


@route('/whoami')
@authorize
def who_am_i():
    return request.auth[0]


def check_permission(app:str, user:str, module_func:str)->bool:
    #TODO: add your implementation of permission checks
    return True


@route('/pyscripts/<app:str>/<path:path>')
@authorize
def execute_module_level_function(app:str, path:str):
    user_name = request.auth[0]

    if check_permission(app, request.auth[0], path):
        return execute('d:\\user-script-root\\', request, {'actual_username': user_name})
    else:
        abort(401, f"Current user ({repr(user_name)}) does not have permission to execute the requested {repr(path)}.")
