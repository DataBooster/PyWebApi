# -*- coding: utf-8 -*-
"""
    json_fmtr.py
    This module implements a MediaTypeFormatter with JSON response.

    This module was originally shipped as an example code from https://github.com/DataBooster/PyWebApi, licensed under the MIT license.
    Anyone who obtains a copy of this code is welcome to modify it for any purpose, and holds all rights to the modified part only.
    The above license notice and permission notice shall be included in all copies or substantial portions of the Software.
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
