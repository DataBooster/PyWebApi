# -*- coding: utf-8 -*-
"""
    PyWebApi is a micro-framework for Python RESTfulization. It turns Python(3+) module/script into Web API (RESTful Service) out of the box.
    With PyWebApi, any http client can invoke module level function in a managed way.
    Input arguments of your function can be supplied in request body by JSON (recommended) or in URL query-string,
    If the client further wraps a batch of arguments sets into an array as the request JSON,
    the server will sequentially call the function by each argument set in the array,
    and wrap all the result objects in a more outer array before return to the client.

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT
"""

import bottle

from .func import execute, ModuleImporter, RequestArguments
from .fmtr import MediaTypeFormatter, MediaTypeFormatterManager

__version__ = "0.1a0.dev10"
