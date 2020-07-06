# -*- coding: utf-8 -*-
"""mdx_task.py

    The main function - run_query(...) Runs a MDX query and returns the result, 
    or forward the result to DbWebApi (for bulk insert/update) and then send a notification to somewhere.

    This module was originally shipped as an example code from https://github.com/DataBooster/PyWebApi, licensed under the MIT license.
    Anyone who obtains a copy of this code is welcome to modify it for any purpose, and holds all rights to the modified part only.
    The above license notice and permission notice shall be included in all copies or substantial portions of the Software.
"""

from time import sleep
from collections.abc import Mapping, MutableMapping
from adomd_client import AdomdClient
from simple_rest_call import request_json


def _notify(result, error=None, notify_url:str=None, notify_args:MutableMapping=None) -> bool:
    result_param_convention = '[=]'
    error_param_convention = '[!]'

    if notify_url:
        if isinstance(notify_args, MutableMapping):
            result_param_name = notify_args.pop(result_param_convention, None)
            error_param_name = notify_args.pop(error_param_convention, None)
        else:
            result_param_name = error_param_name = None

        if result_param_name:
            notify_args[result_param_name] = result

        if error_param_name:
            notify_args[error_param_name] = error

        request_json(notify_url, notify_args)

        return True
    else:
        return False


def run_query(connection_string:str, command_text:str,
              result_model:str='DictOfList', column_mapping:Mapping={},
              mdx_retries:int=1, delay_retry:float=10.0,
              pass_result_to_url:str=None, more_args:Mapping=None,
              notify_url:str=None, notify_args:MutableMapping=None):

    result = {}
    retries = 0
    max_retries = int(mdx_retries) if isinstance(mdx_retries, (int, str)) else 0
    delay = float(delay_retry) if isinstance(delay_retry, (int, float, str)) else 10.0
    if delay < 1.0:
        delay = 1.0

    while True:
        try:
            with AdomdClient(connection_string) as client:
                result = client.execute(command_text, result_model, column_mapping)
            break

        except Exception as err:
            if retries < max_retries:
                retries += 1
                sleep(delay)
            else:
                if _notify(result, err, notify_url, notify_args):   # Send a notification with result data and/or error information
                    return result
                else:
                    raise

    try:
        if pass_result_to_url:
            if more_args:
                if isinstance(result, MutableMapping):
                    result.update(more_args)
                elif isinstance(result, list):
                    for row in result:
                        if isinstance(row, MutableMapping):
                            row.update(more_args)

            result = request_json(pass_result_to_url, result)   # Chain above result to DbWebApi for storage or further processing

    except Exception as err:
        if not _notify(result, err, notify_url, notify_args):   # Send a notification with result data and/or error information
            raise

    else:
        _notify(result, None, notify_url, notify_args)          # Send a notification with result data

    return result



__version__ = "0.1"
