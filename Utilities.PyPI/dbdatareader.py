# -*- coding: utf-8 -*-
"""
dbDataReader - Data Reader for .NET IDataReader

----

**dbDataReader** is a simple data reader for reading .NET ``System.Data.IDataReader``-like forward-only streams.

The returned data model depends on the type of data container passed in.

4 built-in container classes:

-   ``ListOfList``
-   ``DictOfList``
-   ``ListOfDict``
-   ``SqlTvp``

are shipped with this package.

Please refer to the `MDX Reader <https://github.com/DataBooster/PyWebApi/blob/master/Sample/UserApps/MdxReader/adomd_client.py>`__ 
example and its `product documentation <https://github.com/DataBooster/PyWebApi#mdx-reader>`__ for quick details.

----

| Homepage and documentation: https://github.com/DataBooster/PyWebApi
| Copyright (c) 2020 Abel Cheng
| License: MIT
"""

from collections.abc import Mapping
from abc import ABCMeta, abstractmethod


class IResultSet(metaclass=ABCMeta):
    """This is the abstract base class for the concrete class of data container"""

    @abstractmethod
    def set_column_names(self, column_names:list):
        """This method is used to set the column names of the data to be received.

    :param column_names: A list of column names. The position of each column of the data to be received must match this list.
        """
        pass

    @abstractmethod
    def add_row_values(self, row_values:list):
        """This method is used to fill a row of data from the forward-only stream.

    :param row_values: A row of data values (a list of values) read from the forward-only stream. 
                       The position of each item of the list must match the list of column names received before.
        """
        pass

    @property
    @abstractmethod
    def result(self):
        """This property renders the the received data as the specific model of this container."""
        return self


class ListOfList(IResultSet):
    """This container class inherited from iresultset can be used to load data as following structure:

    .. code-block:: python

        {
            'column_names': [a-list-of-column-name], 
            'value_matrix': [
                                [list-of-row1values], 
                                [list-of-row2values], 
                                [list-of-row3values] 
                                ...
                            ]
        }

----

    :param trim_func: A function used to map each incoming original column name to the corresponding simple name.
                      For example, trims "``[Some Dimension]...[Column Name A].[MEMBER_CAPTION]``" to "``Column Name A``"
    :param column_mapping: A specific mapping dictionary can be used to customize irregular column name mapping.
                           For example, ``{'Column Name A': 'Branch', 'Useless Col2': ''}``
                           Mapping a column name to empty string (or None) - often used to indicate that column 
                           does not need to appear in the final rendering of data.
    """
    def __init__(self, trim_func, column_mapping:Mapping):
        self._trim_func = trim_func
        self._column_mapping = column_mapping
        self.column_names = []
        self.result_set = []

    def set_column_names(self, column_names:list):
        """This method is used to set the column names of the data to be received.

    :param column_names: A list of column names. The position of each column of the data to be received must match this list.
        """
        for col_name in column_names:
            if self._trim_func:
                col_name = self._trim_func(col_name)
            if self._column_mapping:
                col_name = self._column_mapping.get(col_name, col_name)
            self.column_names.append(col_name)

    def add_row_values(self, row_values:list):
        """This method is used to fill a row of data from the forward-only stream.

    :param row_values: A row of data values (a list of values) read from the forward-only stream. 
                       The position of each item of the list must match the list of column names received before.
        """
        self.result_set.append(row_values)

    @property
    def result(self):
        """This property renders the received data as the following structure:

    .. code-block:: python

        {
            'column_names': [a-list-of-column-name], 
            'value_matrix': [
                                [list-of-row1values], 
                                [list-of-row2values], 
                                [list-of-row3values] 
                                ...
                            ]
        }
        """
        return {'column_names': self.column_names, 'value_matrix': self.result_set}


