# -*- coding: utf-8 -*-
"""
powerbi_push_datasets - Power BI Push Datasets Mgmt

----

The main class **PushDatasetsMgmt** encapsulates the Power BI REST operations on `Push Datasets <https://docs.microsoft.com/en-us/rest/api/power-bi/pushdatasets>`_
into a few simple methods:

-   ``deploy_dataset`` : Create a pushable dataset (or update the metadata and schema for existing tables) in Power BI Service by a `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file);
-   ``push_tables`` : Push a `ResultSets of Stored Procedure (ResultSets) <https://github.com/DataBooster/DbWebApi/wiki#http-response>`__ - data for multiple tables into a Power BI Push Dataset;
-   ``truncate_tables`` : Removes all rows from specified (or all) tables in a Power BI Push Dataset;

This module also provides two conversion tools:

-   ``convert_bim_to_push_dataset`` : Convert a `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file) into a Push Dataset Model supported by Power BI Service;
-   ``derive_bim_from_resultsets`` : Generate a `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file) based on a `ResultSets of Stored Procedure (ResultSets) <https://github.com/DataBooster/DbWebApi/wiki#http-response>`__ - data for multiple tables;


----

| Homepage and documentation: https://github.com/DataBooster/PyWebApi
| Copyright (c) 2020 Abel Cheng
| License: MIT
"""

import re
from collections import Iterable
from collections.abc import MutableMapping
from urllib.parse import urljoin, quote
from datetime import datetime, date, time, timedelta

from simple_rest_call import request_json
from json import loads as json_decode


_uuid_pattern = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")

def is_uuid(name:str) -> bool:
    return True if _uuid_pattern.fullmatch(name) else False


def powerbi_rest_v1(access_token: str, http_method:str, rest_path:str, request_payload:dict=None, **kwargs):

    def full_url(relative_url:str) -> str:
        return urljoin("https://api.powerbi.com/v1.0/myorg/", relative_url)

    explicit_headers = kwargs.get('headers', {})
    if isinstance(explicit_headers, str):
        explicit_headers = json_decode(explicit_headers)
    if not isinstance(explicit_headers, MutableMapping):
        explicit_headers = {}

    headers = {'Pragma': 'no-cache', 'Cache-Control': 'no-cache', 'Authorization': 'Bearer ' + access_token, 'Accept': 'application/json'}
    headers.update(explicit_headers)
    kwargs['headers'] = headers

    return request_json(full_url(rest_path), request_payload, http_method, **kwargs)


def convert_bim_to_push_dataset(model_bim:MutableMapping, dataset_name:str, defaultMode:str="Push") -> dict:

    def find_tables_dict(model_bim:MutableMapping) -> MutableMapping:
        if not isinstance(model_bim, MutableMapping):
            return None

        if "tables" in model_bim:
            return model_bim

        for value in model_bim.values():
            if isinstance(value, MutableMapping):
                return find_tables_dict(value)

        return None

    def clean_up_keys(model_dict:MutableMapping, parent_key:str, include_keys:set):

        def drill_down_value(value, parent_key:str, include_keys:set):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, MutableMapping):
                        clean_up_keys(item, parent_key, include_keys)
            elif isinstance(value, MutableMapping):
                clean_up_keys(value, parent_key, include_keys)

        if parent_key:
            v = model_dict.get(parent_key)
            if v:
                drill_down_value(v, None, include_keys)
            else:
                for c in model_dict.values():
                    drill_down_value(c, parent_key, include_keys)
        else:
            for x in [k for k in model_dict if k not in include_keys]:
                model_dict.pop(x)


    if not model_bim or not dataset_name:
        return None

    if isinstance(model_bim, str):
        model_bim = json_decode(model_bim)

    model = find_tables_dict(model_bim)
    if not model:
        return None

    dataset_properties = {"name": dataset_name, "tables": model["tables"]}

    relationships = model.get('relationships')
    if relationships:
        dataset_properties["relationships"] = relationships

    if defaultMode:
        dataset_properties["defaultMode"] = defaultMode

    clean_up_keys(dataset_properties, "tables", {'columns', 'measures', 'name', 'rows', 'isHidden'})
    clean_up_keys(dataset_properties, "columns", {'dataType', 'name', 'formatString', 'sortByColumn', 'dataCategory', 'isHidden', 'summarizeBy'})
    clean_up_keys(dataset_properties, "measures", {'expression', 'name', 'formatString', 'isHidden'})
    clean_up_keys(dataset_properties, "relationships", {'crossFilteringBehavior', 'fromColumn', 'fromTable', 'name', 'toColumn', 'toTable'})

    return dataset_properties


