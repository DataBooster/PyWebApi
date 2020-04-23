# -*- coding: utf-8 -*-
from jsonpickle import decode, encode


def dumps(obj, **kwargs):
    kwargs['unpicklable'] = kwargs.get('unpicklable', False)
    return encode(obj, **kwargs)


def loads(s, **kwargs):
    return decode(s, **kwargs)
