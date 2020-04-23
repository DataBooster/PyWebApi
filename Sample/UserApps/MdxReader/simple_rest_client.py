# -*- coding: utf-8 -*-
"""
    simple_rest_client.py
    This module is a simplified wrapper of Requests, specifically for JSON-request and JSON-response, 
    and by default, Windows single sign-on authentication is used for convenience in enterprise environment.

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT
"""
from requests import request
from requests_negotiate_sspi import HttpNegotiateAuth
from jsonpickle import dumps, loads


def request_json(url:str, payload=None, method:str='POST', auth=(None,None), **kwargs):

    body = dumps(payload, unpicklable=False) if payload is not None else None
    header = {"Content-Type": "application/json"} if body else None

    if auth == (None, None):
        auth = HttpNegotiateAuth()

    r = request(method, url, data=body, headers=header, auth=auth, **kwargs)
    r.raise_for_status()

    try:
        return r.json()
    except:
        return loads(r.text)
