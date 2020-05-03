########
PyWebApi
########

PyWebApi is a micro-framework for Python RESTfulization. It turns Python(3+) module/script into Web API (RESTful Service) out of the box.

The repository provides:

    1. A library package **pywebapi** (https://pypi.org/project/pywebapi) for making PyWebApi Server.

    2. A sample server **PyWebApi for IIS** (https://github.com/DataBooster/PyWebApi/tree/master/Sample/PyWebApi.IIS). It can be easily customized to your own PyWebApi server..

    3. Some sample user-apps/user-modules:

        + A MDX query transponder (https://github.com/DataBooster/PyWebApi/tree/master/Sample/UserApps/MdxReader)

            i) Forward the MDX query (received as JSON from the HTTP client) to the specified OLAP, and then convert the query result to the specified model

            #) (optional) Send the above results to a database (`DbWebApi <https://github.com/DataBooster/DbWebApi>`_) for storage or further processing;

            #) (optional) Send a notification about the final result or error.

    4. Some utilities (PyPI packages):

        + **dbdatareader** (https://pypi.org/project/dbdatareader/) - Data Reader for .NET IDataReader

        + **simple-rest-call** (https://pypi.org/project/simple-rest-call/) - wraps Requests into a simple call


PyWebApi Server
===============
Just copy any ordinary Python module (and its dependent components) to an organized container (directory) on a PyWebApi Server and it will become a RESTfull service immediately. There is no need to write any code or configuration to become a RESTfull service.

    With PyWebApi, any http client can invoke module level function in a managed way.
    Input arguments of your function can be supplied in request body by JSON (recommended) or in URL query-string,
    If the client further wraps a batch of arguments sets into an array as the request JSON,
    the server will sequentially call the function by each argument set in the array,
    and wrap all the result objects in a more outer array before return to the client.
