# -*- coding: utf-8 -*-
from setuptools import setup

import task_grouping

setup(name='task-grouping',
      version=task_grouping.__version__,
      description='Task Grouping',
      long_description=task_grouping.__doc__,
      keywords=("grouping", "tasks", "parallel", "serial", "pipeline", "arguments", "container", "loader", "JSON", "tree"),
      author='Abel Cheng',
      author_email='abelcys@gmail.com',
      url='https://github.com/DataBooster/PyWebApi',
      license='MIT',
      platforms='any',
      py_modules=['task_grouping'],
      python_requires='>=3.5')
