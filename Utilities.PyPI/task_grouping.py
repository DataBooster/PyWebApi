# -*- coding: utf-8 -*-
"""
task_grouping - Task Grouping

----

This module provides a basic class library for task grouping, includes 2 classes:

-   **TaskContainer**

    Organizes a batch of task groups, including the serial/parallel structures, and carries the arguments information for each task unit to run.

-   **ITaskLoader**

    This is an abstract base class for implementing a concrete loader class to load a task tree from Dict/JSON to TaskContainer.

----

| Homepage and documentation: https://github.com/DataBooster/PyWebApi
| Copyright (c) 2020 Abel Cheng
| License: MIT
"""

from abc import ABCMeta, abstractmethod
from typing import Union, List, Dict, Tuple, Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


class TaskContainer(object):
    """Organizes a batch of task groups, including the serial/parallel structures, and carries the arguments information for each task unit to run.

    :param func: A callable to be executed by the task.
    :param merge_fn: A function for merging pipeline arguments (a dictionary ``[Dict[str, Any]``) with user input arguments (a dictionary ``[Dict[str, Any]``), it must return a new dictionary ``[Dict[str, Any]``.
    :param thread_pool: An instance of ``ThreadPoolExecutor`` for executing any parallel task group. This argument is required, otherwise any parallel task group will actually be executed serially.
    """
    def __init__(self, func:Callable, merge_fn:Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]], thread_pool:ThreadPoolExecutor, **kwargs):
        self.task_group : List[TaskContainer] = kwargs.get('task_group', None)
        self.parallel : bool = kwargs.get('parallel', False)
        self.thread_pool = thread_pool
        self.timeout : float = kwargs.get('timeout', None)

        self.func = func
        self.pos_args : Tuple = kwargs.get('pos_args', ())
        self.kw_args : Dict = kwargs.get('kw_args', {})

        self.merge_fn = merge_fn    # A function for merging pipeline arguments with user input kw_args


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
        """Execute all tasks and task groups in the specified order (serial/parallel) and assemble their results into a tree structure corresponding to the input payload.

    :param pipeargs: (optional) If the result of the previous task is a dictionary ``[Dict[str, Any]``, it can be piped to current task or task group at run time and merged into the user input arguments.

        -   If current task is a serial group, the first subtask will receive the pipeline arguments, and the result of the first subtask will be used as the pipeline arguments of the second subtask, and so on.
        -   If current task is a parallel group, all subtasks will receive this same pipeline arguments.

    :return: All results will be assembled into a tree structure corresponding to the input payload.
        """
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

            if self.merge_fn:
                pipe_args = self._pipe_in(pipeargs)
                if pipe_args:
                    kw_args = self.merge_fn(self.kw_args, pipe_args)
                else:
                    kw_args = self.kw_args
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
    """This is an abstract base class for implementing a concrete loader class to load a task tree from Dict/JSON to ``TaskContainer``."""

    @abstractmethod
    def create_base_container(self) -> TaskContainer:
        """This method is used to create a new container and initialize the most basic properties of ``TaskContainer``: ``func``, ``merge_fn``, ``thread_pool``, etc.
    For an example:

    .. code-block:: python

        def create_base_container(self) -> TaskContainer:
            return TaskContainer(self.task_func, self.pipemerge_fn, self.thread_pool, **{'timeout':self.timeout})
        """
        pass


    @abstractmethod
    def extract_single_task(self, task_node:Dict[str, Any]) -> Tuple[tuple, Dict[str, Any], bool]:
        """This method is used to determine whether the task node is a leaf task (single task).
If so, it should return a tuple containing three elements:

1.   The first element must be a tuple containing the positional arguments to be passed to the task. If the position argument is not needed at all, please put ``()``;
2.   The second element must be a dictionary containing keyworded arguments to be passed to the task. If there are no arguments, please put ``{}``;
3.   The third element must be a Boolean value to indicate whether to merge the execution result of the previous task as a pipeline argument into the user input keyworded arguments.

If the task node is NOT a leaf task, this method should return ``None``.

    :param task_node: A node of task tree - ``Dict[str, Any]``.
    :return: ``Tuple[tuple, Dict[str, Any], bool]``
        """
        pass


    @abstractmethod
    def extract_serial_group(self, task_node:Dict[str, Any]) -> List[Dict[str, Any]]:
        """This method is used to determine whether the task node is a serial task group.

If so, a list of child nodes ``List[Dict[str, Any]]`` should be returned for recursive extraction;

Otherwise, ``None`` should be returned.

    :param task_node: A node of task tree - ``Dict[str, Any]``.
    :return: ``List[Dict[str, Any]]``
        """
        pass


    @abstractmethod
    def extract_parallel_group(self, task_node:Dict[str, Any]) -> List[Dict[str, Any]]:
        """This method is used to determine whether the task node is a parallel task group.

If so, a list of child nodes ``List[Dict[str, Any]]`` should be returned for recursive extraction;

Otherwise, ``None`` should be returned.

    :param task_node: A node of task tree - ``Dict[str, Any]``.
    :return: ``List[Dict[str, Any]]``
        """
        pass


    def create_single_task(self, with_pipe:bool=False, *args, **kwargs) -> TaskContainer:
        """This method creates an instance of ``TaskContainer`` for a single (leaf) task.

    :param with_pipe: A Boolean value indicates that the task accepts pipeline parameters from the result of the previous task.

        *When the pipeline arguments and user input arguments are both dictionary types, the arguments of these two parts can be merged together.*

    :param args: Positional arguments to be passed to the task.
    :param kwargs: keyworded arguments to be passed to the task.
    :return: An instance of ``TaskContainer``
        """
        task = self.create_base_container()
        task.pos_args = args
        task.kw_args = kwargs
        task.parallel = False
        task.thread_pool = None

        if not with_pipe:
            task.merge_fn = None

        return task


    def create_group_task(self, task_group:List[TaskContainer], parallel:bool=False) -> TaskContainer:
        """This method creates an instance of ``TaskContainer`` for a task group.

    :param task_group: A list of subtasks, each subtask is presented as a ``TaskContainer``.

    :param parallel: A Boolean value indicates that its first-level subtasks should be executed in parallel (``True`` value) or serial (``False`` value).
    :return: An instance of ``TaskContainer``
        """
        if not task_group:
            raise ValueError("the task_group cannot be empty")

        task = self.create_base_container()
        task.task_group = task_group
        task.func = None

        task.parallel = parallel if len(task_group) > 1 else False
        return task


    def load(self, task_tree:Dict[str, Any]) -> TaskContainer:
        """This method is used to load a task tree from Dict/JSON to a ``TaskContainer``
    :param task_tree: A task tree ``Dict[str, Any]`` containing all task groups and user input arguments.

        Usually, this dictionary tree comes from the client JSON payload.

    :return: An instance of ``TaskContainer``
        """
        if not isinstance(task_tree, dict):
            raise TypeError("task_tree argument must be a dictionary type: Dict[str, Any]")

        leaf = self.extract_single_task(task_tree)
        if leaf is not None:
            if not isinstance(leaf, tuple) or len(leaf) != 3 or not isinstance(leaf[0], tuple) or not isinstance(leaf[1], dict) or not isinstance(leaf[2], bool):
                raise TypeError("extract_single_task must return Tuple[tuple, Dict[str, Any], bool] if the current node is a leaf task, otherwise it must return None.")
            return self.create_single_task(leaf[2], *leaf[0], **leaf[1])

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
