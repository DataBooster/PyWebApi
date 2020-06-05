# -*- coding: utf-8 -*-
"""
task_grouping - Task Grouping

----

This module provides a basic class library for task grouping, mainly includes 2 classes:

*   TaskContainer - 

*   ITaskLoader - 

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


    @property
    def task_group(self):
        return self.__task_group

    @task_group.setter
    def task_group(self, group):
        if group is None:
            self.__task_group = None
        elif isinstance(group, list):
            if len(group) < 1:
                raise ValueError("task_group cannot be empty")

            for t in group:
                if not isinstance(t, TaskContainer):
                    raise TypeError("each task context must be an instance of the TaskContainer class")

            self.__task_group = group
        else:
            raise TypeError("task_group must be a list of TaskContainer")


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


    def _serial_run(self, pipeargs:dict={}):
        serial_results = []

        for task in self.task_group:
            pipeargs = result = task.run(pipeargs)
            serial_results.append(result)

        return serial_results


    def _parallel_run(self, pipeargs:dict={}):
        task_list = []

        for task in self.task_group:
            task_list.append(self.thread_pool.submit(task.run, pipeargs))

        parallel_results = []
        for future in as_completed(task_list, self.timeout):
            parallel_results.append(future.result())

        return parallel_results



class ITaskLoader(metaclass=ABCMeta):

    @abstractmethod
    def create_base_container(self) -> TaskContainer:
        pass


    @abstractmethod
    def extract_single_task(self, task_node:Dict[str, Any]) -> Tuple[tuple, Dict[str, Any]]:
        pass

    @abstractmethod
    def extract_serial_group(self, task_node:Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def extract_parallel_group(self, task_node:Dict[str, Any]) -> List[Dict[str, Any]]:
        pass


    def create_single_task(self, *args, **kwargs) -> TaskContainer:
        task = self.create_base_container()
        task.pos_args = args
        task.kw_args = kwargs
        task.parallel = False
        task.thread_pool = None

        return task


    def create_group_task(self, task_group:List[TaskContainer], parallel:bool=False) -> TaskContainer:
        if not task_group:
            raise ValueError("the task_group cannot be empty")

        task = self.create_base_container()
        task.task_group = task_group
        task.func = None

        task.parallel = parallel if len(task_group) > 1 else False
        return task


    def load(self, task_tree:Dict[str, Any]) -> TaskContainer:
        if not isinstance(task_tree, dict):
            raise TypeError("task_tree argument must be a dictionary type: Dict[str, Any]")

        leaf = self.extract_single_task(task_tree)
        if leaf is not None:
            if not isinstance(leaf, tuple) or len(leaf) != 2 or not isinstance(leaf[0], tuple) or not isinstance(leaf[1], dict):
                raise TypeError("extract_single_task must return Tuple[tuple, Dict[str, Any]] if the current node is a leaf task, otherwise it must return None.")
            return self.create_single_task(*leaf[0], **leaf[1])

        serial = self.extract_serial_group(task_tree)
        if serial is not None:
            if not isinstance(serial, list) or len(serial) < 1 or not isinstance(serial[0], dict):
                raise TypeError("extract_serial_group must return List[Dict[str, Any]] if the current node is a serial group, otherwise it must return None.")
            return self.create_group_task([self.load(t) for t in serial], False)

        parallel = self.extract_parallel_group(task_tree)
        if parallel is not None:
            if not isinstance(parallel, list) or len(parallel) < 1 or not isinstance(parallel[0], dict):
                raise TypeError("extract_parallel_group must return List[Dict[str, Any]] if the current node is a parallel group, otherwise it must return None.")
            return self.create_group_task([self.load(t) for t in parallel], True)

        raise TypeError(f"current node of task_tree is not a leaf task, serial task group or parallel task group.\n{repr(task_tree)}")



__version__ = "0.1a0.dev1"
