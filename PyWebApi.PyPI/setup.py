# -*- coding: utf-8 -*-
from setuptools import setup

import pywebapi

setup(name='pywebapi',
      version=pywebapi.__version__,
      description=next(filter(None, map(lambda l: l.strip(), pywebapi.__doc__.splitlines()))),
      long_description=pywebapi.__doc__,
      keywords=("RESTful", "Service", "WebAPI", "IIS", "JSON", "DataBooster", "Python", "module_level_function", "HTTP"),
      author='Abel Cheng',
      author_email='abelcys@gmail.com',
      url='https://github.com/DataBooster/PyWebApi',
      license='MIT',
      platforms='any',
      packages=['pywebapi'],
      python_requires='>=3',
      install_requires=['bottle'])
