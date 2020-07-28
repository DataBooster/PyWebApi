# -*- coding: utf-8 -*-
"""model.py



    This module was originally shipped as an example code from https://github.com/DataBooster/PyWebApi, licensed under the MIT license.
    Anyone who obtains a copy of this code is welcome to modify it for any purpose, and holds all rights to the modified part only.
    The above license notice and permission notice shall be included in all copies or substantial portions of the Software.
"""

from bottle import response
from urllib.parse import urlparse
from collections.abc import Mapping, MutableMapping
from simple_rest_call import request_json
from powerbi_push_datasets import generate_bim_from_resultsets


def _invoke_sp(sp_url:str, sp_args:dict, sp_timeout:float) -> dict:

    def check_dbwebapi(result:dict) -> bool:
        if not isinstance(result, Mapping):
            return False

        if 'ResultSets' in result and 'OutputParameters' in result and 'ReturnValue' in result:
            return True
        else:
            return False

    result = request_json(sp_url, sp_args, timeout=sp_timeout)

    if result and not check_dbwebapi(result):
        raise TypeError(f"{repr(sp_url)} is not a dbwebapi call")

    return result


def _get_table_names(first_result_set:list) -> list:
    table_name_column = next(col_name for col_name, col_value in first_result_set[0].items() if isinstance(col_value, str))
    return [row[table_name_column] for row in first_result_set]


def derive_bim(sp_url:str, sp_args:dict=None, dataset_name:str=None, timeout:float=1800) -> dict:
    def extract_sp_name(sp_url:str):
        sp_path = urlparse(sp_url).path
        _, _, sp_name = sp_path.rpartition('.')
        sp_name, _, _ = sp_name.partition('/')
        return sp_name

    if not dataset_name:
        dataset_name = extract_sp_name(sp_url)

    result = _invoke_sp(sp_url, sp_args, timeout)

    metadata = result['ResultSets'].pop(0)
    table_names = _get_table_names(metadata)

    bim = generate_bim_from_resultsets(result['ResultSets'], table_names, dataset_name)

    response.set_header('Content-Disposition', f'attachment; filename="{dataset_name}.bim"')

    return bim