class ListOfDict(ListOfList):
    """This container class inherited from iresultset can be used to load data as following structure:

    .. code-block:: python

        [
            {'Column_A': value_a1,  'Column_B': value_b1, 'Column_C': value_c1, ... },
            {'Column_A': value_a2,  'Column_B': value_b2, 'Column_C': value_c2, ... },
            {'Column_A': value_a3,  'Column_B': value_b3, 'Column_C': value_c3, ... }
            ...
        ]

----

    :param trim_func: A function used to map each incoming original column name to the corresponding simple name.
                      For example, trims "``[Some Dimension]...[Column Name A].[MEMBER_CAPTION]``" to "``Column Name A``"
    :param column_mapping: A specific mapping dictionary can be used to customize irregular column name mapping.
                           For example, ``{'Column Name A': 'Branch', 'Useless Col2': ''}``
                           Mapping a column name to empty string (or None) - often used to indicate that column 
                           does not need to appear in the final rendering of data.
    """
    def __init__(self, trim_func, column_mapping:Mapping):
        super().__init__(trim_func, column_mapping)


    def add_row_values(self, row_values:list):
        """This method is used to fill a row of data from the forward-only stream.

    :param row_values: A row of data values (a list of values) read from the forward-only stream. 
                       The position of each item of the list must match the list of column names received before.
        """
        row_dict = {}
        i = 0
        for col_value in row_values:
            cn = self.column_names[i]
            if cn:
                row_dict[cn] = col_value
            i += 1
        self.result_set.append(row_dict)


    @property
    def result(self):
        """This property renders the received data as the following structure:

    .. code-block:: python

        [
            {'Column_A': value_a1,  'Column_B': value_b1, 'Column_C': value_c1, ... },
            {'Column_A': value_a2,  'Column_B': value_b2, 'Column_C': value_c2, ... },
            {'Column_A': value_a3,  'Column_B': value_b3, 'Column_C': value_c3, ... }
            ...
        ]
        """
        return self.result_set


class SqlTvp(ListOfDict):
    """This container class inherited from iresultset can be used to load data as 'Table-Valued Parameters' for SQL Server:

    .. code-block:: python

        {
            'TableValuedParam':
                [
                    {'Column_A': value_a1,  'Column_B': value_b1, 'Column_C': value_c1, ... },
                    {'Column_A': value_a2,  'Column_B': value_b2, 'Column_C': value_c2, ... },
                    {'Column_A': value_a3,  'Column_B': value_b3, 'Column_C': value_c3, ... }
                    ...
                ]
        }

----

    :param trim_func: A function used to map each incoming original column name to the corresponding simple name.
                      For example, trims "``[Some Dimension]...[Column Name A].[MEMBER_CAPTION]``" to "``Column Name A``"
    :param column_mapping: A specific mapping dictionary can be used to customize irregular column name mapping.
                           For example, ``{'Column Name A': 'Branch', 'Useless Col2': ''}``
                           Mapping a column name to empty string (or None) - often used to indicate that column 
                           does not need to appear in the final rendering of data.
                           Special Note: A empty key in the map is used to specify the name of the table-valued parameter.
    """

    @property
    def result(self):
        """This property renders the received data as the following structure:

    .. code-block:: python

        {
            'TableValuedParam':
                [
                    {'Column_A': value_a1,  'Column_B': value_b1, 'Column_C': value_c1, ... },
                    {'Column_A': value_a2,  'Column_B': value_b2, 'Column_C': value_c2, ... },
                    {'Column_A': value_a3,  'Column_B': value_b3, 'Column_C': value_c3, ... }
                    ...
                ]
        }

----

    Note: The actual name of 'TableValuedParam' depends on the value of the empty key in the column mapping passed in the class initialization.
        """
        tvp = ''
        if self._column_mapping:
            tvp = self._column_mapping.get('', '').strip()
            if not tvp:
                tvp = self._column_mapping.get(None, '').strip()

        if not tvp:
            tvp = 'TableValuedParam'    # default name

        return {tvp: self.result_set}


