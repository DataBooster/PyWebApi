# -*- coding: utf-8 -*-
"""push_datasets.py



    This module was originally shipped as an example code from https://github.com/DataBooster/PyWebApi, licensed under the MIT license.
    Anyone who obtains a copy of this code is welcome to modify it for any purpose, and holds all rights to the modified part only.
    The above license notice and permission notice shall be included in all copies or substantial portions of the Software.
"""

from os import path as os_path
from json import loads as json_decode
from collections.abc import MutableMapping
from authorization import get_accesstoken
from powerbi_push_datasets import PushDatasetsMgmt
from model import invoke_sp, get_table_name_seq_list, extract_sp_name


def deploy_dataset(model_bim:MutableMapping, dataset_name:str, workspace:str=None):
    if isinstance(model_bim, str):
        if 8 < len(model_bim) < 200 and model_bim[-4:].lower() == '.bim' and os_path.exists(model_bim):
            with open(model_bim, 'r') as bim_file:
                model_bim = bim_file.read()
        model_bim = json_decode(model_bim)

    if not isinstance(model_bim, MutableMapping):
        raise ValueError(f"model_bim argument is not a valid JSON")

    if not dataset_name:
        raise ValueError(f"dataset_name argument is missing")

    access_token = get_accesstoken()

    pd_mgmt = PushDatasetsMgmt(access_token)

    return pd_mgmt.deploy_dataset(model_bim, dataset_name, workspace)


def push_data(sp_url:str, sp_args:dict=None, dataset_name:str=None, workspace:str=None, timeout:float=1800):
    if not dataset_name:
        dataset_name = extract_sp_name(sp_url)

    result = invoke_sp(sp_url, sp_args, timeout)

    metadata = result['ResultSets'].pop(0)
    table_name_seq_list = get_table_name_seq_list(metadata, False)

    access_token = get_accesstoken()

    pd_mgmt = PushDatasetsMgmt(access_token)

    pd_mgmt.push_tables(result['ResultSets'], table_name_seq_list, dataset_name, workspace)

    table_names = [tbn for tbn, seq in table_name_seq_list]
    return pd_mgmt.get_sequence_numbers(table_names, dataset_name, workspace)

