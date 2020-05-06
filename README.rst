########
PyWebApi
########

PyWebApi is a micro-framework for Python RESTfulization. It turns Python(3+) modules/scripts into Web API (RESTful Service) out of the box.

The repository provides:

    1. A library package **pywebapi** (https://pypi.org/project/pywebapi) for making PyWebApi Server.

    2. A sample `PyWebApi Server (for IIS) <https://github.com/DataBooster/PyWebApi/tree/master/Sample/PyWebApi.IIS>`_. It can be easily customized to your own PyWebApi Server.

    3. Some sample user-apps/user-modules:

        + A MDX query transponder (https://github.com/DataBooster/PyWebApi/tree/master/Sample/UserApps/MdxReader)

            i) It forwards a MDX query (received as JSON from the HTTP client) to a specified OLAP, and then convert the query result to the specified model;

            #) (optional) Sends the above results to a database (`DbWebApi <https://github.com/DataBooster/DbWebApi>`_) for storage or further processing;

            #) (optional) Sends a notification about the final result or error.

    4. Some utility PyPI packages:

        + **dbdatareader** (https://pypi.org/project/dbdatareader/) - Data Reader for .NET IDataReader

        + **simple-rest-call** (https://pypi.org/project/simple-rest-call/) - wraps Requests into a simple call

|

----

PyWebApi Server
===============
Just copy any ordinary Python module (and its dependent components) to an organized container (directory) in a PyWebApi Server and it will become a RESTfull service immediately. There is no need to write any code or configuration to become a RESTfull service.

Any authorized HTTP client can invoke module level functions. Input arguments of your function can be passed in request body by JSON (recommended) or in URL query-string.
If the client further wraps a batch of arguments sets into an array as the request JSON, the server will sequentially call the function by each argument set in the array, and wrap all the result objects in a more outer array before return to the client.

The quickest way to build your own PyWebApi Server is to use the source code of the sample server (`PyWebApi for IIS <https://github.com/DataBooster/PyWebApi/tree/master/Sample/PyWebApi.IIS>`_) as a prototype for custom modification and improvement.


Sample PyWebApi Server (for IIS)
--------------------------------

1. **Setup**

    https://github.com/DataBooster/PyWebApi/tree/master/Sample/PyWebApi.IIS contains the complete code of the sample server, 
	which is a  normal Python `Bottle <https://bottlepy.org/>`_ web application. The project file ``PyWebApi.IIS.pyproj`` can be opened by Visual Studio if you like, 
	and recreate the virtual environment from ``requirements.txt``. 

    The following documents are helpful if you are not familiar with setting up a Python web application on IIS:

    - `Configure Python web apps for IIS <https://docs.microsoft.com/en-us/visualstudio/python/configure-web-apps-for-iis-windows>`_
    - `FastCGI \<fastCgi\> <https://docs.microsoft.com/en-us/iis/configuration/system.webserver/fastcgi/>`_
    - `WFastCGI <https://pypi.org/project/wfastcgi/>`_


2. **Configure**


3. **Customize**


	Although this sample server is hosted in IIS as a complete working example, 
	the source code is pure Python and does not depend on any features specific to IIS or Windows platforms.
	It can be easily applied to any platform that supports Python(3+).
