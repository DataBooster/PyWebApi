# -*- coding: utf-8 -*-
"""
    mdx_task.py
    The main function - run_query(...) Runs a MDX query and returns the result, 
    or forward the result to DbWebApi (for bulk insert/update) and then send a notification to somewhere.

    This module was originally shipped as an example code from https://github.com/DataBooster/PyWebApi, licensed under the MIT license.
    Anyone who obtains a copy of this code is welcome to modify it for any purpose, and holds all rights to the modified part only.
    The above license notice and permission notice shall be included in all copies or substantial portions of the Software.
"""
from adomd_client import AdomdClient
from simple_rest_call import request_json


def run_query(connection_string:str, command_text:str, result_model:str='DictOfList', column_mapping:dict={},
              pass_result_to_url:str=None, more_args:dict=None, notify_url:str=None, notify_args:dict=None):

    result = {}

    try:
        with AdomdClient(connection_string) as client:
            result = client.execute(command_text, result_model, column_mapping)

        if pass_result_to_url:
            if isinstance(result, dict) and more_args:
                result.update(more_args)

            result = request_json(pass_result_to_url, result)

        if notify_url:
            request_json(notify_url, {'result': result})

        return result

    except Exception as e:
        if notify_url:
            if notify_args is None:
                notify_args = {}
            notify_args.update({'error': e, 'result': result})

            request_json(notify_url, notify_args)
        else:
            raise