class DictOfList(ListOfList):
    """This container class inherited from iresultset can be used to load data as following structure:

    .. code-block:: python

        {
            'Column_A': [value_a1, value_a2, value_a3, ...],
            'Column_B': [value_b1, value_b2, value_b3, ...],
            'Column_C': [value_c1, value_c2, value_c3, ...],
            ...
        }

----

    :param trim_func: A function used to map each incoming original column name to the corresponding simple name.
                      For example, trims "``[Some Dimension]...[Column Name A].[MEMBER_CAPTION]``" to "``Column Name A``"
    :param column_mapping: A specific mapping dictionary can be used to customize irregular column name mapping.
                           For example, ``{'Column Name A': 'Branch', 'Useless Col2': ''}``

                           *Mapping a column name to empty string (or None) - often used to indicate that column 
                           does not need to appear in the final rendering of data.*
    """
    def __init__(self, trim_func, column_mapping:Mapping):
        super().__init__(trim_func, column_mapping)

    def set_column_names(self, column_names:list):
        """This method is used to set the column names of the data to be received.

    :param column_names: A list of column names. The position of each column of the data to be received must match this list.
        """
        self.result_set.clear()
        for col_name in column_names:
            if self._trim_func:
                col_name = self._trim_func(col_name)
            if self._column_mapping:
                col_name = self._column_mapping.get(col_name, col_name)
            self.column_names.append(col_name)
            self.result_set.append([])


    def add_row_values(self, row_values:list):
        """This method is used to fill a row of data from the forward-only stream.

    :param row_values: A row of data values (a list of values) read from the forward-only stream. 
                       The position of each item of the list must match the list of column names received before.
        """
        i = 0
        for col_value in row_values:
            self.result_set[i].append(col_value)
            i += 1

    @property
    def result(self):
        """This property renders the received data as the following structure:

    .. code-block:: python

        {
            'Column_A': [value_a1, value_a2, value_a3, ...],
            'Column_B': [value_b1, value_b2, value_b3, ...],
            'Column_C': [value_c1, value_c2, value_c3, ...],
            ...
        }
        """
        result_dict = {}
        column_count = len(self.column_names)
        i = 0
        while i < column_count:
            cn = self.column_names[i]
            if cn:
                result_dict[cn] = self.result_set[i]
            i += 1
        return result_dict



# For .NET IDataReader Interface
class DbDataReader(object):
    """This class is used to encapsulate an ``IDataReader``-like (https://docs.microsoft.com/en-us/dotnet/api/system.data.idatareader) 
forward-only stream into a Python context manager and read the data into the expected structure.

    :param i_data_reader: An instance with ``IDataReader``-like interface.
    """
    def __init__(self, i_data_reader): 
        if i_data_reader.IsClosed:
            raise ValueError("the data reader has been closed")
        self._data_reader = i_data_reader

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if not self._data_reader.IsClosed:
            self._data_reader.Close()


    def read_one_result(self, result_set:IResultSet):
        """Read current result set into a specified data container.

    :param result_set: An instance of a data container class inherited from IResultSet.
        """
        if not isinstance(result_set, IResultSet):
            raise TypeError("the result_set argument must be an object inherited from IResultSet")
        
        field_count = self._data_reader.FieldCount
        column_names = [''] * field_count
        i = 0
        while i < field_count:
            column_names[i] = self._data_reader.GetName(i)
            i += 1

        result_set.set_column_names(column_names)

        row_values = []
        while(self._data_reader.Read()):
            row_values = [None] * field_count
            i = 0
            while i < field_count:
                row_values[i] = self._data_reader.GetValue(i)
                i += 1

            result_set.add_row_values(row_values)

        return result_set.result


    def read_all_results(self, result_set_class, *args, **kwargs) -> list:
        """Read all result sets as a specified data structure.

    :param result_set_class: The class of the data container inherited from IResultSet.
    :param args: Any positional argument(s) for initializing the result_set_class class.
    :param kwargs: Any keyword argument(s) for initializing the result_set_class class.

    :return: A list of result sets, each of them is presented by the result_set_class.
        """
        result_set_list = []

        while True:
            result_set = result_set_class(*args, **kwargs)
            self.read_one_result(result_set)
            result_set_list.append(result_set.result)

            if not self._data_reader.NextResult():
                break

        return result_set_list



__version__ = "0.1a10"
