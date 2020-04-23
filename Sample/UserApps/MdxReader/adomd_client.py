# -*- coding: utf-8 -*-
"""
    adomd_client.py
    This module encapsulates Microsoft.AnalysisServices.AdomdClient as a Python context manager, 
    also presents an example of using dbdatareader to read query results into an expectation model.

    Homepage and documentation: https://github.com/DataBooster/PyWebApi
    Copyright (c) 2020 Abel Cheng
    License: MIT
"""
import re
from dbdatareader import DbDataReader, DictOfList, ListOfDict, ListOfList

import clr
clr.AddReference('Microsoft.AnalysisServices.AdomdClient')
from Microsoft.AnalysisServices.AdomdClient import AdomdConnection, AdomdCommand, AdomdDataReader


_reg_mdx_column_name = re.compile(r'(?P<sb>\[)?(?P<col>(?(sb)([^\]]|\]\])*|\w*))(?(sb)\]|\b)\s*(\.\s*\[MEMBER_CAPTION\]\s*$|\.\s*MEMBER_CAPTION\s*$|$)', re.I)

def trim_mdx_column_name(raw_caption:str) -> str:
    m = _reg_mdx_column_name.search(raw_caption)
    if m:
        return m.group('col').strip().replace(']]', ']')
    else:
        return raw_caption.strip()


class AdomdClient(object):
    def __init__(self, connection_string:str):
        self._connection = AdomdConnection(connection_string)

    def __enter__(self):
        if self._connection.State == 0:
            self._connection.Open()
        elif self._connection.State == 16:
            self._connection.Close()
            self._connection.Open()

        return self

    #enum ConnectionState:
    #    Broken 16
    #    Closed 0
    #    Connecting 2
    #    Executing 4
    #    Fetching 8
    #    Open 1

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self._connection.State != 0:
            self._connection.Close()


    def execute(self, command_text:str, result_model:str='ListOfDict', column_mapping:dict={}) -> list:
        model = result_model.lower().strip()

        if model == 'dictoflist':
            result_set_class = DictOfList
        elif model == 'listofdict':
            result_set_class = ListOfDict
        else:
            result_set_class = ListOfList

        cmd = AdomdCommand(command_text, self._connection)
        all_results = []

        with DbDataReader(cmd.ExecuteReader()) as reader:
            all_results = reader.read_all_results(result_set_class, trim_func=trim_mdx_column_name, column_mapping=column_mapping)

        # In most cases, there will be only one result set, which can be taken directly from the list.
        return all_results[0] if all_results and len(all_results) == 1 else all_results
