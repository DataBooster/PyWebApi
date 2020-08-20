# -*- coding: utf-8 -*-
"""
PyWebApi is a micro-framework for Python RESTfulization. It turns Python(3+) modules/scripts into Web API (RESTful Service) out of the box.

Just copy any ordinary Python module (and its dependent components) to an organized 
container (directory) in a PyWebApi Server and it will become a RESTfull service immediately. 
There is no need to write any code or configuration to become a RESTfull service.

Then, any authorized HTTP client can invoke module level functions. 
Input arguments of your function can be passed in request body by JSON (recommended) or in URL query-string.
If the client further wraps a batch of arguments sets into an array as the request JSON, 
the server will sequentially call the function by each argument set in the array, 
and wrap all the result objects in a more outer array before return to the client.

This library package is for making PyWebApi Server. See the following homepage for details.

----

| Homepage and documentation: https://github.com/DataBooster/PyWebApi
| Copyright (c) 2020 Abel Cheng
| License: MIT
"""

import bottle

from .func import execute, ModuleImporter, RequestArguments
from .fmtr import MediaTypeFormatter, MediaTypeFormatterManager


__version__ = "0.1a6"
