# -*- coding: utf-8 -*-
"""
powerbi_push_datasets - Power BI Push Datasets Mgmt

----

The main class **PushDatasetsMgmt** encapsulates the Power BI REST operations on `Push Datasets <https://docs.microsoft.com/en-us/rest/api/power-bi/pushdatasets>`_
(which allows programmatic access for pushing data into PowerBI) into a few simple methods:

-   ``deploy_dataset`` : Create a pushable dataset (or update the metadata and schema for existing tables) in Power BI Service by a `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file);
-   ``push_tables`` : Push all `ResultSets of a Stored Procedure <https://github.com/DataBooster/DbWebApi/wiki#http-response>`__ - data for multiple tables into a Power BI Push Dataset;
-   ``truncate_tables`` : Removes all rows from specified (or all) tables in a Power BI Push Dataset;

This module also provides two conversion tools for development-time:

-   ``convert_bim_to_push_dataset`` : Convert a `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file) into a Push Dataset Model supported by Power BI Service;
-   ``derive_bim_from_resultsets`` : Generate a `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file) based on `ResultSets of a Stored Procedure (ResultSets) <https://github.com/DataBooster/DbWebApi/wiki#http-response>`__ - data for multiple tables;

For detailed usage, see the practice sample code: https://github.com/DataBooster/PyWebApi/blob/master/Sample/UserApps/PowerBIPusher/db_to_pbi.py

and its product documentation: https://github.com/DataBooster/PyWebApi#powerbi-data-pusher

----

| Homepage and documentation: https://github.com/DataBooster/PyWebApi
| Copyright (c) 2020 Abel Cheng
| License: MIT
"""

import re
from collections import Iterable
from collections.abc import Mapping, MutableMapping
from datetime import datetime, date, time, timedelta
from urllib.parse import urljoin, quote
from simple_rest_call import rest
from json import loads as json_decode


_uuid_pattern = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$")

def is_uuid(name:str) -> bool:
    return True if _uuid_pattern.fullmatch(name) else False


def invoke_powerbi_rest(access_token: str, http_method:str, rest_path:str, request_payload:Mapping=None, organization:str='myorg', api_version:str='v1.0', **kwargs):
    """Executes a REST call to the Power BI service, with the specified URL and body.

    :param access_token: The authentication access token for the Power BI REST call.
    :param http_method: Method for the request: ``GET``, ``POST``, ``DELETE``, ``PUT``, ``PATCH``, ``OPTIONS``.
    :param rest_path: Relative or absolute URL of the Power BI entity you want to access. For example, if you want to access https://api.powerbi.com/v1.0/myorg/groups, then specify 'groups', or pass in the entire URL.
    :param request_payload: Body of the request. This is optional unless the request method is POST, PUT, or PATCH.
    :param organization: (optional) Organization name or tenant GUID to include in the URL. Default is 'myorg'.
    :param api_version: (optional) Version of the API to include in the URL. Default is 'v1.0'. Ignored if ``rest_path`` is an absolute URL.
    :param kwargs: (optional) Please refer to https://requests.readthedocs.io for other optional arguments.
    :return: A JSON decoded object.
    """

    def full_url(relative_url:str, organization:str, api_version:str) -> str:
        if not organization:
            organization = 'myorg'
        if not api_version:
            api_version = 'v1.0'
        return urljoin(f"https://api.powerbi.com/{api_version}/{organization}/", relative_url)

    explicit_headers = kwargs.get('headers', {})
    if isinstance(explicit_headers, str):
        explicit_headers = json_decode(explicit_headers)
    if not isinstance(explicit_headers, Mapping):
        explicit_headers = {}

    headers = {'Pragma': 'no-cache', 'Cache-Control': 'no-cache', 'Authorization': 'Bearer ' + access_token, 'Accept': 'application/json'}
    headers.update(explicit_headers)
    kwargs['headers'] = headers

    return rest(full_url(rest_path, organization, api_version), request_payload, http_method, error_extractor=lambda x: x['error']['message'], **kwargs)


