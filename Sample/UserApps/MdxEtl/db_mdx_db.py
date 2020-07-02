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
from bottle import request
from simple_rest_call import request_json


def _full_url(relative_url:str) -> str:
    return urljoin(request.url, relative_url)

_url_mdx_reader = _full_url("../mdxreader/mdx_task.run_query")
_url_svc_grp = _full_url("../services_grouping/rest_grouping.start")


def _check_dbwebapi(result:dict) -> bool:
    if result is None or not isinstance(result, dict):
        return False

    if 'ResultSets' in result and 'OutputParameters' in result and 'ReturnValue' in result:
        return True
    else:
        return False


def _notify(result, error=None, notify_url:str=None, notify_args:dict=None) -> bool:
    result_param_convention = '[=]'
    error_param_convention = '[!]'

    if notify_url:
        if isinstance(notify_args, dict):
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


def start(task_list_url:str, sp_args:dict, mdx_conn_str:str, each_timeout:float=1800,
          mdx_column:str='MDX_QUERY', column_map_column:str='COLUMN_MAPPING', callback_sp_column:str='CALLBACK_SP', callback_args_column:str='CALLBACK_ARGS', db_type='ora',
          post_sp_outparam:str='OUT_POST_SP', post_sp_args_outparam:str='OUT_POST_SP_ARGS',
          notify_url:str=None, notify_args:dict=None):
    try:
        task_list = request_json(task_list_url, sp_args)
        if task_list:
            prev_result = task_list
        else:
            return None

        if not _check_dbwebapi(task_list):
            raise TypeError(f"the task_list_url ({repr(task_list_url)}) is not a dbwebapi call")

        out_params = task_list['OutputParameters']
        post_sp = out_params.pop(post_sp_outparam, None)
        post_sp_args = json.loads(out_params.pop(post_sp_args_outparam, '{}'))

        if db_type and isinstance(db_type, str) and db_type[:4].lower() == 'ora':
            result_model = 'DictOfList'
        else:
            result_model = 'SqlTvp'

        parallel_tasks = []

        for t in task_list['ResultSets'][0]:
            mdx_query = t.get(mdx_column)
            if not mdx_query:
                raise ValueError(f"{repr(mdx_column)} is required for each subtask")

            callback_sp = t.get(callback_sp_column)

            if callback_sp:
                column_map = json.loads(t.get(column_map_column))
                callback_url = urljoin(task_list_url, callback_sp)
                callback_args = json.loads(t.get(callback_args_column, '{}'))
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
                        "(:!!)": each_timeout
                    })

        if not parallel_tasks:
            return None

        svc_grp = {"[###]": parallel_tasks}

        if post_sp:
            post_url = urljoin(task_list_url, post_sp)
            if out_params:
                post_sp_args.update(out_params)
            post_svc = {
                "(://)": post_url,
                "(...)": post_sp_args,
                "(:!!)": each_timeout
            }
            svc_grp = {"[+++]": [svc_grp, post_svc]}

        final_result = request_json(_url_svc_grp, {"rest": svc_grp})
        task_list = final_result

    except Exception as err:
        if not _notify(prev_result, err, notify_url, notify_args):  # Send a notification with result data and/or error information
            raise

    else:
        _notify(final_result, None, notify_url, notify_args)        # Send a notification with result data

    return final_result



__version__ = "0.1a0.dev1"