def derive_bim_from_resultsets(result_sets:list, table_names:list, dataset_name:str) -> dict:

    def detect_data_type(column_name:str, first_value, result_set:list) -> str:
        if first_value is None:
            first_value = next((value for value in (row.get(column_name) for row in result_set) if value is not None), '')

        if isinstance(first_value, int):
            return "int64"
        elif isinstance(first_value, float):
            return "double"
        elif isinstance(first_value, bool):
            return "boolean"
        elif isinstance(first_value, (datetime, date, time, timedelta)):
            return "dateTime"
        else:
            return "string"

    def generate_table_bim(result_set:list, table_name:str) -> dict:
        if not isinstance(result_set, list) or len(result_set) == 0:
            raise ValueError(f"unable to detect metadata for {repr(table_names)} table from an empty result")

        first_row = result_set[0]
        if not isinstance(first_row, MutableMapping):
            raise ValueError(f"invalid row data for {repr(table_names)} table")

        columns = []
        for column_name, column_value in first_row.items():
            columns.append({"name":column_name, "dataType":detect_data_type(column_name, column_value, result_set)})

        if len(columns) == 0:
            raise ValueError(f"there are no columns in {repr(table_names)} table")

        return {"name":table_name, "columns":columns, "partitions":[{"name": "None","source": {"type": "m"}}]}

    if not isinstance(result_sets, list) or not isinstance(table_names, list) or len(result_sets) != len(table_names) or len(table_names) == 0:
        raise ValueError(f"the count of table_names does not match the count of result_sets")

    tables = []
    for i in range(len(table_names)):
        table_name = table_names[i]
        if isinstance(table_name, tuple) and len(table_name) > 0 and isinstance(table_name[0], str):
            table_name = table_name[0]
        if table_name:
            tables.append(generate_table_bim(result_sets[i], table_name))

    if len(tables) == 0:
        raise ValueError(f"there are no tables in {repr(dataset_name)} dataset")

    return {
        "name": dataset_name,
        "compatibilityLevel": 1520,
        "model": {
            "defaultPowerBIDataSourceVersion": "powerBI_V3",
            "tables": tables
        }
    }


