# -*- coding: utf-8 -*-
"""
task_grouping - Task Grouping

----



|

| Homepage and documentation: https://github.com/DataBooster/PyWebApi
| Copyright (c) 2020 Abel Cheng
| License: MIT
"""

from abc import ABCMeta, abstractmethod
from typing import Union, List, Dict, Tuple, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


class TaskContainer(object):

    def __init__(self, func:Callable, merge_fn:Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]], thread_pool:ThreadPoolExecutor, **kwargs):
        self.task_group : List[TaskContainer] = kwargs.get('task_group', None)
        self.parallel : bool = kwargs.get('parallel', False)
        self.thread_pool = thread_pool
        self.timeout : float = kwargs.get('timeout', None)

        self.func = func
        self.pos_args : Tuple = kwargs.get('pos_args', ())
        self.kw_args : Dict = kwargs.get('kw_args', {})

        self.merge_fn = merge_fn

        self.check_group()


    def check_group(self):
        if self.task_group:
            for t in self.task_group:
                self._check_task_type(t)
                t.check_group()


    def run(self, pipeargs:dict={}):
        if self.task_group is None:
            return self._single_run(pipeargs)
        else:
            if self.parallel and self.thread_pool and self.task_group and len(self.task_group) > 1:
                return self._parallel_run(pipeargs)
            else:
                return self._serial_run(pipeargs)


    def _pipe_in(self, pipeargs:Union[Dict, List[Dict]]={}) -> Dict:
        if pipeargs:
            if isinstance(pipeargs, dict):
                return pipeargs

            if isinstance(pipeargs, iterable):
                pipe_args = {}
                for p in pipeargs:
                    d = self._pipe_in(p)
                    if d:
                        pipe_args.update(d)
                return pipe_args

        return {}


    def _single_run(self, pipeargs:dict={}):
        if self.func:
            if self.pos_args is None:
                self.pos_args = ()

            if self.kw_args is None:
                self.kw_args = {}

            pipe_args = self._pipe_in(pipeargs)
            if pipe_args and self.merge_fn:
                kw_args = self.merge_fn(self.kw_args, pipe_args)
            else:
                kw_args = self.kw_args

            return self.func(*self.pos_args, **kw_args)
        else:
            return None


    def _check_task_type(self, task):
       if not isinstance(task, TaskContainer):
          raise TypeError("each task context must be an instance of the TaskContainer class")


    def _serial_run(self, pipeargs:dict={}):
        serial_results = []

        for task in self.task_group:
            self._check_task_type(task)
            pipeargs = result = task.run(pipeargs)
            serial_results.append(result)

        return serial_results


    def _parallel_run(self, pipeargs:dict={}):
        task_list = []

        for task in self.task_group:
            self._check_task_type(task)
            task_list.append(self.thread_pool.submit(task.run, pipeargs))

        parallel_results = []
        for future in as_completed(task_list, self.timeout):
            parallel_results.append(future.result())

        return parallel_results



class ITaskLoader(metaclass=ABCMeta):

    @abstractmethod
    def create_base_container(self) -> TaskContainer:
        pass


    def create_single_task(self, *args, **kwargs) -> TaskContainer:
        task = create_base_container()
        task.pos_args = args
        task.kw_args = kwargs
        task.parallel = False
        task.thread_pool = None

        return task


    def _create_group_task(self, task_group:List[TaskContainer]) -> TaskContainer:
        if not task_group:
            raise ValueError("the task_group cannot be empty")

        task = create_base_container()
        task.task_group = task_group
        task.func = None

        task.check_group()
        return task


    def create_serial_group(self, task_group:List[TaskContainer]) -> TaskContainer:
        task = self._create_group_task(task_group)
        task.parallel = False
        return task


    def create_parallel_group(self, task_group:List[TaskContainer], timeout:float=None) -> TaskContainer:
        task = self._create_group_task(task_group)
        task.parallel = True if len(task_group) > 1 else False
        task.timeout = timeout
        return task

