# -*- coding: utf-8 -*-
"""rest_grouping.py

    This module implements:

    *   ``RestTaskLoader`` class, which is used to load a group of RESTful services (call tasks) from a JSON payload into ``TaskContainer``.

    *   ``start`` function, which is the main entry for the client to call a group of RESTful services.

    This module was originally shipped as an example code from https://github.com/DataBooster/PyWebApi, licensed under the MIT license.
    Anyone who obtains a copy of this code is welcome to modify it for any purpose, and holds all rights to the modified part only.
    The above license notice and permission notice shall be included in all copies or substantial portions of the Software.
"""
from typing import List, Tuple, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from task_grouping import TaskContainer, ITaskLoader
from simple_rest_call import request_json


_reserved_key_parallel_group : str = "[###]"
_reserved_key_serial_group : str = "[+++]"
_reserved_key_rest_url : str = "(://)"
_reserved_key_headers : str = "(:^:)"
_reserved_key_payload : str = "(...)"
_reserved_key_payload_with_pipe : str = "(.|.)"
_reserved_key_timeout : str = "(:!!)"


def _task_func(url:str, data:dict=None, timeout:float=None):
    return request_json(url, data, timeout=timeout)


def _pipeargs_merge_fn(kw_args:Dict[str, Any], pipe_args:Dict[str, Any]) -> Dict[str, Any]:
    if pipe_args and isinstance(pipe_args, dict):
        merged_args = kw_args.copy() if kw_args else {}
        payload = kw_args.get('data', {})
        if payload is None:
            payload = {}

        if isinstance(payload, dict):
            merged_args['data'] = payload.copy().update(pipe_args)

        return merged_args
    else:
        return kw_args


class RestTaskLoader(ITaskLoader):
    """This class is used to load a group of RESTful services (call tasks) from a JSON payload into ``TaskContainer``"""
    def __init__(self, thread_pool:ThreadPoolExecutor):
        self.thread_pool = thread_pool


    def create_base_container(self) -> TaskContainer:
        return TaskContainer(_task_func, _pipeargs_merge_fn, self.thread_pool)


    @staticmethod
    def _get_timeout(task_node:Dict[str, Any])->float:
        timeout = task_node.get(_reserved_key_timeout)
        if isinstance(timeout, (int, float)) and timeout > 0:
            return timeout
        else:
            return None


    def extract_single_task(self, task_node:Dict[str, Any]) -> Tuple[tuple, Dict[str, Any], bool]:
        url = task_node.get(_reserved_key_rest_url)
        if url:
            headers = task_node.get(_reserved_key_headers)

            data = task_node.get(_reserved_key_payload)
            if data is None:
               data = {}

            data_ = task_node.get(_reserved_key_payload_with_pipe)
            if data_ is not None or _reserved_key_payload_with_pipe in task_node:
                if data_:
                    data.update(data_)
                with_pipe = True
            else:
                with_pipe = False

            timeout = self._get_timeout(task_node)
            return ((), {'url': url, 'headers': headers, 'data': data, 'timeout': timeout}, with_pipe)
        else:
            return None


    def extract_serial_group(self, task_node:Dict[str, Any]) -> List[Dict[str, Any]]:
        return task_node.get(_reserved_key_serial_group)


    def extract_parallel_group(self, task_node:Dict[str, Any]) -> List[Dict[str, Any]]:
        return task_node.get(_reserved_key_parallel_group)


    def load(self, task_tree:Dict[str, Any]) -> TaskContainer:
        container = super().load(task_tree)
        container.timeout = self._get_timeout(task_tree)
        return container


def start(rest:Dict[str, Any]):
    """the main entry for the client to call a group of RESTful services."""
    with ThreadPoolExecutor(max_workers=64) as thread_pool:
        loader = RestTaskLoader(thread_pool)
        container = loader.load(rest)
        return container.run()



__version__ = "0.1"