class PushDatasetsMgmt(object):

    def __init__(self, access_token:str):

        self._group_dict = {}
        self._dataset_dict = {}
        self.access_token = access_token


    class ErrorAggregation(object):
        def __init__(self):
            self._error_dict = {}

        def add(self, err_obj:Exception, table_name:str):
            err_type = type(err_obj).__name__
            err_sort = self._error_dict.get(err_type)
            if err_sort is None:
                self._error_dict[err_type] = {err_obj: [table_name]}
            else:
                tbs = err_sort.get(err_obj)
                if tbs is None:
                    err_sort[err_obj] = [table_name]
                else:
                    tbs.append(table_name)

        @property
        def aggregated_error(self):
            if not self._error_dict:
                return None
            if len(self._error_dict) == 1:
                err_objs = next(e for e in self._error_dict.values())
                same_error, tb_names = next(pair for pair in err_objs.items())
                if len(err_objs) == 1:
                    same_error.args = (f"{str(tb_names)} - {str(same_error)}",)
                else:
                    same_error.args = (f"{str(tbs)} - {str(err)}" for err, tbs in err_objs.items())
                return same_error
            else:
                err_args = (f"{str(tbs)} - {repr(err)}"
                               for et, ed in self._error_dict.items() 
                               for err, tbs in ed.items())
                return RuntimeError(err_args)

        def check(self):
            agg_err = self.aggregated_error
            if agg_err:
                raise agg_err


    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, accesstoken:str):
        if accesstoken and isinstance(accesstoken, str) and len(accesstoken) > 1000:
            self._access_token = accesstoken
        else:
            raise ValueError("a valid access token is required")


    @staticmethod
    def _check_name(id:str, name:str, category:str):
        if not id or not is_uuid(id):
            raise NameError(f"the {repr(name)} is not an existing {category} name")


    def get_group_id(self, workspace:str) -> str:
        if not workspace:
            return None

        if is_uuid(workspace):
            return workspace.lower()

        group_id = self._group_dict.get(workspace)

        if group_id:
            return group_id
        else:
            name_filter = quote("name eq " + repr(workspace))
            resp = powerbi_rest_v1(self.access_token, 'GET', "groups?$filter=" + name_filter)

            if not resp:
                return resp
    
            value = resp['value']

            if len(value) == 0:
                return None

            group_id = value[0]['id']

            if group_id:
                self._group_dict[workspace] = group_id

            return group_id


    def get_dataset_id(self, dataset:str, workspace:str=None) -> str:
        if not dataset:
            return None

        if is_uuid(dataset):
            return dataset.lower()

        dataset_id = self._dataset_dict.get(dataset)

        if dataset_id:
            return dataset_id
        else:
            if workspace:
                group_id = self.get_group_id(workspace)
                self._check_name(group_id, workspace, 'workspace')
                rest_path = f"groups/{group_id}/datasets"
            else:
                rest_path = "datasets"

            resp = powerbi_rest_v1(self.access_token, 'GET', rest_path)

            if not resp:
                return resp

            value = resp['value']

            if len(value) == 0:
                return None

            dataset_id = next((v['id'] for v in value if v['name'] == dataset), None)

            if dataset_id:
                self._dataset_dict[dataset] = dataset_id

            return dataset_id


    def get_tables(self, dataset:str, workspace:str=None) -> set:
        dataset_id = self.get_dataset_id(dataset, workspace)
        self._check_name(dataset_id, dataset, 'dataset')

        if workspace:
            group_id = self.get_group_id(workspace)
            rest_path = f"groups/{group_id}/datasets/{dataset_id}/tables"
        else:
            rest_path = f"datasets/{dataset_id}/tables"

        resp = powerbi_rest_v1(self.access_token, 'GET', rest_path)

        if resp:
            return set(v['name'] for v in resp['value'])
        else:
            return set()


    def _create_dataset(self, dataset_name:str, dataset_properties:MutableMapping, defaultRetentionPolicy, group_id:str=None) -> str:
        if group_id:
            rest_path = f"groups/{group_id}/datasets"
        else:
            rest_path = "datasets"

        if defaultRetentionPolicy:
            rest_path += "?defaultRetentionPolicy=" + defaultRetentionPolicy

        resp = powerbi_rest_v1(self.access_token, 'POST', rest_path, dataset_properties)

        return resp['id']

    def _update_table(self, table_bim:MutableMapping, dataset_id:str, group_id:str=None):
        table_name = quote(table_bim["name"])

        if group_id:
            rest_path = f"groups/{group_id}/datasets/{dataset_id}/tables/{table_name}"
        else:
            rest_path = f"datasets/{dataset_id}/tables/{table_name}"

        resp = powerbi_rest_v1(self.access_token, 'PUT', rest_path, table_bim)

        return resp["name"]


    def deploy_dataset(self, model_bim:MutableMapping, dataset_name:str, workspace:str=None, defaultMode:str="Push", defaultRetentionPolicy:str='basicFIFO') -> str:

        dataset_properties = convert_bim_to_push_dataset(model_bim, dataset_name, defaultMode)

        if not dataset_properties:
            raise ValueError("the dataset properties are not sufficient to create a Power BI Push Dataset or add tables")

        group_id = self.get_group_id(workspace)
        dataset_id = self.get_dataset_id(dataset_name, workspace)

        if dataset_id:
            tables = dataset_properties.get("tables")
            if tables:
                existing_tables = self.get_tables(dataset_name, workspace)
                for table_bim in tables:
                    if table_bim["name"] in existing_tables:
                        self._update_table(table_bim, dataset_id, group_id)
            return dataset_id
        else:
            return self._create_dataset(dataset_name, dataset_properties, defaultRetentionPolicy, group_id)


    def push_rows(self, row_list:list, table_name:str, sequence_number:int, dataset_name:str, workspace:str=None):
        if not row_list or not isinstance(row_list, Iterable):
            raise TypeError("row_list argument requires a list of objects")

        if table_name:
            table_name = quote(table_name)
        else:
            raise ValueError("table_name argument is missing")

        if not dataset_name:
            raise ValueError("dataset_name argument is missing")

        dataset_id = self.get_dataset_id(dataset_name, workspace)
        self._check_name(dataset_id, dataset_name, 'dataset')

        if workspace:
            group_id = self.get_group_id(workspace)
            rest_path = f"groups/{group_id}/datasets/{dataset_id}/tables/{table_name}/rows"
        else:
            rest_path = f"datasets/{dataset_id}/tables/{table_name}/rows"

        if sequence_number:
            headers = {"X-PowerBI-PushData-SequenceNumber": str(sequence_number)}
        else:
            headers = {}

        resp = powerbi_rest_v1(self.access_token, 'POST', rest_path, {"rows": row_list}, headers=headers)


    def push_tables(self, result_sets:list, table_name_seq_list:list, dataset_name:str, workspace:str=None):

        if not isinstance(result_sets, list) or not isinstance(table_name_seq_list, list) or len(result_sets) != len(table_name_seq_list) or len(table_name_seq_list) == 0:
            raise ValueError(f"the count of table_names does not match the count of result_sets")

        agg_error = self.ErrorAggregation()

        for i in range(len(table_name_seq_list)):
            name_seq = table_name_seq_list[i]
            if isinstance(name_seq, tuple):
                table_name, seq_num = name_seq
            elif isinstance(name_seq, str):
                table_name = name_seq
                seq_num = None
            else:
                raise TypeError(f"table_name_seq_list argument requires a list of tuples [(TableName, PowerBI_PushData_SequenceNumber)]")

            new_rows = result_sets[i]
            if table_name and new_rows:
                try:
                    self.push_rows(new_rows, table_name, seq_num, dataset_name, workspace)
                except Exception as err:
                    agg_error.add(err, table_name)

        agg_error.check()


    def truncate_tables(self, table_names:list, dataset_name:str, workspace:str=None):
        if not table_names:
            table_names = self.get_tables(dataset_name, workspace)
        elif isinstance(table_names, str):
            table_names = [table_names]

        if table_names:
            dataset_id = self.get_dataset_id(dataset_name, workspace)
            group_id = self.get_group_id(workspace)
            agg_error = self.ErrorAggregation()

            for table in table_names:
                table_name = quote(table)
                if workspace:
                    rest_path = f"groups/{group_id}/datasets/{dataset_id}/tables/{table_name}/rows"
                else:
                    rest_path = f"datasets/{dataset_id}/tables/{table_name}/rows"

                try:
                    powerbi_rest_v1(self.access_token, 'DELETE', rest_path)
                except Exception as err:
                    agg_error.add(err, table_name)

            agg_error.check()


    def get_sequence_numbers(self, table_names:list, dataset_name:str, workspace:str=None):
        if not table_names:
            table_names = self.get_tables(dataset_name, workspace)
        elif isinstance(table_names, str):
            table_names = [table_names]

        table_seq_list = []
        if table_names:
            dataset_id = self.get_dataset_id(dataset_name, workspace)
            group_id = self.get_group_id(workspace)
            agg_error = self.ErrorAggregation()

            for table in table_names:
                table_name = quote(table)
                if workspace:
                    rest_path = f"groups/{group_id}/datasets/{dataset_id}/tables/{table_name}/sequenceNumbers"
                else:
                    rest_path = f"datasets/{dataset_id}/tables/{table_name}/sequenceNumbers"

                try:
                    resp = powerbi_rest_v1(self.access_token, 'GET', rest_path)
                except Exception as err:
                    agg_error.add(err, table_name)
                else:
                    resp.pop('@odata.context', None)
                    resp.setdefault('name', table)
                    table_seq_list.append(resp)

            agg_error.check()

        return table_seq_list



__version__ = "0.1a0.dev6"
