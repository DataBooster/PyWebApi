# -*- coding: utf-8 -*-
from jsonpickle import encode
from json import loads as decode
from dateutil import parser


def dumps(obj, **kwargs):
    kwargs['unpicklable'] = kwargs.get('unpicklable', False)
    return encode(obj, **kwargs)


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



def loads(s, **kwargs):
    kwargs['object_pairs_hook'] = kwargs.get('object_pairs_hook', _json_datetime_decode_hook)
    return decode(s, **kwargs)
