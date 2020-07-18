@Echo off
CD /d "%~dp0"
IF "%~1"=="" (
	SET "DESTINATION=..\..\PyWebApi.IIS\user-script-root\utilities\mdx_etl"
) ELSE (
	SET "DESTINATION=%~1"
)

RoboCopy . "%DESTINATION%" /s /purge /xf *.pyproj *.sql *.pck deploy.bat /xd __pycache__

SETLOCAL EnableDelayedExpansion EnableExtensions
FOR /f "delims=" %%i in ('dir pywintypes??.dll /s /b') DO (
	SET SOURCE=%%i
	IF "!SOURCE:~-4!"==".dll" (
		Copy "!SOURCE!" "!DESTINATION!" /y
	)
)
ENDLOCAL
