# -*- coding: utf-8 -*-
"""db_mdx_db.py

    This module (main function: ``start(...)``) implements a common end-to-end MDX ETL process：

    **db->mdx->db**

    #.  Call a stored procedure to obtain a group of MDX queries generated from the database; 
    #.  Concurrently execute this group of MDX queries and pass the query results to the corresponding stored procedures;
    #.  (optional) Once all concurrent tasks get completed, a summary level post-processing stored procedure is called.

    This module was originally shipped as an example code from https://github.com/DataBooster/PyWebApi, licensed under the MIT license.
    Anyone who obtains a copy of this code is welcome to modify it for any purpose, and holds all rights to the modified part only.
    The above license notice and permission notice shall be included in all copies or substantial portions of the Software.
"""

import json
from urllib.parse import urljoin
from collections.abc import Mapping, MutableMapping
from bottle import request
from requests.structures import CaseInsensitiveDict
from simple_rest_call import request_json


def _full_url(relative_url:str) -> str:
    return urljoin(request.url, relative_url)

_url_mdx_reader = _full_url("../mdxreader/mdx_task.run_query")
_url_svc_grp = _full_url("../services_grouping/rest_grouping.start")


def _notify(result, error=None, notify_url:str=None, notify_args:dict=None) -> bool:
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


def start(task_sp_url:str, sp_args:dict, mdx_conn_str:str, timeout:float=1800,
          mdx_column:str='MDX_QUERY', column_map_column:str='COLUMN_MAPPING', callback_sp_column:str='CALLBACK_SP', callback_args_column:str='CALLBACK_ARGS', db_type='oracle',
          post_sp_outparam:str='OUT_POST_SP', post_sp_args_outparam:str='OUT_POST_SP_ARGS',
          notify_url:str=None, notify_args:dict=None):

    def invoke_main_sp(sp_url:str, sp_args:dict, sp_timeout:float) -> dict:

        def check_dbwebapi(result:dict) -> bool:
            if not isinstance(result, Mapping):
                return False

            if 'ResultSets' in result and 'OutputParameters' in result and 'ReturnValue' in result:
                return True
            else:
                return False

        result = request_json(sp_url, sp_args, timeout=sp_timeout)

        if result and not check_dbwebapi(result):
            raise TypeError(f"{repr(sp_url)} is not a dbwebapi call")

        return result

    def get_tasks(sp_result:dict) -> dict:

        out_params = CaseInsensitiveDict(sp_result['OutputParameters'])
        post_sp = out_params.pop(post_sp_outparam, None)
        post_sp_args = json.loads(out_params.pop(post_sp_args_outparam, '{}'))
        if post_sp:
            post_url = urljoin(task_sp_url, '../' + post_sp)
            post_sp_args.update(out_params)
        else:
            post_url = None
            post_sp_args = None

        if db_type and isinstance(db_type, str) and db_type[:3].lower() == 'ora':
            result_model = 'DictOfList'
        else:
            result_model = 'SqlTvp'

        serial_tasks = []

        for rs in sp_result['ResultSets']:

            parallel_tasks = []

            for row in rs:
                task = CaseInsensitiveDict(row)
                mdx_query = task.get(mdx_column)
                if not mdx_query:
                    if parallel_tasks:
                        continue    # skip a row if mdx_column is missing from a subsequent row
                    else:
                        break       # skip the whole resultset if mdx_column is missing from the first row

                callback_sp = task.get(callback_sp_column)

                if callback_sp:
                    column_map = json.loads(task.get(column_map_column))
                    callback_url = urljoin(task_sp_url, '../' + callback_sp)
                    callback_args = json.loads(task.get(callback_args_column, '{}'))
                    if out_params:
                        callback_args.update(out_params)

                    parallel_tasks.append({
                            "(://)": _url_mdx_reader,
                            "(...)": {
                                "connection_string": mdx_conn_str,
                                "command_text": mdx_query,
                                "result_model": result_model,
                                "column_mapping": column_map,
                                "pass_result_to_url": callback_url,
                                "more_args": callback_args
                                },
                            "(:!!)": timeout
                        })

            if parallel_tasks:
                serial_tasks.append({"[###]": parallel_tasks})

        if serial_tasks:
            if len(serial_tasks) == 1:
                svc_grp = serial_tasks[0]
            else:
                svc_grp = {"[+++]": serial_tasks}
        else:
            svc_grp = None

        return (svc_grp, post_url, post_sp_args)

    try:
        result = None

        while True:
            result = invoke_main_sp(task_sp_url, sp_args, timeout)

            svc_grp, post_url, post_sp_args = get_tasks(result)

            if svc_grp:

                result = request_json(_url_svc_grp, {"rest": svc_grp})

                if post_url:
                    task_sp_url, sp_args = post_url, post_sp_args
                else:
                    break
            else:
                break

    except Exception as err:
        if not _notify(result, err, notify_url, notify_args):   # Send a notification with result data and/or error information
            raise

    else:
        _notify(result, None, notify_url, notify_args)          # Send a notification with result data

    return result



__version__ = "0.1a0.dev2"
