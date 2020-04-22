@Echo off
CD /d "%~dp0"
SET "THIS_SCRIPT_PATH=%~dp0..\env\Scripts\"
SET EXISTS_IN_PATH=0
FOR /F "delims=" %%i IN ('PATH ^| Find /C /I "%THIS_SCRIPT_PATH%"') DO SET EXISTS_IN_PATH=%%i 2>NUL
If %EXISTS_IN_PATH%==0 SET "PATH=%THIS_SCRIPT_PATH%;%PATH%"

If Exist build\lib Del /q build\lib\*
If Exist dist Del /q dist\*

Python.exe setup.py bdist_wheel --universal
