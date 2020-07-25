# -*- coding: utf-8 -*-
from setuptools import setup

import powerbi_push_datasets

setup(name='powerbi-push-datasets',
      version=powerbi_push_datasets.__version__,
      description='Power BI Push Datasets Mgmt',
      long_description=powerbi_push_datasets.__doc__,
      keywords=("PowerBI", "Push", "Datasets", "REST", "API", "Tabular", "Model", "ResultSets", "StoredProcedure", "TabularEditor", "metadata", "schema", "table", "workspace", "pump", "xcopy"),
      author='Abel Cheng',
      author_email='abelcys@gmail.com',
      url='https://github.com/DataBooster/PyWebApi',
      license='MIT',
      platforms='any',
      py_modules=['powerbi_push_datasets'],
      install_requires=['simple-rest-call'],
      python_requires='>=3.6')
