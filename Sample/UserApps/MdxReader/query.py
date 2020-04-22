# -*- coding: utf-8 -*-
from adomd_client import AdomdClient


def query(connection_string:str, command_text:str, result_model:str='ListOfDict', column_mapping:dict={}):
    with AdomdClient(connection_string) as client:
        return client.query(command_text, result_model, column_mapping)