def convert_bim_to_push_dataset(model_bim:Mapping, dataset_name:str, default_mode:str="Push") -> dict:
    """Convert a `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file) into a Push Dataset Model supported by Power BI Service.
All properties not supported by Power BI Push Datasets will be filtered out of the output model.

    :param model_bim: The JSON of the `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file).
    :param dataset_name: The dataset name.
    :param default_mode: The dataset mode or type which allows programmatic access for pushing data into PowerBI. Only 'Push' and 'PushStreaming' are currently supported.
    :return: A Push Dataset Model (request body of https://docs.microsoft.com/en-us/rest/api/power-bi/pushdatasets/datasets_postdatasetingroup) that can be directly used to create a new dataset in Power BI Service.
    """

    def find_tables_dict(model_bim:Mapping) -> Mapping:
        if not isinstance(model_bim, Mapping):
            return None

        if "tables" in model_bim:
            return model_bim

        for value in model_bim.values():
            if isinstance(value, Mapping):
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

    if default_mode:
        dataset_properties["defaultMode"] = default_mode

    clean_up_keys(dataset_properties, "tables", {'columns', 'measures', 'name', 'rows', 'isHidden'})
    clean_up_keys(dataset_properties, "columns", {'dataType', 'name', 'formatString', 'sortByColumn', 'dataCategory', 'isHidden', 'summarizeBy'})
    clean_up_keys(dataset_properties, "measures", {'expression', 'name', 'formatString', 'isHidden'})
    clean_up_keys(dataset_properties, "relationships", {'crossFilteringBehavior', 'fromColumn', 'fromTable', 'name', 'toColumn', 'toTable'})

    return dataset_properties


