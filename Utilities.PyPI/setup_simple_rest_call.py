# -*- coding: utf-8 -*-
from setuptools import setup

import simple_rest_call

setup(name='simple-rest-call',
      version=simple_rest_call.__version__,
      description='Simple RESTful Call',
      long_description=simple_rest_call.__doc__,
      keywords=("RESTful", "Request", "JSON", "WebAPI", "DateTime", "Windows", "Authentication"),
      author='Abel Cheng',
      author_email='abelcys@gmail.com',
      url='https://github.com/DataBooster/PyWebApi',
      license='MIT',
      platforms='any',
      py_modules=['simple_rest_call'],
      install_requires=['requests-negotiate-sspi', 'jsonpickle', 'python-dateutil'],
      python_requires='>=3.6')
