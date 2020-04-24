# -*- coding: utf-8 -*-
from setuptools import setup

import dbdatareader

setup(name='dbdatareader',
      version=dbdatareader.__version__,
      description=next(filter(None, map(lambda l: l.strip(), dbdatareader.__doc__.splitlines()))),
      long_description=dbdatareader.__doc__,
      keywords=("IDataReader", "DataReader", "DataBooster", "WebAPI", "forward-only", "IResultSet", "ListOfList", "ListOfDict", "DictOfList"),
      author='Abel Cheng',
      author_email='abelcys@gmail.com',
      url='https://github.com/DataBooster/PyWebApi',
      license='MIT',
      platforms='any',
      py_modules=['dbdatareader'],
      python_requires='>=3')