def derive_bim_from_resultsets(result_sets:list, table_names:list, dataset_name:str) -> dict:
    """Generate a `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file) based on `ResultSets of a Stored Procedure <https://github.com/DataBooster/DbWebApi/wiki#http-response>`__ - data for multiple tables.

    :param result_sets: A list of result sets returned from a stored procedure corresponding to multiple Power BI tables.
    :param table_names: A list of table names corresponding to the result set list.
    :return: The `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file).
    """

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
        if not isinstance(first_row, Mapping):
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
    """This class encapsulates the Power BI REST operations on `Push Datasets <https://docs.microsoft.com/en-us/rest/api/power-bi/pushdatasets>`_
(which allows programmatic access for pushing data into PowerBI) into a few simple methods.

    :param access_token: A valid access token for authenticating subsequent Power BI REST operations.
    """

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
        """Get the group_id according to a specified workspace. If the name of the workspace passed in looks like a UUID, the UUID will be returned directly without querying it from the Power BI Service."""

        if not workspace:
            return None

        if is_uuid(workspace):
            return workspace.lower()

        group_id = self._group_dict.get(workspace)

        if group_id:
            return group_id
        else:
            name_filter = quote("name eq " + repr(workspace))
            resp = invoke_powerbi_rest(self.access_token, 'GET', "groups?$filter=" + name_filter)

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
        """Get the dataset_id according to a dataset name in the specified workspace. If the name of the dataset passed in looks like a UUID, the UUID will be returned directly without querying it from the Power BI Service."""

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

            resp = invoke_powerbi_rest(self.access_token, 'GET', rest_path)

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
        """Get a list of tables within the specified dataset from the specified workspace."""

        dataset_id = self.get_dataset_id(dataset, workspace)
        self._check_name(dataset_id, dataset, 'dataset')

        if workspace:
            group_id = self.get_group_id(workspace)
            rest_path = f"groups/{group_id}/datasets/{dataset_id}/tables"
        else:
            rest_path = f"datasets/{dataset_id}/tables"

        resp = invoke_powerbi_rest(self.access_token, 'GET', rest_path)

        if resp:
            return set(v['name'] for v in resp['value'])
        else:
            return set()


    def _create_dataset(self, dataset_name:str, dataset_properties:Mapping, default_retention_policy, group_id:str=None) -> str:
        if group_id:
            rest_path = f"groups/{group_id}/datasets"
        else:
            rest_path = "datasets"

        if default_retention_policy:
            rest_path += "?defaultRetentionPolicy=" + default_retention_policy

        resp = invoke_powerbi_rest(self.access_token, 'POST', rest_path, dataset_properties)

        return resp['id']

    def _update_table(self, table_bim:Mapping, dataset_id:str, group_id:str=None):
        table_name = quote(table_bim["name"])

        if group_id:
            rest_path = f"groups/{group_id}/datasets/{dataset_id}/tables/{table_name}"
        else:
            rest_path = f"datasets/{dataset_id}/tables/{table_name}"

        resp = invoke_powerbi_rest(self.access_token, 'PUT', rest_path, table_bim)

        return resp["name"]


    def deploy_dataset(self, model_bim:Mapping, dataset_name:str, workspace:str=None, default_mode:str="Push", default_retention_policy:str='basicFIFO') -> str:
        """Create a pushable dataset (or update the metadata and schema for existing tables) in Power BI Service by a `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file).

    :param model_bim: The JSON of the `Tabular Model <https://github.com/otykier/TabularEditor/wiki/Power-BI-Desktop-Integration>`__ (.bim file).
    :param dataset_name: The dataset name.
    :param workspace: (optional) The workspace name.
    :param default_mode: (optional) The dataset mode or type which allows programmatic access for pushing data into PowerBI. Only 'Push' and 'PushStreaming' are currently supported.
    :param default_retention_policy: (optional) The default retention policy. Default is 'basicFIFO'.
    :return: The dataset_id of the dataset.
        """
        dataset_properties = convert_bim_to_push_dataset(model_bim, dataset_name, default_mode)

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
            return self._create_dataset(dataset_name, dataset_properties, default_retention_policy, group_id)


    def push_rows(self, row_list:list, table_name:str, sequence_number:int, dataset_name:str, workspace:str=None):
        if not row_list:
            return

        if not isinstance(row_list, Iterable) or not isinstance(row_list[0], Mapping) or not row_list[0]:
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

        resp = invoke_powerbi_rest(self.access_token, 'POST', rest_path, {"rows": row_list}, headers=headers)


    def push_tables(self, result_sets:list, table_name_seq_list:list, dataset_name:str, workspace:str=None):
        """Push all `ResultSets of a Stored Procedure <https://github.com/DataBooster/DbWebApi/wiki#http-response>`__ - data for multiple tables into a Power BI Push Dataset.

    :param result_sets: The data for multiple tables that will be pushed to a Power BI Push Dataset. It is usually multiple result sets returned by a stored procedure.
    :param table_name_seq_list: A list of tuples corresponding to the list of result sets. 
        The first item in each tuple must specify the table name of the corresponding result set in the Power BI Dataset, 
        and the second item (optional) is used to specify a Sequence Number of the corresponding table 
        if you need to enable the **X-PowerBI-PushData-SequenceNumber** feature - a build-in mechanism to guarantee which rows have been successfully pushed.
    :param dataset_name: The dataset to be pushed data into.
    :param workspace: (optional) The workspace name.
        """

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
        """Removes all rows from specified (or all) tables in a Power BI Push Dataset.

    :param table_names: A list of table names. The data in these specified tables will be truncated. 
        All tables in the specified dataset will be truncated if ``None`` is passed in.
    :param dataset_name: The dataset name.
    :param workspace: (optional) The workspace name.
        """
        if table_names is None:
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
                    invoke_powerbi_rest(self.access_token, 'DELETE', rest_path)
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
                    resp = invoke_powerbi_rest(self.access_token, 'GET', rest_path)
                except Exception as err:
                    agg_error.add(err, table_name)
                else:
                    resp.pop('@odata.context', None)
                    resp.setdefault('name', table)
                    table_seq_list.append(resp)

            agg_error.check()

        return table_seq_list



__version__ = "0.1a5"
