# -*- coding: utf-8 -*-
"""
    simple_rest_call

    This module wraps Requests(https://requests.readthedocs.io/) into a simple call, 
    specifically for JSON-request and JSON-response with datetime support. By default, 
    Windows single sign-on authentication is used for convenience in enterprise environment.

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT
"""
from requests import request
from requests.structures import CaseInsensitiveDict
from requests_negotiate_sspi import HttpNegotiateAuth
from jsonpickle import encode as json_encode
from dateutil import parser as dt_parser


def _json_datetime_decode_hook(pairs):
    obj_dict = {}

    for k, v in pairs:
        if isinstance(v, str) and 10 <= len(v) <= 50:
            try:
                obj_dict[k] = dt_parser.parse(v)
            except: #ValueError:
                obj_dict[k] = v
        else:
            obj_dict[k] = v

    return obj_dict


def _to_json(data, header:CaseInsensitiveDict=None, quotes:bool=False):
    if data is None:
        return data

    if isinstance(data, (str, bytes)) and not quotes:
        return data

    body = json_encode(data, unpicklable=False)
    content_type = 'application/json'

    if not isinstance(body, bytes):
        body = body.encode('utf-8')
        content_type += '; charset=utf-8'

    if isinstance(header, CaseInsensitiveDict):
        header.setdefault('Content-Type', content_type)

    return body


def request_json(url:str, data=None, method:str='POST', auth=(None,None), **kwargs):
    """ This module is a simplified wrapper of Requests, specifically for JSON-request and JSON-response with datetime support.
        And by default, Windows single sign-on authentication is used for convenience in enterprise environment.

        :param url:  The URL for the RESTful call.
        :param data:  The payload to be passed in the request body. Any incoming Python object will be encoded as JSON content
                      except it is already a string or bytes. "Content-Type: application/json; charset=utf-8" will be added into 
                      the request header if the object is converted to JSON inside this function.
        :param method:  (Default: ``POST``) Method for the request: ``GET``, ``POST``, ``PUT``, ``PATCH``, ``DELETE``, ``OPTIONS``, or ``HEAD``.
        :param auth:  (The user's default credentials are used for Windows single sign-on by default) Auth tuple to enable Basic/Digest/Custom HTTP Auth.
        :param **kwargs:  (optional) Please refer to https://requests.readthedocs.io for other optional arguments.
        :return:  A JSON decoded object if the response content type is a valid JSON, otherwise the text content will be tried to return.
    """
    explicitly_to_json = False

    if data is None:
        data = kwargs.get('json')
        if data is not None:
            explicitly_to_json = True

    header = CaseInsensitiveDict(kwargs.get('headers', {}))
    body = _to_json(data, header, explicitly_to_json)

    kwargs['headers'] = header
    kwargs['data'] = body

    if auth == (None, None):
        auth = HttpNegotiateAuth()
    if auth is not None:
        kwargs['auth'] = auth

    r = request(method, url, **kwargs)
    r.raise_for_status()

    try:
        return r.json(object_pairs_hook=_json_datetime_decode_hook)
    except ValueError:
        return r.text



__version__ = "0.1a1.dev2"

