# -*- coding: utf-8 -*-
"""cors.py

This module implements a simplified method of CORS (Cross-Origin Resource Sharing Standard).

| Homepage and documentation: https://github.com/DataBooster/PyWebApi
| Copyright (c) 2020 Abel Cheng
| License: MIT (See LICENSE file in the repository root for details)
"""

from bottle import Request, Response


def enable_cors(request:Request, response:Response, allow_credentials:bool=True, max_age:int=86400) -> bool:
    """
This function detects whether the request is a cross-origin request or 
a preflight request based on certain characteristic headers, 
and then adds the corresponding response headers as needed.

    :param request: The bottle.request object (current request).
    :param response: The bottle.response object.
    :param allow_credentials: A bool flag indicates whether to send the response header "Access-Control-Allow-Credentials: true", if the request is a cross-origin request.
    :param max_age: The number of seconds that the results of the preflight request can be cached, if the request is a preflight request.
    :return: A Boolean value tells the caller whether the request is just a preflight request, so no further processing is required.
    """
    is_preflight = False

    origin = request.get_header('Origin')
    if not origin:
        return is_preflight

    host = request.get_header('Host')
    if not host:
        host = request.urlparts.netloc

    if origin.lower().endswith('//' + host.lower()):
        return is_preflight

    response.set_header('Access-Control-Allow-Origin', origin)

    if allow_credentials:
        response.set_header('Access-Control-Allow-Credentials', 'true')

    if request.method == 'OPTIONS':
        cors_method = request.get_header('Access-Control-Request-Method')
        if cors_method:
            response.set_header('Access-Control-Allow-Methods', cors_method)
            if max_age:
                response.set_header('Access-Control-Max-Age', str(max_age))
            is_preflight = True

        cors_headers = request.get_header('Access-Control-Request-Headers')
        if cors_headers:
            response.set_header('Access-Control-Allow-Headers', cors_headers)

    return is_preflight
