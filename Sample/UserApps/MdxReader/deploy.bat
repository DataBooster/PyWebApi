@Echo off
CD /d "%~dp0"
SET "DESTINATION=..\..\PyWebApi.IIS\user-script-root\utilities\mdxreader"

Robocopy . "%DESTINATION%" /s /purge /xf *.pyproj deploy.bat /xd __pycache__

SETLOCAL EnableDelayedExpansion EnableExtensions
FOR /f "delims=" %%i in ('dir pywintypes??.dll /s /b') DO (
	SET TOKEN=%%i
	IF "!TOKEN:~-4!"==".dll" (
		Copy "!TOKEN!" "!DESTINATION!" /y
	)
)
ENDLOCAL
