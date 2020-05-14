########
PyWebApi
########

PyWebApi is a micro-framework for Python RESTfulization. It turns Python(3+) modules/scripts into Web API (RESTful Service) out of the box.

The repository provides:

#.  A library package **pywebapi** (https://pypi.org/project/pywebapi) for making PyWebApi Server.
#.  A sample `PyWebApi Server (for IIS) <https://github.com/DataBooster/PyWebApi/tree/master/Sample/PyWebApi.IIS>`_. It can be easily customized to your own PyWebApi Server.
#.  Some sample `user-apps/user-modules/user-scripts <Sample User Apps/Modules/Scripts:_>`__.
#.  Some utility PyPI packages:

    +   **dbdatareader** (https://pypi.org/project/dbdatareader/) - Data Reader for .NET `IDataReader <https://docs.microsoft.com/en-us/dotnet/api/system.data.idatareader>`_
    +   **simple-rest-call** (https://pypi.org/project/simple-rest-call/) - wraps `Requests <https://requests.readthedocs.io/>`__ into a simple call

|

----

PyWebApi Server
===============
Just copy any ordinary Python module (and its dependent components) to an organized container (directory) in a PyWebApi Server and it will become a RESTfull service immediately. 
There is no need to write any code or configuration to become a RESTfull service.

Any authorized HTTP client can invoke module level functions. Input arguments of your function can be passed in request body by JSON (recommended) or in URL query-string. 
If the client further wraps a batch of arguments sets into an array as the request JSON, the server will sequentially call the function by each argument set in the array, 
and wrap all the result objects in a more outer array before return to the client.

.. image:: docs/overview.png

The quickest way to build your own PyWebApi Server is to use the source code of the sample server (`PyWebApi for IIS <https://github.com/DataBooster/PyWebApi/tree/master/Sample/PyWebApi.IIS>`_) 
as a prototype for custom modification and improvement.


Sample PyWebApi Server (for IIS)
--------------------------------

#.  **Setup**

    https://github.com/DataBooster/PyWebApi/tree/master/Sample/PyWebApi.IIS contains the complete code of the sample server, which is a  normal Python `Bottle <https://bottlepy.org/>`_ 
    web application. The project file ``PyWebApi.IIS.pyproj`` can be opened by Visual Studio if you like, and recreate the virtual environment from ``requirements.txt``. 

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

    ``Anonymous Authentication`` (to allow `CORS <https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS>`__ `Preflight <https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request>`__) 
    and ``Windows Authentication`` need to be Enabled in IIS level. After handling CORS, anonymous authentication will be blocked in web application level.

    |

    **Configure**: -- ``web.config``

    -   `Enabling wfastcgi <https://github.com/microsoft/PTVS/tree/master/Python/Product/WFastCgi#enabling-wfastcgi>`__ is one of the crucial step above if we are using 
        `WFastCGI <https://github.com/microsoft/PTVS/tree/master/Python/Product/WFastCgi>`__ as the `route handler <https://github.com/microsoft/PTVS/tree/master/Python/Product/WFastCgi#route-handlers>`__ .

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

        .. _script-name:
    -   Modify the ``SCRIPT_NAME`` entry in the <appSettings> section to the Virtual/Application directory (ApplicationPath) you installed in IIS, 
        do NOT put a slash ``/`` at the end of the path here. However, if the web app is installed on the root of a website, this entry can be removed.

        .. code:: xml

          <appSettings>
            <add key="WSGI_HANDLER" value="app.wsgi_app()"/>
            <add key="WSGI_LOG" value="D:\wwwroot\PyWebApi\log\wfastcgi.log"/>
            <add key="SCRIPT_NAME" value="/PyWebApi"/>
            <add key="USER_SCRIPT_ROOT" value=".\user-script-root\"/>
            <add key="SERVER_DEBUG" value="IIS"/>
          </appSettings>

        .. _user-script-root:
    -   Modify the value of the ``USER_SCRIPT_ROOT`` entry to the container location where all user modules will be organized, 
        it is a local file system path which can be an absolute path, or a relative path - relative to the root of the web application 
        (where this ``web.config`` file is located).

    -   ``WSGI_LOG`` is an optional entry for WFastCGI to write its logging information to a file. This entry should be removed from production.
        (After the web app is setup properly, this log does not capture many application-level errors.)


    **Troubleshoot**:

    -   ``whoami`` can be used to verify that the server has been setup properly or not. - E.g. ``http://ourteam.company.com/PyWebApi/whoami``. 
        The actual URL depends on where you install it, and its URL routing is defined in `route.py <https://github.com/DataBooster/PyWebApi/blob/master/Sample/PyWebApi.IIS/routes.py>`_ -- 
        ``@route(path='/whoami', ...)``. It should return your Windows username if you are currently logged in with a domain account.

    -   If the initial setup is not smooth, many causes are often related to lack of permissions. Check Windows Event Viewer for more clues.


#.  **Customize**

    a.  Authentication

        Since this sample is hosted on IIS, it simply receives the authentication result passed by IIS.
        If you need other authentication methods not provided by IIS, you should find the corresponding authentication plug-in 
        (for `Bottle <https://bottlepy.org/docs/dev/tutorial.html#plugins>`__) or implement it yourself.

    #.  Authorization

        Most companies have their own enterprise-level authorization services. The placeholder function ``check_permission(...)`` in 
        `route.py <https://github.com/DataBooster/PyWebApi/blob/master/Sample/PyWebApi.IIS/routes.py>`_ provides a junction box to 
        integrate with your authorization service.

        .. code-block:: python

            def check_permission(app_id:str, user_id:str, module_func:str) -> bool:
                #TODO: add your implementation of permission checks
                return True

        Arguments:

        - **app_id**: This is the app category indicated in the requesting URL - matched by the ``<app_id>`` wildcard in ``@route(path='/pys/<app_id>/<module_func:path>', ...)``. If your enterprise's authorization implementation does not require this concept, this parameter and the corresponding ``<app_id>`` wildcard in the URL route should be removed together.

        - **user_id**: This is the client user identity passed by IIS authentication.
        - **module_func**: This is the `USER_SCRIPT_ROOT <user-script-root_>`_ relative logical path to the current request ``module.function``, it is the matching ``<module_func:path>`` (in ``@route(path='/pys/<app_id>/<module_func:path>', ...)``) from the request URL.

        **Return**: According to the above conditions, 

        - ``True`` should be returned if you want to allow the requesting module-level function to be executed;
        - ``False`` should be returned if you want to reject the request.


    #.  Logging

        There are many efficient logging packages, and you can find logging plugins for Bottle directly from `PyPi <https://pypi.org/>`_, 
        or implement one yourself.

    #.  Migration

        Although this sample server is hosted on IIS as a complete working example, 
        the source code is pure Python and does not depend on any features specific to IIS or Windows platforms.
        It can be easily applied to any platform that supports Python(3+).

Deploy User Modules/Scripts:
----------------------------

#.  **Copy to Server**

    Deploying user modules/scripts is a simple copying.
    Copy the user module and its dependent files to a planned path directory under `USER_SCRIPT_ROOT <user-script-root_>`_ in the server.
    This path (relative to `USER_SCRIPT_ROOT <user-script-root_>`_) determines what URL path the client should use to call the functions.

        For example, if we copy the module mdx_task (``mdx_task.py`` and all dependent files) to the relative path ``utilities\mdxreader\`` (in Windows) or ``utilities/mdxreader/`` (in UNIX) under `USER_SCRIPT_ROOT <user-script-root_>`_,
        then the client should use ``http://ourteam.company.com/PyWebApi/pys/etl/utilities/mdxreader/mdx_task.run_query`` to invoke the ``run_query`` function of the ``mdx_task`` module.

        Breakdown:

        -   ``/PyWebApi`` -- the virtual/application directory (ApplicationPath) installed in IIS, and it's also the value of the appSettings item `SCRIPT_NAME <script-name_>`_ in ``web.config``;
        -   ``/pys/`` -- the static segment in ``@route(path='/pys/<app_id>/<module_func:path>', ...)``;
        -   ``etl`` -- matched by the ``<app_id>`` wildcard;
        -   ``utilities/mdxreader/`` -- the relative path where the user module is located;
        -   ``mdx_task`` -- the user module (``mdx_task.py``);
        -   ``run_query`` -- the module-level function to be invoked;

    **.pth file**

    If some dependent library packages are not copied into the same directory as the user main entry module, 
    and you do not want to install them in the global virtual environment of the website. 
    Then you need to put a ``.pth`` file (E.g. ``pywebapi.pth``) in the directory of the user main entry module, 
    so that the Python runtime knows where to find those dependent library packages.

    The ``.pth`` file only takes effect within the scope of the user entry module in the same directory.
    Its contents are additional paths (one per line) to be added to Python’s search path.
    Each line in the file should be a relative path, relative to the directory where the ``.pth`` file is located.
    Non-existing paths, blank lines and lines beginning with # are skipped. 

    Example `pywebapi.pth <https://github.com/DataBooster/PyWebApi/blob/master/Sample/UserApps/MdxReader/pywebapi.pth>`_:

    ::

        env\Lib\site-packages
        env\Lib\site-packages\win32
        env\Lib\site-packages\win32\lib
        
        #copy pywintypes??.dll from env\Lib\site-packages\pywin32_system32 to env\Lib\site-packages\win32\lib


#.  **Grant Permissions**

    All client users (or group account) who will invoke the user-module-function, need to be granted permissions in your authorization system.

    Take the above URL as an example, 

    .. code-block:: JSON

        {
            "app_id": "etl",
            "action": "utilities/mdxreader/mdx_task.run_query",
            "account": "user id/name or group account/role"
        }

    These elements can be essential stuff for an authorization entry.

|

----

|

Sample User Apps/Modules/Scripts:
---------------------------------

*   `MdxReader <https://github.com/DataBooster/PyWebApi/tree/master/Sample/UserApps/MdxReader>`_

    This sample user app is a practical Python app that acts as an MDX query dispatcher:

    1.  It forwards an MDX query (received as JSON from the HTTP client) to a specified OLAP, and then convert the query result to the specified model;
    #.  (optional) Sends the above results to a database (`DbWebApi <https://github.com/DataBooster/DbWebApi>`_) for storage or further processing;
    #.  (optional) Sends a notification about the final result or error.
