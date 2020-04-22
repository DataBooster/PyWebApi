# -*- coding: utf-8 -*-
"""
    json_fmtr.py
    This module implements a MediaTypeFormatter with JSON response.

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT
"""

from jsonpickle import dumps
from pywebapi import MediaTypeFormatter


class JsonFormatter(MediaTypeFormatter):
    """description of class"""

    @property
    def supported_media_types(self):
       return ['application/json', 'text/json']


    def format(self, obj, media_type:str, **kwargs):
        kwargs['unpicklable'] = kwargs.get('unpicklable', False)
        return dumps(obj, **kwargs)
