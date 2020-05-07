########
PyWebApi
########

PyWebApi is a micro-framework for Python RESTfulization. It turns Python(3+) modules/scripts into Web API (RESTful Service) out of the box.

The repository provides:

#.  A library package **pywebapi** (https://pypi.org/project/pywebapi) for making PyWebApi Server.
#.  A sample `PyWebApi Server (for IIS) <https://github.com/DataBooster/PyWebApi/tree/master/Sample/PyWebApi.IIS>`_. It can be easily customized to your own PyWebApi Server.
#.  Some sample user-apps/user-modules:

    *   A MDX query transponder (https://github.com/DataBooster/PyWebApi/tree/master/Sample/UserApps/MdxReader)

        i)  It forwards a MDX query (received as JSON from the HTTP client) to a specified OLAP, and then convert the query result to the specified model;
        #)  (optional) Sends the above results to a database (`DbWebApi <https://github.com/DataBooster/DbWebApi>`_) for storage or further processing;
        #)  (optional) Sends a notification about the final result or error.

#.  Some utility PyPI packages:

    +   **dbdatareader** (https://pypi.org/project/dbdatareader/) - Data Reader for .NET IDataReader
    +   **simple-rest-call** (https://pypi.org/project/simple-rest-call/) - wraps Requests into a simple call

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

#.  **Setup**

    https://github.com/DataBooster/PyWebApi/tree/master/Sample/PyWebApi.IIS contains the complete code of the sample server, which is a  normal Python `Bottle <https://bottlepy.org/>`_ web application. The project file ``PyWebApi.IIS.pyproj`` can be opened by Visual Studio if you like, and recreate the virtual environment from ``requirements.txt``. 

    The following documents are helpful if you are not familiar with setting up a Python web application on IIS:

    -   `Configure Python web apps for IIS <https://docs.microsoft.com/en-us/visualstudio/python/configure-web-apps-for-iis-windows>`_
    -   `FastCGI \<fastCgi\> <https://docs.microsoft.com/en-us/iis/configuration/system.webserver/fastcgi/>`_
    -   `WFastCGI <https://pypi.org/project/wfastcgi/>`_

    Some Considerations:

    -   Where to install the PyWebApi Server?
    -   Physical directory in the file system? (for the website and for user scripts)
    -   Virtual/Application directory in the IIS system?
    -   Which identity (service account) will be used for the application pool?
    -   Permissions to the correct account

    ``Anonymous Authentication`` (to allow `CORS <https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS>`__ `Preflight <https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request>`__) and ``Windows Authentication`` need to be **Enabled** in IIS level. After handling CORS, anonymous authentication will be blocked in web application level.

    |

    **Configure** - ``web.config``:

    -   `Enabling wfastcgi <https://github.com/microsoft/PTVS/tree/master/Python/Product/WFastCgi#enabling-wfastcgi>`__ is one of the crucial step above if we are using `WFastCGI <https://github.com/microsoft/PTVS/tree/master/Python/Product/WFastCgi>`__ as the `route handler <https://github.com/microsoft/PTVS/tree/master/Python/Product/WFastCgi#route-handlers>`__ .

        .. code:: shell
        
            wfastcgi-enable
    
        The output of wfastcgi-enable will be used to replace below value of scriptProcessor:
    
        .. code:: xml
        
          <system.webServer>
            <handlers>
              <add name="PythonHandler" path="*" verb="*" modules="FastCgiModule"
                   scriptProcessor="D:\wwwroot\PyWebApi\env\Scripts\python.exe|D:\wwwroot\PyWebApi\env\Lib\site-packages\wfastcgi.py"
                   resourceType="Unspecified" requireAccess="Script"/>
            </handlers>
          </system.webServer>

    -   Modify the ``SCRIPT_NAME`` entry in the <appSettings> section to the Virtual/Application directory (ApplicationPath) you installed in IIS, do NOT put a slash ``/`` at the end of the path here. However, if the service is installed on the root of a website, this entry can be removed.

        .. code:: xml

          <appSettings>
            <add key="WSGI_HANDLER" value="app.wsgi_app()"/>
            <add key="WSGI_LOG" value="D:\wwwroot\PyWebApi\log\wfastcgi.log"/>
            <add key="SCRIPT_NAME" value="/PyWebApi"/>
            <add key="USER_SCRIPT_ROOT" value=".\user-script-root\"/>
            <add key="SERVER_DEBUG" value="IIS"/>
          </appSettings>

    -   Modify the value of the ``USER_SCRIPT_ROOT`` entry to the container location where all user modules will be organized, 
        it is a local file system path which can be an absolute path, or a relative path - relative to the root of the web application 
        (where this ``web.config`` file is located).

    -   ``WSGI_LOG`` is an optional entry for WFastCGI to write its logging information to a file. This entry should be removed from the production.
        (After the web app is setup properly, this log does not capture many application-level errors.)


    **Troubleshooting**:

    - 



#. **Customize**


    Although this sample server is hosted in IIS as a complete working example, 
    the source code is pure Python and does not depend on any features specific to IIS or Windows platforms.
    It can be easily applied to any platform that supports Python(3+).
